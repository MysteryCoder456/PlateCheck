from fastapi import FastAPI
from pydantic import Base64Bytes, BaseModel

app = FastAPI()


class NutritionItem(BaseModel):
    """
    Represents a single nutrition item.
    Contains the item's name and macronutrient quantities.
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


@app.get("/")
async def root():
    return "Hello, PlateCheck"


@app.post("/calculate")
async def calculate(_request: CalculateRequest) -> CalculateResponse:
    raise NotImplementedError
