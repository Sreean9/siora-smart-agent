import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from agent.siora_core import SioraAgent

st.set_page_config(page_title="Siora Smart Shopper", page_icon="🛒")

st.title("🛍️ Meet Siora – Your Smart Shopping Assistant")

# Initialize the agent
agent = SioraAgent()

# Input box
user_input = st.text_input("What do you need to buy?", "")

# Trigger search
if st.button("Ask Siora"):
    if user_input.strip() == "":
        st.warning("Please type something, e.g., atta, shampoo, etc.")
    else:
        items = agent.get_items(user_input)

        if not items:
            st.warning("🤖 No matching items found. Try mentioning atta, shampoo, etc.")
        else:
            st.subheader("🛒 Items in your cart:")
            total = sum(item['price'] for item in items)
            for item in items:
                st.markdown(f"- **{item['name']}** – ₹{item['price']}")
            st.markdown(f"**Total: ₹{total}**")

            # Budget logic
            if total <= agent.budget:
                if st.checkbox("Confirm purchase?"):
                    st.success("✅ All items are within budget. Proceeding with your Visa card simulation!")
                else:
                    st.info("🕒 Waiting for confirmation to proceed.")
            else:
                st.error("🚫 Items exceed your budget. Please remove something.")
