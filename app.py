import streamlit as st
import time

# --- Configuration & State Initialization ---
st.set_page_config(
    page_title="Secure Fraud App Login", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None


# --- Functions ---
def login_form():

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

                st.session_state.logged_in = True
                st.session_state.username = username

                st.success(f"Welcome, {username}! Redirecting...")
                time.sleep(0.5)

                # 🔥 AUTO-REDIRECT to score_page
                st.experimental_set_query_params(page="score_page")
                st.rerun()

            else:
                st.error("❌ Invalid Username or Password")


# --- Main Logic ---
if st.session_state.logged_in:

    # If URL already has the correct page, do nothing
    params = st.experimental_get_query_params()
    if params.get("page") != ["score_page"]:
        # Redirect only when needed
        st.experimental_set_query_params(page="score_page")
        st.rerun()

    # Fallback message (will rarely be seen)
    st.title("Redirecting…")

else:
    login_form()
