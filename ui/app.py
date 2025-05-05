if st.button("Ask Siora"):
    items, budget = agent.parse_request(user_input)
    cart, total, approved = agent.create_cart(items, budget)

    if cart:
        st.write("### 🛍️ Items in your cart:")
        for item in cart:
            st.markdown(f"- **{item['name']}** – ₹{item['price']}")

        st.write(f"**🧾 Total: ₹{total}**")

        if approved:
            confirm = st.checkbox("✅ Confirm purchase with Visa card simulation")

            if confirm:
                st.success("🎉 Purchase confirmed! Siora used your Visa card successfully.")
            else:
                st.info("🕐 Waiting for your confirmation to proceed.")
        else:
            st.error("❌ Budget exceeded. Please revise your cart.")
    else:
        st.warning("🤖 No matching items found. Try mentioning atta, shampoo, etc.")
