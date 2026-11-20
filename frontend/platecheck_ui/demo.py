"""Clearly labeled sample values for UI development only."""

from .models import FoodItem, Nutrients


# These are illustrative values, not USDA data or neural-network predictions.
DEMO_FOODS = {
    "Grilled chicken": Nutrients(1.65, .31, 0, .036),
    "White rice": Nutrients(1.30, .027, .282, .003),
    "Broccoli": Nutrients(.35, .024, .072, .004),
    "Avocado": Nutrients(1.60, .02, .085, .147),
    "Egg": Nutrients(1.55, .13, .011, .11),
}


def starting_items() -> list[FoodItem]:
    return [
        FoodItem("Grilled chicken", 120, DEMO_FOODS["Grilled chicken"]),
        FoodItem("White rice", 160, DEMO_FOODS["White rice"]),
        FoodItem("Broccoli", 80, DEMO_FOODS["Broccoli"]),
    ]
