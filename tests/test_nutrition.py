import unittest

from nutrition import all_foods, get_food, healthier_swaps, nutri_score


def facts(kcal=0, sugars=0, sat_fat=0, sodium=0, fiber=0, protein=0):
    return {"kcal": kcal, "sugars_g": sugars, "sat_fat_g": sat_fat, "sodium_mg": sodium,
            "fiber_g": fiber, "protein_g": protein, "fat_g": 0, "carbs_g": 0}


class NutriScoreTest(unittest.TestCase):
    def test_points_thresholds(self):
        # 400 kcal = 1673.6 kJ -> 4 energy points; 20 g sugar -> 4; 3.5 g sat fat -> 3; 500 mg sodium -> 5
        health = nutri_score(facts(kcal=400, sugars=20, sat_fat=3.5, sodium=500), 0)
        self.assertEqual(health.negative, {"energy": 4, "sugars": 4, "sat_fat": 3, "sodium": 5})

    def test_vegetables_give_grade_a(self):
        health = nutri_score(facts(kcal=40, sugars=2, sodium=20, fiber=3, protein=2), 90)
        self.assertEqual(health.grade, "A")
        self.assertLess(health.score, 0)

    def test_protein_ignored_when_unhealthy(self):
        # 500 kcal = 2092 kJ -> 6, sugars 10 -> 2, sat fat 6 -> 5, sodium 600 -> 6: 19 negative points.
        # With few vegetables the 5 protein points must not be subtracted.
        health = nutri_score(facts(kcal=500, sugars=10, sat_fat=6, sodium=600, protein=20), 0)
        self.assertEqual(sum(health.negative.values()), 19)
        self.assertEqual(health.positive["protein"], 5)
        self.assertEqual(health.score, 19)
        self.assertEqual(health.grade, "E")

    def test_grade_boundaries(self):
        cases = [(-1, "A"), (0, "B"), (2, "B"), (3, "C"), (10, "C"), (11, "D"), (18, "D"), (19, "E")]
        for target, grade in cases:
            sodium = [0, 90, 180, 270, 360, 450, 540, 630, 720, 810, 900][min(max(target, 0), 10)] + 1
            extra_sugar = max(target - 10, 0)
            sugars = [0, 4.5, 9, 13.5, 18, 22.5, 27, 31, 36, 40, 45][extra_sugar] + 0.1 if extra_sugar else 0
            fiber = 1.0 if target < 0 else 0  # one positive point
            health = nutri_score(facts(sodium=sodium if target > 0 else 0, sugars=sugars, fiber=fiber), 0)
            self.assertEqual(health.score, target)
            self.assertEqual(health.grade, grade, target)


class FoodTableTest(unittest.TestCase):
    def test_all_101_classes_have_data(self):
        foods = all_foods()
        self.assertEqual(len(foods), 101)
        self.assertTrue(all(food.per_100g["kcal"] > 0 for food in foods.values()))

    def test_salad_is_healthier_than_cake(self):
        self.assertLess(get_food("greek_salad").health.score, get_food("chocolate_cake").health.score)
        self.assertIn(get_food("edamame").health.grade, "AB")

    def test_serving_scales(self):
        pizza = get_food("Pizza")
        self.assertAlmostEqual(pizza.serving(250)["kcal"], pizza.per_100g["kcal"] * 2.5)

    def test_swaps_are_better(self):
        burger = get_food("hamburger")
        swaps = healthier_swaps(burger)
        self.assertTrue(swaps)
        self.assertTrue(all(s.health.grade < burger.health.grade for s in swaps))


if __name__ == "__main__":
    unittest.main()
