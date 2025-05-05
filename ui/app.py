import sys
import os
import json
import streamlit as st

# Ensure the parent directory is in the Python path for custom imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.siora_core import SioraAgent

# Load product database
PRODUCTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'products.json'))

try:
    with open(PRODUCTS_PATH, "r") as f:
        products = json.load(f)
except FileNotFoundError:
    st.error(f"Product database not found at {PRODUCTS_PATH}")
    st.stop()

# Initialize the agent
agent = SioraAgent(products)

st.title("🛒 Siora – Your Smart Shopping Agent")

# User input
user_input = st.text_input("What do you need today?", placeholder="e.g. Buy atta and shampoo under 800")

if st.button("Ask Siora") and user_input.strip():
    try:
        items, budget = agent.parse_request(user_input)
        cart, total, approved = agent.create_cart(items, budget)

        st.write("### 🛍️ Items in your cart:")
        for item in cart:
            st.write(f"- {item['name']} – ₹{item['price']}")

        st.write(f"**Total: ₹{total}**")

        if approved:
            st.success("✅ All items are within budget. Proceeding with your Visa card simulation!")
        else:
            st.error("❌ Budget exceeded. Please revise your cart.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
elif st.button("Ask Siora"):
    st.warning("Please enter your shopping request.")

