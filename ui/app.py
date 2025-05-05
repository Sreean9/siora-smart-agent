import sys
import os
import json
import streamlit as st
import re
import traceback

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

# Function to create sample products if no database exists (for testing)
def create_sample_products():
    return [
        {"name": "Atta", "price": 45, "category": "Groceries"},
        {"name": "Sugar", "price": 40, "category": "Groceries"},
        {"name": "Rice", "price": 60, "category": "Groceries"},
        {"name": "Dal", "price": 120, "category": "Groceries"},
        {"name": "Milk", "price": 25, "category": "Dairy"},
        {"name": "Bread", "price": 30, "category": "Bakery"},
        {"name": "Eggs", "price": 60, "category": "Dairy"},
        {"name": "Salt", "price": 20, "category": "Groceries"},
        {"name": "Oil", "price": 120, "category": "Groceries"}
    ]

# Try to load products, or use sample data if not available
try:
    products = load_products()
except Exception as e:
    st.warning(f"Using sample product data due to: {str(e)}")
    products = create_sample_products()

# Create the agent with the products
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

# Initialize session state variables individually
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'total' not in st.session_state:
    st.session_state.total = 0
if 'not_found' not in st.session_state:
    st.session_state.not_found = []
if 'approved' not in st.session_state:
    st.session_state.approved = False
if 'purchase_ready' not in st.session_state:
    st.session_state.purchase_ready = False
if 'error' not in st.session_state:
    st.session_state.error = None
if 'success_message' not in st.session_state:
    st.session_state.success_message = None
if 'budget' not in st.session_state:
    st.session_state.budget = None
if 'debug_info' not in st.session_state:
    st.session_state.debug_info = {}

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
    st.session_state.budget = None

# Process user input
if st.button("Ask Siora"):
    if user_input.strip():
        try:
            # Reset any previous error
            st.session_state.error = None
            
            # Parse the request
            try:
                items, quantities, budget = agent.parse_request(user_input)
                
                # Store budget in session state
                st.session_state.budget = budget
                
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
                    st.session_state.purchase_ready = approved and bool(cart)  # Ensure it's a boolean
                    
                    # Debug information
                    st.session_state.debug_info = {
                        "parsed_items": items,
                        "quantities": quantities,
                        "budget": budget
                    }
            except ValueError as ve:
                st.session_state.error = f"Error processing your request: {str(ve)}"
            except Exception as e:
                st.session_state.error = f"An unexpected error occurred: {str(e)}"
                st.session_state.debug_info = {"error_trace": traceback.format_exc()}
        except Exception as outer_e:
            st.session_state.error = f"System error: {str(outer_e)}"
            st.session_state.debug_info = {"outer_error_trace": traceback.format_exc()}
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
            
        if not st.session_state.approved and st.session_state.budget is not None:
            st.error(f"❌ Budget exceeded (₹{st.session_state.budget}). Please revise your cart before purchase.")
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
            st.experimental_rerun()
    
    # Add a clear cart button
    if st.session_state.cart:
        if st.button("Clear Cart", key="clear_cart"):
            reset_cart()
            st.session_state.success_message = "Cart has been cleared!"
            st.experimental_rerun()
    
    # Add a simple help section
    st.write("### Need Help?")
    st.write("Try saying: 'buy rice 2kg and dal 1kg under 500'")

# Debug section (always show when there's an error)
show_debug = st.checkbox("Show Debug Info", value=st.session_state.error is not None)
if show_debug:
    st.write("### Debug Information")
    st.write("### Session State")
    debug_state = {k: v for k, v in st.session_state.items() if k != 'cart'}
    st.json(debug_state)
    if st.session_state.cart:
        st.write("### Cart Details")
        st.json(st.session_state.cart)
