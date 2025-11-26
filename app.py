import streamlit as st
import time

# --- Configuration & State Initialization ---
st.set_page_config(
    page_title="Secure Fraud App Login", 
    layout="centered",
    initial_sidebar_state="expanded" # Hides the sidebar on the login page
)

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

# --- Functions ---

def login_form():
    """Displays the login form and handles authentication."""
    
    # Simple, hardcoded credentials. 
    # CONSIDER USING STREAMLIT SECRETS/ENVIRONMENT VARIABLES FOR PRODUCTION!
    CREDENTIALS = {"user1": "pass123", "admin": "securepwd"}
    
    st.title("🔑 Car Insurance Fraud Detection Login")
    st.markdown("Please sign in to access the secure analysis tool.")

    with st.form("login_form", clear_on_submit=True):
        st.subheader("Enter Credentials")
        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password").strip()
        submitted = st.form_submit_button("Log In")

        if submitted:
            if username in CREDENTIALS and CREDENTIALS[username] == password:
                # Set session state on successful login
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}! Access granted.")
                time.sleep(0.5)
                # Force a rerun to reload the app, making the secure page visible in the sidebar
                st.session_state.page = "score_page"  # New session state to manage page navigation
                st.rerun() 
            else:
                st.error("❌ Invalid Username or Password")

# --- Main Logic (The Login Gate) ---

if st.session_state.logged_in:
    # If logged in, greet the user and instruct them to navigate
    st.title(f"🚀 Welcome Back, {st.session_state.username}!")
    st.markdown("You are logged in. Select **Fraud App** from the sidebar to access the analysis tools.")
    
    # Provide a logout button on the landing page
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.info("Logged out successfully.")
        st.rerun()

else:
    # If not logged in, show the login form
    login_form()
