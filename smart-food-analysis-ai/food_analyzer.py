from functools import lru_cache
from transformers import pipeline

MODEL_NAME = "nateraw/food"

# Illustrative values per 100 g for demonstration only.
# They are not a verified nutrition database and may not match the uploaded meal.
NUTRITION_PER_100G = {
    "pizza": {"calories": 266, "protein_g": 11, "carbs_g": 33, "fat_g": 10},
    "hamburger": {"calories": 295, "protein_g": 17, "carbs_g": 24, "fat_g": 14},
    "salad": {"calories": 80, "protein_g": 3, "carbs_g": 10, "fat_g": 4},
    "sushi": {"calories": 150, "protein_g": 6, "carbs_g": 28, "fat_g": 1},
    "soup": {"calories": 70, "protein_g": 3, "carbs_g": 9, "fat_g": 2},
    "fried_rice": {"calories": 174, "protein_g": 4, "carbs_g": 25, "fat_g": 6},
    "steak": {"calories": 271, "protein_g": 26, "carbs_g": 0, "fat_g": 19},
    "grilled_salmon": {"calories": 206, "protein_g": 22, "carbs_g": 0, "fat_g": 12},
    "apple_pie": {"calories": 237, "protein_g": 2, "carbs_g": 34, "fat_g": 11},
    "ice_cream": {"calories": 207, "protein_g": 4, "carbs_g": 24, "fat_g": 11},
}
DEFAULT_NUTRITION = {"calories": 160, "protein_g": 7, "carbs_g": 20, "fat_g": 6}


@lru_cache(maxsize=1)
def _classifier():
    return pipeline("image-classification", model=MODEL_NAME)


def analyze_food(image, serving_grams=250):
    predictions = _classifier()(image)
    if not predictions:
        raise RuntimeError("The model returned no predictions.")

    top = predictions[0]
    label = top["label"].strip().lower().replace(" ", "_")
    base = NUTRITION_PER_100G.get(label, DEFAULT_NUTRITION)
    factor = serving_grams / 100
    nutrition = {
        key: round(value * factor) if key == "calories" else round(value * factor, 1)
        for key, value in base.items()
    }
    if label in NUTRITION_PER_100G:
        note = "Nutrition is a rough illustrative estimate based on the predicted category and serving slider."
    else:
        note = "No category-specific example was available; generic illustrative values are shown. Check a reliable nutrition source for real estimates."
    return {
        "label": top["label"],
        "confidence": float(top["score"]),
        "nutrition": nutrition,
        "note": note,
    }
