import random

from fastapi import FastAPI
from pydantic import Base64Bytes, BaseModel

app = FastAPI()


class NutritionItem(BaseModel):
    """
    Represents a single nutrition item.
    Contains the item's name and macronutrient quantities in grams.
    """

    name: str
    quantity: float
    protein: float
    carbs: float
    fat: float


class CalculateRequest(BaseModel):
    """
    Represents a request to calculate the macros of food in an image.
    Image must be a base64-encoded PNG image.
    """

    image: Base64Bytes


class CalculateResponse(BaseModel):
    """
    Represents the response to a macro calculation request.
    Contains a list of items along with their macronutrients.
    """

    items: list[NutritionItem]


# Illustrative sample values, not model predictions. All quantities are in grams,
# and macros are totals for the item's quantity.
PREVIEW_ITEMS = [
    NutritionItem(name="Grilled chicken", quantity=120, protein=37.2, carbs=0, fat=4.3),
    NutritionItem(name="White rice", quantity=160, protein=4.3, carbs=45.1, fat=0.5),
    NutritionItem(name="Broccoli", quantity=80, protein=1.9, carbs=5.8, fat=0.3),
    NutritionItem(name="Avocado", quantity=50, protein=1.0, carbs=4.3, fat=7.4),
    NutritionItem(name="Egg", quantity=50, protein=6.5, carbs=0.6, fat=5.5),
]


@app.get("/")
async def root():
    return "Hello, PlateCheck"


@app.post("/calculate")
async def calculate(_request: CalculateRequest) -> CalculateResponse:
    num = random.randrange(len(PREVIEW_ITEMS))
    items = random.sample(PREVIEW_ITEMS, k=num)
    return CalculateResponse(items=items)
