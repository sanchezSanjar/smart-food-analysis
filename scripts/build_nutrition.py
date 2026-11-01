"""Build data/foods.csv: per-100 g nutrition for every Food-101 class from USDA FNDDS.

Source: USDA FoodData Central, Survey Foods (FNDDS) 2024-10-31 (public domain).
Download the CSV zip from https://fdc.nal.usda.gov/download-datasets and unzip it into data/raw/.

Each dish maps to one FNDDS food, or to a weighted mix when no single entry fits
(e.g. fish and chips = fried cod + restaurant fries). The fruit/vegetable/legume share is an
estimate per dish (potatoes excluded, as in Nutri-Score), needed by the Nutri-Score; USDA does
not publish it.

Run:  .venv\\Scripts\\python.exe scripts\\build_nutrition.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "FoodData_Central_survey_food_csv_2024-10-31"
OUT = ROOT / "data" / "foods.csv"

NUTRIENTS = {  # FNDDS nutrient number (food_nutrient.csv uses these) -> column, all per 100 g
    208: "kcal", 203: "protein_g", 205: "carbs_g", 204: "fat_g",
    606: "sat_fat_g", 269: "sugars_g", 291: "fiber_g", 307: "sodium_mg",
}

# label: (category, fruit/veg/legume %, [(FNDDS description, weight share), ...])
FOODS = {
    "apple_pie": ("dessert", 35, [("Pie, apple", 1)]),
    "baby_back_ribs": ("main", 0, [("Pork, ribs", 1)]),
    "baklava": ("dessert", 0, [("Baklava", 1)]),
    "beef_carpaccio": ("main", 5, [("Steak tartare", 1)]),
    "beef_tartare": ("main", 5, [("Steak tartare", 1)]),
    "beet_salad": ("salad", 75, [("Beets, fresh, cooked, no added fat", 0.79), ("Cheese, Feta", 0.15), ("Olive oil", 0.06)]),
    "beignets": ("dessert", 0, [("Beignet", 1)]),
    "bibimbap": ("main", 35, [("Bibimbap, Korean", 1)]),
    "bread_pudding": ("dessert", 0, [("Pudding, bread", 1)]),
    "breakfast_burrito": ("breakfast", 10, [("Egg burrito", 1)]),
    "bruschetta": ("snack", 40, [("Bruschetta", 1)]),
    "caesar_salad": ("salad", 60, [("Caesar salad, with romaine, no dressing", 0.85), ("Caesar dressing", 0.15)]),
    "cannoli": ("dessert", 0, [("Cheese, Ricotta", 0.45), ("Churros", 0.55)]),
    "caprese_salad": ("salad", 55, [("Tomatoes, raw", 0.57), ("Cheese, Mozzarella, NFS", 0.38), ("Olive oil", 0.05)]),
    "carrot_cake": ("dessert", 10, [("Cake or cupcake, carrot", 1)]),
    "ceviche": ("seafood", 30, [("Ceviche", 1)]),
    "cheese_plate": ("snack", 0, [("Cheese, NFS", 1)]),
    "cheesecake": ("dessert", 0, [("Cheesecake, plain", 1)]),
    "chicken_curry": ("main", 25, [("Chicken curry", 1)]),
    "chicken_quesadilla": ("main", 5, [("Quesadilla, chicken", 1)]),
    "chicken_wings": ("main", 0, [("Chicken wing, baked, coated", 1)]),
    "chocolate_cake": ("dessert", 0, [("Cake or cupcake, chocolate with chocolate icing, bakery", 1)]),
    "chocolate_mousse": ("dessert", 0, [("Mousse", 1)]),
    "churros": ("dessert", 0, [("Churros", 1)]),
    "clam_chowder": ("soup", 10, [("Soup, New England clam chowder", 1)]),
    "club_sandwich": ("sandwich", 10, [("Club sandwich on white", 1)]),
    "crab_cakes": ("seafood", 5, [("Crab, cake", 1)]),
    "creme_brulee": ("dessert", 0, [("Creme brulee", 1)]),
    "croque_madame": ("sandwich", 0, [("Ham sandwich on white, with cheese", 0.82), ("Egg, whole, fried with butter", 0.18)]),
    "cup_cakes": ("dessert", 0, [("Cake or cupcake, NFS", 1)]),
    "deviled_eggs": ("snack", 0, [("Egg, deviled", 1)]),
    "donuts": ("dessert", 0, [("Doughnut, NFS", 1)]),
    "dumplings": ("main", 15, [("Wonton, dumpling or pot sticker, steamed", 1)]),
    "edamame": ("snack", 100, [("Edamame, cooked", 1)]),
    "eggs_benedict": ("breakfast", 0, [("Egg, Benedict", 1)]),
    "escargots": ("seafood", 0, [("Escargot", 1)]),
    "falafel": ("main", 70, [("Falafel", 1)]),
    "filet_mignon": ("main", 0, [("Beef, steak, tenderloin", 1)]),
    "fish_and_chips": ("seafood", 0, [("Fish, cod, fried", 0.5), ("Potato, french fries, restaurant", 0.5)]),
    "foie_gras": ("snack", 0, [("Liver, paste or pate", 1)]),
    "french_fries": ("snack", 0, [("Potato, french fries, restaurant", 1)]),
    "french_onion_soup": ("soup", 30, [("Soup, French onion", 1)]),
    "french_toast": ("breakfast", 0, [("French toast, plain", 1)]),
    "fried_calamari": ("seafood", 0, [("Calamari, fried", 1)]),
    "fried_rice": ("main", 15, [("Rice, fried, NFS", 1)]),
    "frozen_yogurt": ("dessert", 0, [("Frozen yogurt, vanilla", 1)]),
    "garlic_bread": ("snack", 0, [("Garlic bread, NFS", 1)]),
    "gnocchi": ("main", 0, [("Gnocchi, potato", 1)]),
    "greek_salad": ("salad", 80, [("Greek Salad, no dressing", 0.94), ("Olive oil", 0.06)]),
    "grilled_cheese_sandwich": ("sandwich", 0, [("Grilled cheese sandwich, NFS", 1)]),
    "grilled_salmon": ("seafood", 0, [("Fish, salmon, grilled", 1)]),
    "guacamole": ("snack", 95, [("Guacamole, NFS", 1)]),
    "gyoza": ("main", 15, [("Wonton, dumpling or pot sticker, fried", 1)]),
    "hamburger": ("sandwich", 10, [("Hamburger, NFS", 1)]),
    "hot_and_sour_soup": ("soup", 25, [("Soup, hot and sour", 1)]),
    "hot_dog": ("sandwich", 0, [("Hot dog sandwich, NFS, on white bun", 1)]),
    "huevos_rancheros": ("breakfast", 40, [("Huevos rancheros", 1)]),
    "hummus": ("snack", 85, [("Hummus, plain", 1)]),
    "ice_cream": ("dessert", 0, [("Ice cream, vanilla", 1)]),
    "lasagna": ("main", 20, [("Lasagna with meat", 1)]),
    "lobster_bisque": ("soup", 10, [("Soup, bisque", 1)]),
    "lobster_roll_sandwich": ("sandwich", 5, [("Lobster salad", 0.6), ("Roll, white, hot dog bun", 0.4)]),
    "macaroni_and_cheese": ("main", 0, [("Macaroni or noodles with cheese", 1)]),
    "macarons": ("dessert", 0, [("Cookie, macaroon", 1)]),
    "miso_soup": ("soup", 30, [("Soup, miso or tofu", 1)]),
    "mussels": ("seafood", 0, [("Mussels", 1)]),
    "nachos": ("snack", 10, [("Nachos, NFS", 1)]),
    "omelette": ("breakfast", 0, [("Egg omelet or scrambled egg, NS as to fat", 1)]),
    "onion_rings": ("snack", 45, [("Fried onion rings", 1)]),
    "oysters": ("seafood", 0, [("Oysters, raw", 1)]),
    "pad_thai": ("main", 20, [("Pad Thai with chicken", 1)]),
    "paella": ("main", 20, [("Paella with seafood", 1)]),
    "pancakes": ("breakfast", 0, [("Pancakes, plain", 1)]),
    "panna_cotta": ("dessert", 0, [("Custard", 1)]),
    "peking_duck": ("main", 0, [("Duck, Peking", 1)]),
    "pho": ("soup", 15, [("Soup, pho, with meat", 1)]),
    "pizza": ("main", 10, [("Pizza, cheese, from restaurant or fast food, medium crust", 1)]),
    "pork_chop": ("main", 0, [("Pork, chop, lean and fat eaten", 1)]),
    "poutine": ("snack", 0, [("Potato, french fries, restaurant", 0.6), ("Cheese, Cheddar", 0.2), ("Gravy, beef", 0.2)]),
    "prime_rib": ("main", 0, [("Beef, roast", 1)]),
    "pulled_pork_sandwich": ("sandwich", 0, [("Barbecue pork sandwich, on white bun", 1)]),
    "ramen": ("soup", 15, [("Ramen bowl, NFS", 1)]),
    "ravioli": ("main", 20, [("Ravioli, cheese-filled, with tomato sauce", 1)]),
    "red_velvet_cake": ("dessert", 0, [("Cake or cupcake, red velvet", 1)]),
    "risotto": ("main", 5, [("Rice, cooked, NFS", 0.88), ("Cheese, Parmesan, hard", 0.08), ("Olive oil", 0.04)]),
    "samosa": ("snack", 15, [("Samosa", 1)]),
    "sashimi": ("seafood", 0, [("Fish, salmon, raw", 0.5), ("Fish, tuna, raw", 0.5)]),
    "scallops": ("seafood", 0, [("Scallops, grilled", 1)]),
    "seaweed_salad": ("salad", 85, [("Seaweed, raw", 0.88), ("Sesame dressing", 0.12)]),
    "shrimp_and_grits": ("seafood", 0, [("Grits, NFS", 0.6), ("Shrimp, grilled", 0.4)]),
    "spaghetti_bolognese": ("main", 20, [("Pasta, cooked", 0.6), ("Spaghetti sauce with meat", 0.4)]),
    "spaghetti_carbonara": ("main", 0, [("Pasta with cream sauce, restaurant", 1)]),
    "spring_rolls": ("snack", 40, [("Egg roll, meatless", 1)]),
    "steak": ("main", 0, [("Beef, steak, NFS", 1)]),
    "strawberry_shortcake": ("dessert", 20, [("Cake, strawberry shortcake", 1)]),
    "sushi": ("seafood", 5, [("Sushi, NFS", 1)]),
    "tacos": ("main", 15, [("Taco, NFS", 1)]),
    "takoyaki": ("snack", 5, [("Pancakes, plain", 0.7), ("Octopus", 0.3)]),
    "tiramisu": ("dessert", 0, [("Tiramisu", 1)]),
    "tuna_tartare": ("seafood", 10, [("Fish, tuna, raw", 1)]),
    "waffles": ("breakfast", 0, [("Waffle, plain", 1)]),
}


def load_fndds():
    ids = {}
    with open(RAW / "food.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ids[row["description"]] = int(row["fdc_id"])
    values = {}
    wanted = set(NUTRIENTS)
    with open(RAW / "food_nutrient.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            nutrient = int(row["nutrient_id"])
            if nutrient in wanted:
                values.setdefault(int(row["fdc_id"]), {})[NUTRIENTS[nutrient]] = float(row["amount"])
    return ids, values


def build():
    ids, values = load_fndds()
    missing = [d for _, _, parts in FOODS.values() for d, _ in parts if d not in ids]
    if missing:
        raise SystemExit(f"Not found in FNDDS: {missing}")

    rows = []
    for label, (category, fruit_veg, parts) in sorted(FOODS.items()):
        assert abs(sum(share for _, share in parts) - 1) < 1e-6, label
        mixed = {column: 0.0 for column in NUTRIENTS.values()}
        for description, share in parts:
            per_100g = values[ids[description]]
            for column in mixed:
                mixed[column] += per_100g.get(column, 0.0) * share
        rows.append({
            "label": label,
            "name": label.replace("_", " ").capitalize(),
            "category": category,
            **{k: round(v, 1) for k, v in mixed.items()},
            "fruit_veg_pct": fruit_veg,
            "usda_source": " + ".join(f"{d} ({share:.0%})" if share < 1 else d for d, share in parts),
            "fdc_ids": " ".join(str(ids[d]) for d, _ in parts),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} foods to {OUT}")


if __name__ == "__main__":
    build()
