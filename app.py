import streamlit as st

st.set_page_config(
    page_title="Fraud Detection System",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Fraud Detection System")
st.write("""
Welcome to the Fraud Detection Web App.

Use the sidebar to navigate:
- Fraud Risk Calculator
- Model Details
- Threshold Values
- About Page
""")

st.info("Open the sidebar to choose a page.")
