"""Deterministic UI calculations, independent of Streamlit or the models."""

from .models import FoodItem, Nutrients


def item_nutrients(item: FoodItem) -> Nutrients:
    if item.grams < 0:
        raise ValueError("Food mass cannot be negative")
    return Nutrients(
        kcal=item.per_gram.kcal * item.grams,
        protein_g=item.per_gram.protein_g * item.grams,
        carbs_g=item.per_gram.carbs_g * item.grams,
        fat_g=item.per_gram.fat_g * item.grams,
    )


def meal_nutrients(items: list[FoodItem]) -> Nutrients:
    values = [item_nutrients(item) for item in items]
    return Nutrients(
        kcal=sum(value.kcal for value in values),
        protein_g=sum(value.protein_g for value in values),
        carbs_g=sum(value.carbs_g for value in values),
        fat_g=sum(value.fat_g for value in values),
    )
