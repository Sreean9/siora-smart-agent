import difflib
import re

class SioraAgent:
    def __init__(self, products):
        self.products = products

    def parse_request(self, request):
        """
        Parse a shopping request to extract product names, quantities, and budget.
        
        Example inputs:
        - "buy atta 5 kgs and sugar 2 kgs"
        - "I need rice 2kg, milk 1L under 500"
        """
        request = request.lower()
        
        # Extract budget if present
        budget = None
        budget_patterns = [
            r'under (\d+)',
            r'less than (\d+)',
            r'below (\d+)',
            r'not more than (\d+)',
            r'max (\d+)',
            r'budget (\d+)'
        ]
        
        for pattern in budget_patterns:
            budget_match = re.search(pattern, request)
            if budget_match:
                budget = int(budget_match.group(1))
                break
        
        # Clean the request for item extraction
        request = re.sub(r'buy|need|get|want|please|i need|i want', '', request)
        
        # Replace 'and' with comma for consistent splitting
        request = request.replace(' and ', ', ')
        
        # Split by commas
        raw_items = [item.strip() for item in request.split(',') if item.strip()]
        
        # Process each item to extract product names
        items = []
        quantities = {}
        
        for raw_item in raw_items:
            # Try to extract product name and quantity
            # Pattern: product name followed by optional quantity and unit
            match = re.match(r'([a-zA-Z\s]+)(?:\s+(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?)?', raw_item)
            
            if match:
                product_name = match.group(1).strip()
                quantity = match.group(2)
                unit = match.group(3) if match.group(3) else ''
                
                items.append(product_name)
                
                if quantity:
                    quantities[product_name] = {
                        'amount': float(quantity),
                        'unit': unit
                    }
        
        return items, quantities, budget

    def create_cart(self, items, quantities=None, budget=None):
        """
        Create a shopping cart based on the requested items.
        
        Args:
            items: List of product names
            quantities: Dictionary of product quantities {product_name: {'amount': float, 'unit': str}}
            budget: Maximum total cost (optional)
            
        Returns:
            cart: List of products in cart with quantities
            total: Total cost
            approved: Whether the cart is within budget
            not_found: List of items not found
        """
        if quantities is None:
            quantities = {}
            
        cart = []
        total = 0
        not_found = []
        
        for item in items:
            # Get close matches from product database
            product_names = [p['name'].lower() for p in self.products]
            matches = difflib.get_close_matches(item.lower(), product_names, n=3, cutoff=0.6)
            
            if matches:
                best_match = matches[0]
                idx = product_names.index(best_match)
                product = self.products[idx].copy()  # Copy to avoid modifying original
                
                # Add quantity information if available
                if item in quantities:
                    product['quantity'] = quantities[item]['amount']
                    product['unit'] = quantities[item]['unit']
                    # Adjust price based on quantity if needed
                    product['total_price'] = product['price'] * product['quantity']
                else:
                    product['quantity'] = 1
                    product['unit'] = ''
                    product['total_price'] = product['price']
                
                cart.append(product)
                total += product['total_price']
            else:
                not_found.append(item)
        
        approved = (budget is None or total <= budget) and bool(cart)
        return cart, total, approved, not_found
