"""C1: frozen FoodSeg103 segmenter (owner: P3).

Takes a top-down meal photo and returns a per-pixel FoodSeg103 label map plus the
fraction of the food area each label covers. C3 uses those fractions to split the
total mass from C2 across items (grams_i = total_mass * area_i).

The weights are a Mask2Former (Swin-T) checkpoint trained on FoodSeg103's 104 classes
(background + 103 foods). They are used frozen; nothing here trains them.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from transformers import Mask2FormerForUniversalSegmentation, Mask2FormerImageProcessor

# Hugging Face location of the checkpoint, pinned to an exact commit so every
# teammate (and Colab) loads the same weights.
HF_REPO_ID = "mericberktas/foodseg-models"
HF_REVISION = "7d47191a61720eb5a36ec4ad044a0cbc1c43cf94"
HF_SUBFOLDER = "foodseg103/mask2former"

INPUT_SIZE = 512  # the proposal's C1 input: 3 x 512 x 512
BACKGROUND = 0

FOODSEG103_LABELS: list[str] = json.loads(
    resources.files("plate_check").joinpath("foodseg103_labels.json").read_text(encoding="utf-8")
)

# The checkpoint's output index k means FoodSeg103 class CHECKPOINT_TO_FOODSEG[k].
#
# Its config only says LABEL_0..LABEL_103, and its food indices are rotated: FoodSeg103
# class g comes out as index (g + 13) mod 104, with background kept at 0. We found this
# on FoodSeg103 validation images (first 106 to spot it, the other 106 to check it):
# held-out pixel accuracy 0.52 -> 0.76, food-class mIoU 0.001 -> 0.29.
# Side effect of the rotation: class 91 ("cabbage") lands on index 0, so this checkpoint
# cannot tell cabbage from background.
_N = len(FOODSEG103_LABELS)
CHECKPOINT_TO_FOODSEG: np.ndarray = (np.arange(_N) - 13) % _N
CHECKPOINT_TO_FOODSEG[0] = BACKGROUND


@dataclass
class SegmentationResult:
    """Output of C1 for one photo."""

    mask: np.ndarray  # H x W, FoodSeg103 class id per pixel (0 = background)
    pixel_counts: dict[str, int] = field(default_factory=dict)  # food labels only
    area_fractions: dict[str, float] = field(default_factory=dict)  # sums to 1 over food

    @property
    def food_pixels(self) -> int:
        return int(sum(self.pixel_counts.values()))

    def items(self) -> list[tuple[str, float]]:
        """Food labels sorted by area, largest first."""
        return sorted(self.area_fractions.items(), key=lambda kv: -kv[1])


def download_weights(local_dir: str | Path) -> Path:
    """Fetch the pinned checkpoint (config.json + model.safetensors, ~190 MB)."""
    from huggingface_hub import hf_hub_download

    local_dir = Path(local_dir)
    for name in ("config.json", "model.safetensors"):
        hf_hub_download(
            HF_REPO_ID,
            f"{HF_SUBFOLDER}/{name}",
            revision=HF_REVISION,
            local_dir=local_dir,
        )
    return local_dir / HF_SUBFOLDER


class FoodSegmenter:
    """Frozen FoodSeg103 segmenter.

    >>> seg = FoodSegmenter("models/foodseg103_mask2former")
    >>> result = seg.segment(Image.open("rgb.png"))
    >>> result.items()[:3]
    """

    def __init__(
        self,
        model_dir: str | Path,
        device: str | None = None,
        min_fraction: float = 0.01,
        drop_edge_food: bool = True,
    ) -> None:
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = Mask2FormerForUniversalSegmentation.from_pretrained(model_dir).to(self.device).eval()
        for p in self.model.parameters():
            p.requires_grad_(False)
        self.processor = Mask2FormerImageProcessor(
            size={"height": INPUT_SIZE, "width": INPUT_SIZE},
            do_reduce_labels=False,
            ignore_index=255,
        )
        # Labels covering less than this share of the food area are dropped as noise
        # and their pixels folded into the largest neighbouring label set (see _clean).
        self.min_fraction = min_fraction
        # Nutrition5k overhead shots often show part of a neighbouring plate at the
        # frame edge. Food blobs that touch the border (other than the largest blob)
        # are treated as someone else's plate and set to background.
        self.drop_edge_food = drop_edge_food

    @torch.no_grad()
    def predict_mask(self, image: Image.Image) -> np.ndarray:
        """Per-pixel FoodSeg103 class ids at the photo's original resolution."""
        image = image.convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        outputs = self.model(**inputs)
        raw = self.processor.post_process_semantic_segmentation(
            outputs, target_sizes=[(image.height, image.width)]
        )[0]
        return CHECKPOINT_TO_FOODSEG[raw.cpu().numpy()]

    def segment(self, image: Image.Image) -> SegmentationResult:
        mask = self._clean(self.predict_mask(image))
        counts = np.bincount(mask.ravel(), minlength=len(FOODSEG103_LABELS))
        food_total = counts[1:].sum()
        pixel_counts = {FOODSEG103_LABELS[c]: int(counts[c]) for c in np.nonzero(counts)[0] if c != BACKGROUND}
        fractions = {name: float(n / food_total) for name, n in pixel_counts.items()} if food_total else {}
        return SegmentationResult(mask=mask, pixel_counts=pixel_counts, area_fractions=fractions)

    def _clean(self, mask: np.ndarray) -> np.ndarray:
        """1) optionally remove edge blobs from neighbouring plates; 2) drop labels below
        min_fraction of the food area by reassigning them to the biggest food label, so
        tiny speckles don't become separate items for C3."""
        if self.drop_edge_food:
            mask = _drop_edge_blobs(mask)
        counts = np.bincount(mask.ravel(), minlength=len(FOODSEG103_LABELS))
        food = counts.copy()
        food[BACKGROUND] = 0
        total = food.sum()
        if total == 0:
            return mask
        small = np.nonzero((food > 0) & (food < self.min_fraction * total))[0]
        if len(small) == 0:
            return mask
        biggest = int(food.argmax())
        out = mask.copy()
        out[np.isin(out, small)] = biggest
        return out


