from fuzzywuzzy import process

class SioraAgent:
    def __init__(self, budget=1000):
        self.budget = budget
        self.catalog = {
            "atta": 250,
            "shampoo": 180,
            "toothpaste": 90,
            "rice": 500,
            "dal": 200,
            "soap": 40,
            "milk": 60,
            "maggi": 20,
            "coffee": 150,
            "biryani masala": 75,
            "oil": 130,
            "salt": 25,
            "biscuits": 50
        }

    def get_items(self, user_input):
        user_items = [item.strip().lower() for item in user_input.split(",")]

        results = []
        for user_item in user_items:
            match, score = process.extractOne(user_item, self.catalog.keys())
            if score >= 70:
                results.append({"name": match, "price": self.catalog[match]})

        return results
