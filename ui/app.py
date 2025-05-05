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

if st.button("Ask Siora"):
    try:
        # Parse request and ensure it returns 3 values
        try:
            parse_result = agent.parse_request(user_input)
            # Check if we got a tuple with 3 elements
            if isinstance(parse_result, tuple) and len(parse_result) == 3:
                items, quantities, budget = parse_result
            else:
                st.error(f"parse_request returned {type(parse_result)} with length {len(parse_result) if hasattr(parse_result, '__len__') else 'N/A'}")
                # Provide default values
                items, quantities, budget = [], {}, None
        except Exception as e:
            st.error(f"Error parsing request: {str(e)}")
            items, quantities, budget = [], {}, None
        
        st.write("### Parsed Request:")
        st.write(f"Items: {items}")
        st.write(f"Quantities: {quantities}")
        st.write(f"Budget: {budget}")
        
        # Create cart - make sure we pass ONLY 3 arguments
        try:
            cart_result = agent.create_cart(items, quantities, budget)
            # Check if we got a tuple with 4 elements
            if isinstance(cart_result, tuple) and len(cart_result) == 4:
                cart, total, approved, not_found = cart_result
            else:
                st.error(f"create_cart returned {type(cart_result)} with length {len(cart_result) if hasattr(cart_result, '__len__') else 'N/A'}")
                # Provide default values
                cart, total, approved, not_found = [], 0, False, []
        except Exception as e:
            st.error(f"Error creating cart: {str(e)}")
            cart, total, approved, not_found = [], 0, False, []
        
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
