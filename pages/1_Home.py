import streamlit as st

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.info("Logged out successfully. Returning to Login Page.")
    st.switch_page("Login.py")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Login to access the platform!!")
    time.sleep(2.5)
    st.switch_page("Login.py")

st.set_page_config(
    page_title="Home",
    layout="centered",
    initial_sidebar_state="collapsed" 
)

st.sidebar.markdown(
    f"<div style='font-weight: bold; font-size: 1.1em; margin-bottom: 10px;'>Welcome, {st.session_state.username}!</div>",
    unsafe_allow_html=True
)

st.sidebar.button("Logout", on_click=logout, key="sidebar_logout_btn")

st.title("Fraud Risk Score Calculator for Car Insurance")
st.markdown("---")

st.markdown("""
### Welcome to the Platform!
""")

st.markdown("This advanced platform is designed to provide immediate, data-driven risk assessment for car insurance claims.")

st.markdown("""
Our system leverages a robust **Ensemble Machine Learning Model** combined with **Natural Language Processing (NLP)** of claim descriptions to achieve industry-leading accuracy in identifying fraudulent activities.
""")

st.markdown("---")


st.markdown("""
## Key Features & Benefits
* **Real-time Scoring:** Get an instant **Fraud Risk Score** (0-100%) for any claim data input.
* **Text Analysis:** Identify suspicious language patterns in claim descriptions using integrated NLP features.
* **Data-Driven Decisions:** Receive a clear decision: **Approve Automatically** or **Manual Review Required** or **Flagged as Potential Fraud**.
""")

st.markdown("---")

##Get Started

st.markdown("""
To protect sensitive claim data, access to the Fraud Risk Score Calculator is restricted.
Please **Sign In** using the official login page available in the navigation menu on the left (once the sidebar is expanded):
""")

# Note: The sidebar is collapsed on initial load. We instruct the user to expand it.

st.info("Click the hamburger menu (☰) in the top-left corner, and select the 'Login' page to continue.")
