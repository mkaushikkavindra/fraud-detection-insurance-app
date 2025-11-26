import streamlit as st

st.set_page_config(
    page_title="Fraud Detection System",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Fraud Detection System")
st.write("""
Welcome to the Fraud Detection Web App.  

Use the link below or the sidebar to access the Fraud Score Calculator.
""")

st.markdown("### 🔗 Navigation")
st.markdown("- 👉 [Go to Fraud Score Calculator](./score_calculator)")

st.info("Tip: You can also use the sidebar to navigate to the calculator page.")
