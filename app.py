import streamlit as st
import time

# --- Configuration & State Initialization ---
st.set_page_config(
    page_title="Secure Fraud App Login", 
    layout="wide",
    initial_sidebar_state="collapsed" # Hide the sidebar on the login page
)

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

# --- Functions ---

def login_form():
    """Displays the login form and handles authentication."""
    
    # Simple, hardcoded credentials. REPLACE THIS IN PRODUCTION!
    CREDENTIALS = {"user1": "pass123", "admin": "securepwd"}
    
    st.title("🔑 Car Insurance Fraud Detection Login")
    st.markdown("Please sign in to access the analysis tool.")

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
                st.success(f"Welcome, {username}! Redirecting to the secured app...")
                time.sleep(0.5)
                # st.rerun() is essential to force Streamlit to refresh the UI 
                # and show the now-available "Secure App" link in the sidebar.
                st.rerun() 
            else:
                st.error("❌ Invalid Username or Password")

def logout_button():
    """Renders a logout button."""
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.info("Logged out successfully.")
        st.rerun()

# --- Main Logic ---

if st.session_state.logged_in:
    # If logged in, display the landing message and the logout button (which will appear on the secured page too)
    st.title(f"Welcome to the Secure Portal, {st.session_state.username}!")
    st.write("You are logged in. Please select **Fraud App** from the sidebar to start your analysis.")
    # Show logout in the main area of the landing page as a courtesy
    if st.button("Logout"):
        logout_button() 
else:
    # If not logged in, show the login form
    login_form()
