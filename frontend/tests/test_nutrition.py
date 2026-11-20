"""Checks that editing item mass changes displayed totals consistently."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from platecheck_ui.models import FoodItem, Nutrients
from platecheck_ui.nutrition import meal_nutrients


class NutritionTests(unittest.TestCase):
    def test_totals_scale_with_edited_mass(self):
        per_gram = Nutrients(2.0, 0.2, 0.1, 0.05)
        meal = [FoodItem("example", 100, per_gram)]
        first = meal_nutrients(meal)
        edited = meal_nutrients([FoodItem("example", 150, per_gram)])
        self.assertEqual(first.kcal, 200)
        self.assertEqual(edited.kcal, 300)
        self.assertEqual(edited.protein_g, 30)

    def test_empty_meal_and_negative_mass(self):
        self.assertEqual(meal_nutrients([]).kcal, 0)
        with self.assertRaises(ValueError):
            meal_nutrients([FoodItem("invalid", -1, Nutrients(1, 1, 1, 1))])


if __name__ == "__main__":
    unittest.main()
