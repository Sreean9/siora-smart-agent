import json

class SioraAgent:
    def __init__(self, product_db):
        self.database = product_db

    def parse_request(self, text):
        # Simple logic: extract known product names from user text
        budget = 800  # Default for demo
        items = [word for word in text.lower().split() if word in self.database]
        return items, budget

    def create_cart(self, items, budget):
        cart = []
        total = 0
        for item in items:
            product = self.database.get(item)
            if product:
                total += product['price']
                cart.append(product)
        approved = total <= budget
        return cart, total, approved
