import streamlit as st
import time

st.set_page_config(page_title="Home", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None


def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.info("Logged out successfully. Please re-run the app to see the login screen.")
    # Streamlit will automatically revert to the login screen on the next rerun
    # if the user manually navigates away and back, or if st.stop() is hit.
    st.rerun() 

def check_login_status():
    if st.session_state.logged_in:
        return True
    else:
        # If not logged in, show the login form instead of the app content
        login_form()
        return False

# --- Login Form Function (The core of the security) ---

def login_form():
    st.title("🔑 Car Insurance Fraud Detection Login")
    st.markdown("Please sign in to access the analysis tool.")
    
    CREDENTIALS = {"user1": "pass123", "admin": "securepwd"} #to be replaced

    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password").strip()
        submitted = st.form_submit_button("Log In")

        if submitted:
            if username in CREDENTIALS and CREDENTIALS[username] == password:
                # Set session state on successful login
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}! Please **refresh the browser tab** or click 'Rerun' in Streamlit's corner to load the main app.")
                # We can't immediately load the secure app content because it's in a different file.
                # Telling the user to rerun is the clean way to switch contexts without the Multi-Page structure.
            else:
                st.error("❌ Invalid Username or Password")

# --- Main Logic for app.py (Redirects to secured_fraud_app.py) ---

if st.session_state.logged_in:
    # If the user is logged in, Streamlit should execute the secure app file.
    # In this non-multi-page structure, the user must manually navigate or re-run
    # after the initial login in app.py. 
    
    # To launch the secure app after a successful login in the same file:
    # Since we can't cleanly import and run a Streamlit file's body in the same folder 
    # without a specific mechanism (like the deprecated streamlit-app-runner), 
    # the **cleanest** method is to use Python's built-in `exec()` or simply 
    # instruct the user to refresh the page after successful login, which Streamlit handles gracefully.
    
    # For a smoother experience without asking the user to refresh, 
    # let's include the entire content of the secure app within the check here:
    
    try:
        # Load and execute the secure app content
        with open("fraudriskscoreAPP.py", "r") as f:
            code = f.read()
            # This executes the entire script, making its Streamlit calls.
            # This is generally discouraged in production for security, but solves your problem of avoiding indentation.
            exec(code, globals()) 
            
    except FileNotFoundError:
        st.error("Error: The secured application file (secured_fraud_app.py) was not found.")
    except Exception as e:
        st.error(f"Error loading secure application: {e}")

else:
    # If not logged in, show the login form
    login_form()
