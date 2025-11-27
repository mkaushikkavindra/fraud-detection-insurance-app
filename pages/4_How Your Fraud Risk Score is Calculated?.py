import streamlit as st

st.set_page_config(
    page_title="How Your Fraud Risk Score is Calculated?",
    layout="centered",
    initial_sidebar_state="collapsed" 
)

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.info("Logged out successfully. Returning to Login Page.")
    st.switch_page("Login.py")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Login to access the platform!!")
    time.sleep(2.5)
    st.switch_page("Login.py")

st.sidebar.markdown(
    f"<div style='font-weight: bold; font-size: 1.1em; ;margin-bottom: 10px;'>Welcome, {st.session_state.username}!</div>",
    unsafe_allow_html=True
)

st.sidebar.button("Logout", on_click=logout, key="sidebar_logout_btn")

st.title("How Your Fraud Risk Score is Calculated?")
