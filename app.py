import streamlit as st

import os

st.write("Files in /pages folder:")
st.write(os.listdir("pages"))

st.set_page_config(
    page_title="Fraud Detection System",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Fraud Detection System")
st.write("Welcome to the Fraud Detection Web App.")

if st.button("Open Fraud Score Calculator"):
    st.switch_page("score_calculator")




