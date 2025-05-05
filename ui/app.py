import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.siora_core import SioraAgent


# Load product database
with open("data/products.json", "r") as f:
    products = json.load(f)

# Initialize the agent
agent = SioraAgent(products)

st.title("🛒 Siora – Your Smart Shopping Agent")

# User input
user_input = st.text_input("What do you need today?", placeholder="e.g. Buy atta and shampoo under 800")

if st.button("Ask Siora"):
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
