import sys
import os
import streamlit as st

# Add parent directory to path for custom imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.siora_core import SioraAgent

# Sample products
sample_products = [
    {"name": "Rice", "price": 60},
    {"name": "Milk", "price": 25},
    {"name": "Apples", "price": 15}
]

# Create agent
agent = SioraAgent(sample_products)

st.title("Siora Shopping Agent")

# User input
user_input = st.text_input("What do you need today?", "2kg rice")

def safe_parse_request(text):
    """Wrapper to ensure parse_request returns 3 values"""
    try:
        # Call the original method
        result = agent.parse_request(text)
        
        # Force it to be a 3-tuple no matter what
        if isinstance(result, tuple):
            if len(result) == 0:
                return [], {}, None
            elif len(result) == 1:
                return result[0], {}, None
            elif len(result) == 2:
                return result[0], result[1], None
            else:  # 3 or more
                return result[0], result[1], result[2]
        else:
            # Not a tuple at all
            return [result], {}, None
    except Exception as e:
        st.error(f"Error in safe_parse_request: {str(e)}")
        return [], {}, None

def safe_create_cart(items, quantities, budget):
    """Wrapper to ensure create_cart returns 4 values"""
    try:
        # Call the original method
        result = agent.create_cart(items, quantities, budget)
        
        # Force it to be a 4-tuple no matter what
        if isinstance(result, tuple):
            if len(result) == 0:
                return [], 0, False, []
            elif len(result) == 1:
                return result[0], 0, False, []
            elif len(result) == 2:
                return result[0], result[1], False, []
            elif len(result) == 3:
                return result[0], result[1], result[2], []
            else:  # 4 or more
                return result[0], result[1], result[2], result[3]
        else:
            # Not a tuple at all
            return [result], 0, False, []
    except Exception as e:
        st.error(f"Error in safe_create_cart: {str(e)}")
        return [], 0, False, []

if st.button("Ask Siora"):
    try:
        # Use the safe wrappers to guarantee correct return values
        items, quantities, budget = safe_parse_request(user_input)
        
        st.write("### Parsed Request:")
        st.write(f"Items: {items}")
        st.write(f"Quantities: {quantities}")
        st.write(f"Budget: {budget}")
        
        cart, total, approved, not_found = safe_create_cart(items, quantities, budget)
        
        st.write("### Cart:")
        if cart:
            for item in cart:
                quantity_str = f"{item['quantity']} {item['unit']}" if item['unit'] else f"{item['quantity']}"
                st.write(f"- {quantity_str} {item['name']} - ₹{item['total_price']}")
            
            st.write(f"**Total: ₹{total}**")
            
            if approved:
                st.success("✅ Your cart is ready for checkout!")
            else:
                if budget is not None:
                    st.error(f"❌ Budget exceeded (₹{budget}).")
            
            if not_found:
                st.warning(f"Could not find: {', '.join(not_found)}")
        else:
            st.info("No items found or added to cart.")
            
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
