class SioraAgent:
    def __init__(self, products):
        self.products = products
    
    def parse_request(self, request):
        # Very basic: split by "and", extract budget after "under"
        items = []
        budget = 1000  # default budget
        if "under" in request:
            parts = request.split("under")
            items = [x.strip() for x in parts[0].replace("buy", "").split("and")]
            try:
                budget = int(parts[1].strip().split()[0])
            except:
                pass
        else:
            items = [x.strip() for x in request.replace("buy", "").split("and")]
        return items, budget

    def create_cart(self, items, budget):
        cart = []
        total = 0
        for item in items:
            found = next((prod for prod in self.products if item.lower() in prod['name'].lower()), None)
            if found:
                cart.append(found)
                total += found['price']
        approved = total <= budget
        return cart, total, approved
