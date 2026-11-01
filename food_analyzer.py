"""Food recognition (Food-101 classifier) combined with nutrition and health grade."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from nutrition import Food, get_food

MODEL_ID = "nateraw/food"
MODEL_DIR = Path(__file__).resolve().parent / "models" / "food"
LOW_CONFIDENCE = 0.5  # below this the photo may show a food the model does not know


@dataclass
class Guess:
    food: Food
    confidence: float


@dataclass
class Analysis:
    guesses: list  # best first
    grams: int

    @property
    def best(self):
        return self.guesses[0]

    @property
    def is_uncertain(self):
        return self.best.confidence < LOW_CONFIDENCE


@lru_cache(maxsize=1)
def classifier():
    """Image classifier on the GPU when available; loads from models/food when downloaded."""
    import torch
    from transformers import pipeline

    local = (MODEL_DIR / "config.json").exists()
    return pipeline(
        "image-classification",
        model=str(MODEL_DIR) if local else MODEL_ID,
        device=0 if torch.cuda.is_available() else -1,
    )


def device_name():
    import torch
    return torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"


def analyze_food(image, serving_grams=250, top_k=3):
    predictions = classifier()(image.convert("RGB"), top_k=top_k)
    if not predictions:
        raise RuntimeError("The model returned no predictions.")
    guesses = []
    for prediction in predictions:
        food = get_food(prediction["label"])
        if food is not None:
            guesses.append(Guess(food, float(prediction["score"])))
    if not guesses:
        raise RuntimeError(f"No nutrition data for {predictions[0]['label']!r}.")
    return Analysis(guesses, serving_grams)
