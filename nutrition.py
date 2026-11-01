"""Nutrition facts, Nutri-Score health grade and healthier swaps for the 101 recognised foods.

Nutrition per 100 g comes from data/foods.csv (USDA FNDDS, built by scripts/build_nutrition.py).
The grade follows the Nutri-Score 2017 algorithm for general foods (Santé publique France):
negative points for energy, sugars, saturated fat and sodium; positive points for
fruit/vegetables/legumes, fibre and protein.
"""
import csv
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

FOODS_CSV = Path(__file__).resolve().parent / "data" / "foods.csv"

# Points thresholds: one point for every threshold the value is above.
ENERGY_KJ = [335, 670, 1005, 1340, 1675, 2010, 2345, 2680, 3015, 3350]
SUGARS_G = [4.5, 9, 13.5, 18, 22.5, 27, 31, 36, 40, 45]
SAT_FAT_G = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
SODIUM_MG = [90, 180, 270, 360, 450, 540, 630, 720, 810, 900]
FIBER_G = [0.9, 1.9, 2.8, 3.7, 4.7]
PROTEIN_G = [1.6, 3.2, 4.8, 6.4, 8.0]

GRADE_COLORS = {"A": "#038141", "B": "#85bb2f", "C": "#fecb02", "D": "#ee8100", "E": "#e63e11"}
GRADE_MEANING = {
    "A": "Very healthy choice",
    "B": "Healthy choice",
    "C": "Fine in moderation",
    "D": "Eat occasionally",
    "E": "Treat food: keep it rare",
}

# Daily reference values (US FDA, 2,000 kcal diet). Sugars uses the added-sugars limit as a guide.
DAILY_VALUES = {"kcal": 2000, "fat_g": 78, "sat_fat_g": 20, "carbs_g": 275, "sugars_g": 50,
                "fiber_g": 28, "protein_g": 50, "sodium_mg": 2300}
NUTRIENT_NAMES = {"kcal": "Energy", "protein_g": "Protein", "carbs_g": "Carbohydrates", "fat_g": "Fat",
                  "sat_fat_g": "Saturated fat", "sugars_g": "Sugars", "fiber_g": "Fibre", "sodium_mg": "Sodium"}


def _points(value, thresholds):
    return sum(value > t for t in thresholds)


def _fruit_veg_points(percent):
    if percent > 80:
        return 5
    if percent > 60:
        return 2
    if percent > 40:
        return 1
    return 0


@dataclass(frozen=True)
class HealthScore:
    score: int
    grade: str
    negative: dict
    positive: dict

    @property
    def color(self):
        return GRADE_COLORS[self.grade]

    @property
    def meaning(self):
        return GRADE_MEANING[self.grade]

    def reasons(self):
        """Short plain-language reasons behind the grade, worst first."""
        labels = {"energy": "calories", "sugars": "sugar", "sat_fat": "saturated fat", "sodium": "salt"}
        bad = [f"high in {labels[k]}" for k, v in sorted(self.negative.items(), key=lambda kv: -kv[1]) if v >= 5]
        some = [f"some {labels[k]}" for k, v in self.negative.items() if 3 <= v < 5]
        good_labels = {"fruit_veg": "rich in fruit/vegetables", "fiber": "good fibre", "protein": "good protein"}
        maxima = {"fruit_veg": 5, "fiber": 5, "protein": 5}
        good = [good_labels[k] for k, v in self.positive.items() if v >= maxima[k] - 1]
        return bad + some + good or ["balanced: no nutrient is especially high or low"]


def nutri_score(per_100g, fruit_veg_pct):
    """Nutri-Score (2017, general foods) from per-100 g values."""
    negative = {
        "energy": _points(per_100g["kcal"] * 4.184, ENERGY_KJ),
        "sugars": _points(per_100g["sugars_g"], SUGARS_G),
        "sat_fat": _points(per_100g["sat_fat_g"], SAT_FAT_G),
        "sodium": _points(per_100g["sodium_mg"], SODIUM_MG),
    }
    positive = {
        "fruit_veg": _fruit_veg_points(fruit_veg_pct),
        "fiber": _points(per_100g["fiber_g"], FIBER_G),
        "protein": _points(per_100g["protein_g"], PROTEIN_G),
    }
    total_negative = sum(negative.values())
    if total_negative >= 11 and positive["fruit_veg"] < 5:
        score = total_negative - positive["fruit_veg"] - positive["fiber"]  # protein does not count
    else:
        score = total_negative - sum(positive.values())
    if score <= -1:
        grade = "A"
    elif score <= 2:
        grade = "B"
    elif score <= 10:
        grade = "C"
    elif score <= 18:
        grade = "D"
    else:
        grade = "E"
    return HealthScore(score, grade, negative, positive)


@dataclass(frozen=True)
class Food:
    label: str
    name: str
    category: str
    per_100g: dict
    fruit_veg_pct: float
    usda_source: str

    @property
    def health(self):
        return nutri_score(self.per_100g, self.fruit_veg_pct)

    def serving(self, grams):
        factor = grams / 100
        return {key: value * factor for key, value in self.per_100g.items()}

    def daily_percent(self, grams):
        portion = self.serving(grams)
        return {key: 100 * portion[key] / DAILY_VALUES[key] for key in DAILY_VALUES}


@lru_cache(maxsize=1)
def all_foods():
    foods = {}
    with open(FOODS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            per_100g = {key: float(row[key]) for key in DAILY_VALUES}
            foods[row["label"]] = Food(row["label"], row["name"], row["category"], per_100g,
                                       float(row["fruit_veg_pct"]), row["usda_source"])
    return foods


def get_food(label):
    return all_foods().get(label.strip().lower().replace(" ", "_"))


SWAP_GROUPS = {  # where to look for healthier options for each category
    "main": ["main", "seafood", "salad"],
    "sandwich": ["sandwich", "main", "salad"],
    "snack": ["snack", "salad"],
    "dessert": ["dessert", "snack"],
    "breakfast": ["breakfast", "snack"],
    "soup": ["soup", "salad"],
    "seafood": ["seafood", "salad"],
    "salad": ["salad", "seafood"],
}


def healthier_swaps(food, limit=3):
    """Foods from similar meal types with a better grade, best first."""
    current = food.health.score
    options = [other for other in all_foods().values()
               if other.label != food.label and other.category in SWAP_GROUPS[food.category]
               and other.health.score < current and other.health.grade < food.health.grade]
    options.sort(key=lambda other: (other.health.score, other.per_100g["kcal"]))
    return options[:limit]
