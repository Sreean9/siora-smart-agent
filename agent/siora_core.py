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
        - "2kg rice, 1L milk, 5 apples"
        
        Returns:
        - items: List of product names
        - quantities: Dictionary of quantities
        - budget: Budget limit or None
        """
        # Initialize return values
        items = []
        quantities = {}
        budget = None
        
        # Clean and normalize the request
        request = request.lower().strip()
        
        # Extract budget if present
        budget_match = re.search(r'under\s+(\d+)', request)
        if budget_match:
            try:
                budget = int(budget_match.group(1))
            except (ValueError, IndexError):
                budget = None
        
        # Clean up the request by removing common shopping phrases
        request = re.sub(r'\b(buy|get|need|want|please)\b', '', request)
        
        # Replace 'and' with comma for consistent splitting
        request = re.sub(r'\band\b', ',', request)
        
        # Split by commas
        parts = [part.strip() for part in request.split(',') if part.strip()]
        
        for part in parts:
            # Here we'll handle two possible formats:
            # 1. "product quantity unit" format (e.g., "rice 2kg")
            # 2. "quantity unit product" format (e.g., "2kg rice")
            
            # Check for format #2 first (quantity comes first)
            quantity_first_match = re.match(r'^(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?\s+([a-zA-Z\s]+)$', part)
            
            if quantity_first_match:
                # Format is "2kg rice" or "5 apples"
                quantity = float(quantity_first_match.group(1))
                unit = quantity_first_match.group(2) or ''
                product = quantity_first_match.group(3).strip()
                
                items.append(product)
                quantities[product] = {'amount': quantity, 'unit': unit}
            else:
                # Try format #1 (product comes first)
                product_first_match = re.match(r'^([a-zA-Z\s]+)\s+(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?$', part)
                
                if product_first_match:
                    # Format is "rice 2kg"
                    product = product_first_match.group(1).strip()
                    quantity = float(product_first_match.group(2))
                    unit = product_first_match.group(3) or ''
                    
                    items.append(product)
                    quantities[product] = {'amount': quantity, 'unit': unit}
                else:
                    # No quantity found, just add the product
                    items.append(part)
        
        # If we couldn't parse anything, use a simple fallback
        if not items and parts:
            # Just use each part as a product name
            items = parts
        
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
        # Default empty dictionary if quantities is None
        if quantities is None:
            quantities = {}
            
        cart = []
        total = 0
        not_found = []
        
        for item in items:
            # Get close matches from product database
            product_names = [p['name'].lower() for p in self.products]
            matches = difflib.get_close_matches(item.lower(), product_names, n=1, cutoff=0.6)
            
            if matches:
                best_match = matches[0]
                idx = product_names.index(best_match)
                product = self.products[idx].copy()  # Copy to avoid modifying original
                
                # Add quantity information if available
                if item in quantities:
                    product['quantity'] = quantities[item]['amount']
                    product['unit'] = quantities[item]['unit']
                    # Adjust price based on quantity
                    product['total_price'] = product['price'] * product['quantity']
                else:
                    product['quantity'] = 1
                    product['unit'] = ''
                    product['total_price'] = product['price']
                
                cart.append(product)
                total += product['total_price']
            else:
                not_found.append(item)
        
        # Check if cart is approved (within budget)
        approved = (budget is None or total <= budget) and bool(cart)
        
        return cart, total, approved, not_found
