import streamlit as st
import time

st.set_page_config(page_title="Login Page", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

# --- Functions ---
def logout():
    """Logs out the user and reruns the script."""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.info("Logged out successfully.")
    st.rerun()

def login_form():
    st.title("🔑 Car Insurance Fraud Detection Login")
    st.markdown("Please sign in to access the analysis tool.")
    
    # Simple, hardcoded credentials. REPLACE THIS IN PRODUCTION!
    CREDENTIALS = {"user1": "pass123", "admin": "securepwd"}

    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password").strip()
        submitted = st.form_submit_button("Log In")

        if submitted:
            if username in CREDENTIALS and CREDENTIALS[username] == password:
                # Set session state on successful login
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}! Accessing secure app...")
                time.sleep(1) 
                st.rerun() # Rerun to trigger the secure app display
            else:
                st.error("❌ Invalid Username or Password")

# --- Main Application Flow ---
if st.session_state.logged_in:
    # 1. Add the logout button to the sidebar
    st.sidebar.button("Logout", on_click=logout)
    
    # 2. Call the main app function from the separate file
    #run_fraud_app()
else:
    # 3. Show the login form
    login_form()
