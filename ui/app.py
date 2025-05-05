import sys
import os
import streamlit as st
import traceback

# Add parent directory to path for custom imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.siora_core import SioraAgent

# Sample products for testing
sample_products = [
    {"name": "Rice", "price": 60},
    {"name": "Milk", "price": 25},
    {"name": "Apples", "price": 15}
]

# Create the agent with sample products
agent = SioraAgent(sample_products)

st.title("Siora Shopping Agent")

# User input
user_input = st.text_input("What do you need today?", "2kg rice, 1L milk, 5 apples")

if st.button("Ask Siora"):
    try:
        # Get parse result and explicitly print the length
        parse_result = agent.parse_request(user_input)
        st.write(f"Parse result: {parse_result}")
        st.write(f"Length of parse result: {len(parse_result)}")
        
        # Unpack only if we have exactly 3 values
        if len(parse_result) == 3:
            items, quantities, budget = parse_result
            
            # Print each value
            st.write(f"Items: {items}")
            st.write(f"Quantities: {quantities}")
            st.write(f"Budget: {budget}")
            
            # Create cart with separate arguments to avoid *result unpacking issue
            cart_result = agent.create_cart(items, quantities, budget)
            
            # Check cart result length
            st.write(f"Cart result length: {len(cart_result)}")
            
            # Unpack only if we have exactly 4 values
            if len(cart_result) == 4:
                cart, total, approved, not_found = cart_result
                
                # Display cart
                st.write("### Cart:")
                for item in cart:
                    st.write(f"- {item['quantity']} {item['unit']} {item['name']} - ₹{item['total_price']}")
                
                st.write(f"Total: ₹{total}")
                st.write(f"Approved: {approved}")
                
                if not_found:
                    st.warning(f"Not found: {', '.join(not_found)}")
            else:
                st.error(f"Expected 4 values from create_cart, got {len(cart_result)}")
        else:
            st.error(f"Expected 3 values from parse_request, got {len(parse_result)}")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.code(traceback.format_exc())
