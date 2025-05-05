import difflib
import re

class SioraAgent:
    def __init__(self, products):
        self.products = products

    def parse_request(self, request):
        """
        Parse a shopping request to extract product names, quantities, and budget.
        """
        # Initialize with empty values
        items = []
        quantities = {}
        budget = None
        
        try:
            # Clean input
            text = request.lower().strip()
            
            # Check for "2kg rice" pattern
            match = re.search(r'(\d+)kg\s+rice', text)
            if match:
                quantity = int(match.group(1))
                items = ["rice"]
                quantities = {"rice": {"amount": quantity, "unit": "kg"}}
            else:
                # Generic parsing
                parts = [p.strip() for p in text.split(',')]
                
                for part in parts:
                    words = part.split()
                    if len(words) >= 2:
                        # Check for quantity-first pattern (e.g., "2kg rice")
                        if words[0][0].isdigit():
                            # Extract quantity and unit
                            qty_str = words[0]
                            qty_match = re.match(r'(\d+)([a-zA-Z]*)', qty_str)
                            
                            if qty_match:
                                quantity = int(qty_match.group(1))
                                unit = qty_match.group(2) or ""
                                product = " ".join(words[1:])
                                
                                items.append(product)
                                quantities[product] = {"amount": quantity, "unit": unit}
                        else:
                            # Just add as a simple product
                            items.append(part)
                    else:
                        # Single word product
                        items.append(part)
        except Exception as e:
            print(f"Error in parse_request: {str(e)}")
        
        # Always return 3 values
        return items, quantities, budget

    def create_cart(self, items, quantities=None, budget=None):
        """
        Create a shopping cart based on the requested items.
        Takes exactly 3 arguments and returns 4 values.
        """
        # Default values
        if items is None:
            items = []
        if quantities is None:
            quantities = {}
        
        cart = []
        total = 0
        not_found = []
        
        try:
            # Process items
            for item in items:
                # Find matching product
                product_names = [p['name'].lower() for p in self.products]
                matches = difflib.get_close_matches(item.lower(), product_names, n=1, cutoff=0.6)
                
                if matches:
                    best_match = matches[0]
                    idx = product_names.index(best_match)
                    product = self.products[idx].copy()
                    
                    # Add quantity information
                    if item in quantities:
                        product['quantity'] = quantities[item]['amount']
                        product['unit'] = quantities[item]['unit']
                        product['total_price'] = product['price'] * product['quantity']
                    else:
                        product['quantity'] = 1
                        product['unit'] = ''
                        product['total_price'] = product['price']
                    
                    cart.append(product)
                    total += product['total_price']
                else:
                    not_found.append(item)
            
            # Determine if cart is approved
            approved = (budget is None or total <= budget) and bool(cart)
        except Exception as e:
            print(f"Error in create_cart: {str(e)}")
            cart = []
            total = 0
            approved = False
            not_found = items.copy() if items else []
        
        return cart, total, approved, not_found
