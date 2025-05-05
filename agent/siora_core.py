import difflib
import re

class SioraAgent:
    def __init__(self, products):
        self.products = products

    def parse_request(self, request):
        """
        Parse a shopping request to extract product names, quantities, and budget.
        Always returns exactly 3 values: items, quantities, budget
        """
        try:
            # Initialize with default values
            items = []
            quantities = {}
            budget = None
            
            # Process input text - handle common formats
            text = request.lower().strip()
            
            # Split by commas
            parts = [part.strip() for part in text.split(',')]
            
            # Process each part to extract items and quantities
            for part in parts:
                # Try to identify the product and quantity
                words = part.split()
                if not words:
                    continue
                
                # Check if the first word starts with a number (e.g., "2kg rice")
                if words[0][0].isdigit():
                    # Format is likely "quantity product"
                    # Extract quantity and unit
                    quantity_match = re.match(r'(\d+(?:\.\d+)?)([a-zA-Z]*)', words[0])
                    if quantity_match:
                        quantity = float(quantity_match.group(1))
                        unit = quantity_match.group(2) or ''
                        
                        # Join remaining words as product name
                        product = ' '.join(words[1:])
                        
                        items.append(product)
                        quantities[product] = {'amount': quantity, 'unit': unit}
                    else:
                        # Just add the whole part as a product
                        items.append(part)
                else:
                    # Format is likely "product quantity" or just "product"
                    # Check if the last word starts with a number
                    if len(words) > 1 and words[-1][0].isdigit():
                        # Extract quantity and unit
                        quantity_match = re.match(r'(\d+(?:\.\d+)?)([a-zA-Z]*)', words[-1])
                        if quantity_match:
                            quantity = float(quantity_match.group(1))
                            unit = quantity_match.group(2) or ''
                            
                            # Join all but the last word as product name
                            product = ' '.join(words[:-1])
                            
                            items.append(product)
                            quantities[product] = {'amount': quantity, 'unit': unit}
                        else:
                            # Just add the whole part as a product
                            items.append(part)
                    else:
                        # No quantity found, just add as product
                        items.append(part)
            
            # Extract budget if present
            budget_match = re.search(r'under\s+(\d+)', text)
            if budget_match:
                try:
                    budget = int(budget_match.group(1))
                except (ValueError, IndexError):
                    budget = None
                    
            # Make sure we have at least one item
            if not items and parts:
                items = parts
                
            # Return exactly 3 values
            return items, quantities, budget
            
        except Exception as e:
            # If any error occurs, return default values
            print(f"Error in parse_request: {str(e)}")
            return [], {}, None

    def create_cart(self, items, quantities=None, budget=None):
        """
        Create a shopping cart based on the requested items.
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
