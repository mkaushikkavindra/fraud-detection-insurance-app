import streamlit as st
import time

def inject_custom_css():
    st.markdown("""
        <style>
            /* 1. Main Background */
            .stApp {
                background-color: #f0f2f6; /* Light gray background */
            }

            /* 2. Primary Header Text */
            h1 {
                color: #0b2e53; /* Dark Navy for titles */
                border-bottom: 2px solid #ff4b4b; /* Red accent underline */
                padding-bottom: 10px;
                margin-bottom: 20px;
            }

            /* 3. Subheaders */
            h2, h3 {
                color: #0b2e53;
            }

            /* 4. Sidebar Styles (score_page.py only) */
            .st-emotion-cache-1lc5d3g, .st-emotion-cache-1lc5d3g .st-emotion-cache-zt5ig8 {
                background-color: #0b2e53; /* Dark Navy background */
            }
            .st-emotion-cache-1lc5d3g .st-emotion-cache-10trblm {
                color: white; /* White text for sidebar header */
            }
            .st-emotion-cache-1lc5d3g .stButton > button {
                background-color: #ff4b4b; /* Red button for Logout */
                color: white;
                border-radius: 5px;
                border: none;
            }
            .st-emotion-cache-1lc5d3g .stButton > button:hover {
                background-color: #e63946;
            }

            /* 5. Form/Input Styling (Make them boxy/professional) */
            .stTextInput > div > div > input,
            .stDateInput > div > div > input,
            .stTextArea > textarea,
            .stSelectbox > div > div {
                border-radius: 8px; /* Slightly rounded corners */
                border: 1px solid #ccc; /* Lighter border */
                box-shadow: 1px 1px 5px rgba(0,0,0,0.05); /* Subtle shadow */
            }

            /* 6. Metrics/Cards (score_page.py results) */
            .st-emotion-cache-16idsys p {
                font-size: 1.1em; /* Make metric labels slightly larger */
                color: #4a4a4a;
            }
            [data-testid="stMetricValue"] {
                font-size: 2.2rem;
                color: #0b2e53; /* Dark value text */
            }

            /* 7. Success/Error Messages */
            .stAlert.success {
                background-color: #e6ffe6;
                color: #008000;
                border-left: 5px solid #008000;
            }
            .stAlert.error {
                background-color: #ffe6e6;
                color: #ff0000;
                border-left: 5px solid #ff0000;
            }

            /* 8. Radio Buttons/Tabs */
            [data-testid="stRadio"] label {
                background-color: #e0e0e0;
                padding: 8px 15px;
                border-radius: 5px;
                margin: 2px;
                font-weight: bold;
                transition: background-color 0.2s;
            }
            [data-testid="stRadio"] label:has(input:checked) {
                background-color: #ff4b4b; /* Red selected background */
                color: white;
            }


        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

st.set_page_config(
    page_title="Secure Fraud App Login",
    layout="centered",
    initial_sidebar_state="collapsed"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None


def login_form():
    CREDENTIALS = {"user1": "pass123", "admin": "securepwd"}

    st.title("🔑 Car Insurance Fraud Detection Login")
    st.markdown("Please sign in to access the secure analysis tool.")

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

                # 🚀 AUTO-REDIRECT to score_page.py
                st.switch_page("pages/score_page.py")

            else:
                st.error("❌ Invalid Username or Password")


# ---------- MAIN ----------
if not st.session_state.logged_in:
    login_form()
else:
    # If someone directly hits app.py after login
    st.switch_page("pages/score_page.py")
