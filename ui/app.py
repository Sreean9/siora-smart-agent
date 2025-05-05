import sys
import os
import json
import streamlit as st

# Add parent directory to path for custom imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.siora_core import SioraAgent

PRODUCTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'products.json'))

try:
    with open(PRODUCTS_PATH, "r") as f:
        products = json.load(f)
except FileNotFoundError:
    st.error(f"Product database not found at {PRODUCTS_PATH}")
    st.stop()
except json.JSONDecodeError:
    st.error("Product database is not a valid JSON file.")
    st.stop()

agent = SioraAgent(products)

st.title("🛒 Siora – Your Smart Shopping Agent")

# Session to keep cart state between runs
if 'cart' not in st.session_state:
    st.session_state.cart = []
    st.session_state.total = 0
    st.session_state.not_found = []
    st.session_state.approved = False
    st.session_state.purchase_ready = False

user_input = st.text_input(
    "What do you need today?",
    placeholder="e.g. Buy atta and shampoo under 800"
)

if st.button("Ask Siora"):
    if user_input.strip():
        items, budget = agent.parse_request(user_input)
        cart, total, approved, not_found = agent.create_cart(items, budget)
        st.session_state.cart = cart
        st.session_state.total = total
        st.session_state.approved = approved
        st.session_state.not_found = not_found
        st.session_state.purchase_ready = approved and cart  # Only allow purchase if items found and approved
    else:
        st.warning("Please enter your shopping request.")

# Cart summary section
st.write("### 🛍️ Items in your cart:")
if st.session_state.cart:
    for item in st.session_state.cart:
        st.write(f"- {item['name']} – ₹{item['price']}")
    st.write(f"**Total: ₹{st.session_state.total}**")
else:
    st.info("No items found or added to cart.")

if st.session_state.not_found:
    st.warning(f"Could not find: {', '.join(st.session_state.not_found)}")

if st.session_state.purchase_ready:
    if st.button("Proceed to Pay with Visa"):
        st.success("💳 Paid with your Visa card! Your order is confirmed. 🎉")
        # Reset cart after purchase
        st.session_state.cart = []
        st.session_state.total = 0
        st.session_state.not_found = []
        st.session_state.approved = False
        st.session_state.purchase_ready = False
elif st.session_state.cart:
    if not st.session_state.approved:
        st.error("❌ Budget exceeded. Please revise your cart before purchase.")

