import sys
import os
import json
import streamlit as st
import traceback

# Add parent directory to path for custom imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.siora_core import SioraAgent

# Sample products for testing
sample_products = [
    {"name": "Rice", "price": 60, "category": "Groceries"},
    {"name": "Milk", "price": 25, "category": "Dairy"},
    {"name": "Apples", "price": 15, "category": "Fruits"},
    {"name": "Atta", "price": 45, "category": "Groceries"},
    {"name": "Sugar", "price": 40, "category": "Groceries"},
    {"name": "Dal", "price": 120, "category": "Groceries"},
    {"name": "Bread", "price": 30, "category": "Bakery"},
    {"name": "Eggs", "price": 60, "category": "Dairy"},
    {"name": "Salt", "price": 20, "category": "Groceries"},
    {"name": "Oil", "price": 120, "category": "Groceries"}
]

# Create the agent with sample products
agent = SioraAgent(sample_products)

# Set page configuration
st.set_page_config(
    page_title="Siora - Smart Shopping Agent",
    page_icon="🛒"
)

st.title("🛒 Siora – Your Smart Shopping Agent")

# Initialize session state
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'total' not in st.session_state:
    st.session_state.total = 0
if 'not_found' not in st.session_state:
    st.session_state.not_found = []
if 'approved' not in st.session_state:
    st.session_state.approved = False
if 'error' not in st.session_state:
    st.session_state.error = None

# User input
user_input = st.text_input(
    "What do you need today?",
    placeholder="e.g. 2kg rice, 1L milk, 5 apples"
)

# Process user input
if st.button("Ask Siora"):
    if user_input.strip():
        try:
            # Reset error
            st.session_state.error = None
            
            # Parse request
            items, quantities, budget = agent.parse_request(user_input)
            
            # Create cart
            cart, total, approved, not_found = agent.create_cart(items, quantities, budget)
            
            # Update session state
            st.session_state.cart = cart
            st.session_state.total = total
            st.session_state.approved = approved
            st.session_state.not_found = not_found
            
        except Exception as e:
            st.session_state.error = f"Error processing your request: {str(e)}"
            st.write(f"Debug: {traceback.format_exc()}")
    else:
        st.session_state.error = "Please enter your shopping request."

# Display any errors
if st.session_state.error:
    st.error(st.session_state.error)

# Cart summary section
st.write("### 🛍️ Items in your cart:")
if st.session_state.cart:
    for item in st.session_state.cart:
        quantity_str = ""
        if 'quantity' in item and item['quantity'] > 0:
            quantity_str = f"{item['quantity']} {item['unit']} of " if item['unit'] else f"{item['quantity']} "
        
        price_str = f"₹{item['price']} per unit"
        if 'total_price' in item and item['total_price'] != item['price']:
            price_str = f"₹{item['price']} each (Total: ₹{item['total_price']})"
        
        st.write(f"- {quantity_str}{item['name']} – {price_str}")
        
    st.write(f"**Total: ₹{st.session_state.total:.2f}**")
    
    if st.session_state.not_found:
        st.warning(f"Could not find: {', '.join(st.session_state.not_found)}")
else:
    st.info("No items found or added to cart.")
