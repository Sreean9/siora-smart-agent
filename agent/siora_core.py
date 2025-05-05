import difflib

class SioraAgent:
    def __init__(self, products):
        self.products = products

    def parse_request(self, request):
        request = request.lower().replace('buy', '').replace('and', ',')
        items = [item.strip() for item in request.split(',') if item.strip()]
        budget = None
        for word in request.split():
            if word.isdigit():
                budget = int(word)
        return items, budget

    def create_cart(self, items, budget=None):
        cart = []
        total = 0
        not_found = []
        for item in items:
            names = [p['name'].lower() for p in self.products]
            match = difflib.get_close_matches(item.lower(), names, n=1, cutoff=0.4)
            if match:
                idx = names.index(match[0])
                product = self.products[idx]
                cart.append(product)
                total += product['price']
            else:
                not_found.append(item)
        approved = (budget is None or total <= budget) and bool(cart)
        return cart, total, approved, not_found