def _drop_edge_blobs(mask: np.ndarray) -> np.ndarray:
    """Set food blobs touching the image border to background, except the largest blob."""
    from scipy import ndimage

    blobs, n = ndimage.label(mask != BACKGROUND)
    if n <= 1:
        return mask
    sizes = np.bincount(blobs.ravel())
    sizes[0] = 0
    keep = int(sizes.argmax())
    border = np.unique(np.concatenate([blobs[0], blobs[-1], blobs[:, 0], blobs[:, -1]]))
    drop = [b for b in border if b not in (0, keep)]
    if not drop:
        return mask
    out = mask.copy()
    out[np.isin(blobs, drop)] = BACKGROUND
    return out


# ---------------------------------------------------------------- visualisation

def _palette(n: int = len(FOODSEG103_LABELS), seed: int = 539) -> np.ndarray:
    rng = np.random.default_rng(seed)
    pal = rng.integers(40, 256, size=(n, 3), dtype=np.uint8)
    pal[BACKGROUND] = 0
    return pal


PALETTE = _palette()


def colorize(mask: np.ndarray) -> Image.Image:
    return Image.fromarray(PALETTE[mask])


def overlay(image: Image.Image, mask: np.ndarray, alpha: float = 0.55) -> Image.Image:
    base = np.asarray(image.convert("RGB"), dtype=np.float32)
    color = PALETTE[mask].astype(np.float32)
    food = (mask != BACKGROUND)[..., None]
    blended = np.where(food, (1 - alpha) * base + alpha * color, base)
    return Image.fromarray(blended.astype(np.uint8))
