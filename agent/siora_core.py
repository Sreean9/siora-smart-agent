from fuzzywuzzy import fuzz
from fuzzywuzzy import process

class SioraAgent:
    def __init__(self, products):
        self.products = products
        self.product_names = [p["name"] for p in products]

    def parse_request(self, text):
        text = text.lower()
        selected_items = []
        budget = None

        # Find likely product matches in the text
        for word in text.split():
            match, score = process.extractOne(word, self.product_names)
            if score > 80:  # Threshold for match confidence
                selected_items.append(match)

        # Remove duplicates
        selected_items = list(set(selected_items))

        # Try to extract a budget (e.g., "under 500")
        for word in text.split():
            if word.isdigit():
                budget = int(word)
                break

        return selected_items, budget

    def create_cart(self, items, budget):
        cart = []
        total = 0

        for item in items:
            for product in self.products:
                if product["name"] == item:
                    cart.append(product)
                    total += product["price"]

        approved = budget is None or total <= budget
        return cart, total, approved
