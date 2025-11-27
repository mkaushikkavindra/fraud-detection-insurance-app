import streamlit as st
import time

st.set_page_config(
    page_title="Login",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,   
        'Report a Bug': None,  
        'About': None,   
    }
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None


def login_form():
    CREDENTIALS = {"user1": "pass123", "admin": "securepwd"}

    st.title("Fraud Risk Score Calculator for Car Insurance")
    st.markdown("Please sign in to access the platform")

    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password").strip()
        submitted = st.form_submit_button("Log In")

        if submitted:
            if username in CREDENTIALS and CREDENTIALS[username] == password:

                st.session_state.logged_in = True
                st.session_state.username = username

                st.success(f"Welcome, {username}! Redirecting...")
                time.sleep(0.3)

                st.switch_page("pages/1_Home.py")

            else:
                st.error("Invalid Username or Password, Try Again!")


# ---------- MAIN ----------
if not st.session_state.logged_in:
    login_form()
else:
    # If someone directly hits app.py after login
    st.switch_page("pages/2_Fraud Risk Score Calculator.py")
    st.warning("You are already logged in!")
