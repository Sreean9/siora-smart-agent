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
    # Explicitly verify return values
    try:
        # Call parse_request and immediately check length
        parse_result = agent.parse_request(user_input)
        st.write(f"Parse result: {parse_result}")
        st.write(f"Type of parse result: {type(parse_result)}")
        st.write(f"Length of parse result: {len(parse_result)}")
        
        # Manually unpack to avoid ValueError
        if len(parse_result) >= 3:
            items = parse_result[0]
            quantities = parse_result[1]
            budget = parse_result[2]
            
            st.write(f"Items: {items}")
            st.write(f"Quantities: {quantities}")
            st.write(f"Budget: {budget}")
            
            # Call create_cart with individual arguments
            cart_result = agent.create_cart(items, quantities, budget)
            st.write(f"Cart result length: {len(cart_result)}")
            
            # Manually unpack again
            if len(cart_result) >= 4:
                cart = cart_result[0]
                total = cart_result[1]
                approved = cart_result[2]
                not_found = cart_result[3]
                
                # Display cart
                st.write("### Cart:")
                for item in cart:
                    st.write(f"- {item['quantity']} {item['unit']} {item['name']} - ₹{item['total_price']}")
                
                st.write(f"Total: ₹{total}")
                st.write(f"Approved: {approved}")
                
                if not_found:
                    st.warning(f"Not found: {', '.join(not_found)}")
            else:
                st.error(f"Invalid cart_result length: {len(cart_result)}")
        else:
            st.error(f"Invalid parse_result length: {len(parse_result)}")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
