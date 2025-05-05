import sys
import os
import streamlit as st

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
        # This is the line that's causing the issue
        result = agent.parse_request(user_input)
        
        # Explicitly unpack the result to make sure we have 3 values
        if len(result) == 3:
            items, quantities, budget = result
            st.success(f"Parsed successfully: {items}, {quantities}, {budget}")
        else:
            st.error(f"Parse_request returned {len(result)} values instead of 3: {result}")
            
        # Try to create cart
        cart, total, approved, not_found = agent.create_cart(*result)
        
        # Display cart
        st.write(f"Cart: {cart}")
        st.write(f"Total: {total}")
        st.write(f"Approved: {approved}")
        st.write(f"Not found: {not_found}")
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
