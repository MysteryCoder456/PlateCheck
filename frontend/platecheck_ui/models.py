"""The data shape shared by the UI and a future model adapter."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Nutrients:
    kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float


@dataclass(frozen=True)
class FoodItem:
    name: str
    grams: float
    per_gram: Nutrients

