import sys
import os
import json
import streamlit as st
import re

# Add parent directory to path for custom imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.siora_core import SioraAgent

PRODUCTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'products.json'))

# Function to load products with error handling
def load_products():
    try:
        with open(PRODUCTS_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Product database not found at {PRODUCTS_PATH}")
        st.stop()
    except json.JSONDecodeError:
        st.error("Product database is not a valid JSON file.")
        st.stop()

# Load products and initialize agent
products = load_products()
agent = SioraAgent(products)

# Set page configuration
st.set_page_config(
    page_title="Siora - Smart Shopping Agent",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Siora – Your Smart Shopping Agent")

# Information about how to use the app
with st.expander("ℹ️ How to use Siora"):
    st.write("""
    - Type your shopping list like: "buy rice 2kg and sugar 1kg"
    - Add a budget: "buy milk, bread, and eggs under 500"
    - Specify quantities: "2kg rice, 1L milk, 5 apples"
    - Review your cart and proceed to checkout
    """)

# Initialize session state
if 'cart' not in st.session_state:
    st.session_state.cart = []
    st.session_state.total = 0
    st.session_state.not_found = []
    st.session_state.approved = False
    st.session_state.purchase_ready = False
    st.session_state.error = None
    st.session_state.success_message = None

# User input
user_input = st.text_input(
    "What do you need today?",
    placeholder="e.g. Buy atta 5kg and sugar 2kg under 800"
)

# Function to reset cart
def reset_cart():
    st.session_state.cart = []
    st.session_state.total = 0
    st.session_state.not_found = []
    st.session_state.approved = False
    st.session_state.purchase_ready = False
    st.session_state.error = None
    st.session_state.success_message = None

# Process user input
if st.button("Ask Siora"):
    if user_input.strip():
        try:
            # Reset any previous error
            st.session_state.error = None
            
            # Parse the request
            items, quantities, budget = agent.parse_request(user_input)
            
            if not items:
                st.session_state.error = "I couldn't understand your request. Please try again with a clearer shopping list."
            else:
                # Create the cart
                cart, total, approved, not_found = agent.create_cart(items, quantities, budget)
                
                # Update session state
                st.session_state.cart = cart
                st.session_state.total = total
                st.session_state.approved = approved
                st.session_state.not_found = not_found
                st.session_state.purchase_ready = approved and cart
                
                # Debug information
                st.session_state.debug_info = {
                    "parsed_items": items,
                    "quantities": quantities,
                    "budget": budget
                }
        except Exception as e:
            st.session_state.error = f"An error occurred: {str(e)}"
    else:
        st.session_state.error = "Please enter your shopping request."

# Display any errors
if st.session_state.error:
    st.error(st.session_state.error)

# Display success message if any
if st.session_state.success_message:
    st.success(st.session_state.success_message)
    # Clear success message after displaying
    st.session_state.success_message = None

# Create two columns for cart and actions
col1, col2 = st.columns([2, 1])

# Cart summary section
with col1:
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
            
        if not st.session_state.approved and budget is not None:
            st.error(f"❌ Budget exceeded (₹{budget}). Please revise your cart before purchase.")
    else:
        st.info("No items found or added to cart.")

# Actions section
with col2:
    st.write("### Actions")
    
    # Only show the payment button if purchase is ready
    if st.session_state.purchase_ready:
        if st.button("Proceed to Pay with Visa", key="pay_button"):
            st.session_state.success_message = "💳 Paid with your Visa card! Your order is confirmed. 🎉"
            reset_cart()
            st.rerun()
    
    # Add a clear cart button
    if st.session_state.cart:
        if st.button("Clear Cart", key="clear_cart"):
            reset_cart()
            st.session_state.success_message = "Cart has been cleared!"
            st.rerun()
    
    # Add a simple help section
    st.write("### Need Help?")
    st.write("Try saying: 'buy rice 2kg and dal 1kg under 500'")

# Debug section (only in development)
if st.checkbox("Show Debug Info", value=False):
    st.write("### Debug Information")
    if hasattr(st.session_state, 'debug_info'):
        st.json(st.session_state.debug_info)
    st.write("### Session State")
    st.write({k: v for k, v in st.session_state.items() if k != 'cart'})
    if st.session_state.cart:
        st.write("### Cart Details")
        st.json(st.session_state.cart)
