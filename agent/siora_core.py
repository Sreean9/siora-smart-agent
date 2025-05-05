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
        
        Returns:
        - items: List of product names
        - quantities: Dictionary of quantities
        - budget: Budget limit or None
        """
        request = request.lower()
        
        # Initialize return values
        items = []
        quantities = {}
        budget = None
        
        # Extract budget if present
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
                try:
                    budget = int(budget_match.group(1))
                    break
                except (ValueError, IndexError):
                    # If conversion fails, continue with None budget
                    pass
        
        # Clean the request for item extraction
        request = re.sub(r'buy|need|get|want|please|i need|i want', '', request)
        
        # Replace 'and' with comma for consistent splitting
        request = request.replace(' and ', ', ')
        
        # Split by commas
        raw_items = [item.strip() for item in request.split(',') if item.strip()]
        
        # If no items found after comma splitting, try to extract from the whole string
        if not raw_items and request.strip():
            raw_items = [request.strip()]
        
        # Process each item to extract product names
        for raw_item in raw_items:
            # Safely extract product name and quantity
            try:
                # Pattern: product name followed by optional quantity and unit
                match = re.match(r'([a-zA-Z\s]+)(?:\s+(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?)?', raw_item)
                
                if match:
                    product_name = match.group(1).strip()
                    quantity_str = match.group(2)
                    unit = match.group(3) if match.group(3) else ''
                    
                    # Only add if we have a product name
                    if product_name:
                        items.append(product_name)
                        
                        # Add quantity information if available
                        if quantity_str:
                            try:
                                quantity = float(quantity_str)
                                quantities[product_name] = {
                                    'amount': quantity,
                                    'unit': unit
                                }
                            except ValueError:
                                # If conversion fails, default to quantity 1
                                quantities[product_name] = {
                                    'amount': 1,
                                    'unit': ''
                                }
                else:
                    # If regex doesn't match, just use the first word as product
                    words = raw_item.split()
                    if words:
                        product_name = words[0].strip()
                        if product_name:
                            items.append(product_name)
            except Exception:
                # If any error occurs in parsing this item, try to extract at least the product name
                words = raw_item.split()
                if words:
                    product_name = words[0].strip()
                    if product_name:
                        items.append(product_name)
        
        # Ensure we have at least one item
        if not items and raw_items:
            # Fallback: just use the first word of each raw item
            for raw_item in raw_items:
                words = raw_item.split()
                if words:
                    items.append(words[0].strip())
        
        # Ensure we return the expected 3 values
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
            
            # Try to find a match with decreasing cutoff values
            match_found = False
            for cutoff in [0.8, 0.6, 0.4]:
                matches = difflib.get_close_matches(item.lower(), product_names, n=3, cutoff=cutoff)
                if matches:
                    match_found = True
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
                    break
            
            if not match_found:
                not_found.append(item)
        
        # Check if cart is approved (within budget)
        approved = (budget is None or total <= budget) and bool(cart)
        
        return cart, total, approved, not_found
