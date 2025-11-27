import streamlit as st
import time

st.set_page_config(
    page_title="User Guide",
    layout="centered",
    initial_sidebar_state="expanded"
)

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.info("Logged out successfully. Returning to Login Page.")
    st.switch_page("Login.py")

st.sidebar.markdown(
    f"<div style='font-weight: bold; font-size: 1.1em; ;margin-bottom: 10px;'>Welcome, {st.session_state.username}!</div>",
    unsafe_allow_html=True
)

st.sidebar.button("Logout", on_click=logout, key="sidebar_logout_btn")

st.title("User Guide")

st.markdown("""
This guide provides step-by-step instructions for utilizing the **Fraud Risk Score Calculator for Car Insurance** to submit claims and interpret the results.
""")

st.markdown("---")


st.markdown("""
<ol>
<li>Navigate to the <b>Login Page</b> from the sidebar navigation menu.</li>
<li>Enter your registered credentials and click <b>"Log In."</b></li>
<li>Upon successful login, the <b>"Fraud Risk Score Calculator for Car Insurance"</b> will open automatically.</li>
</ol>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
The application offers two primary methods for submitting claim details for fraud risk analysis:

<ol start="4">
<li>Review the available input methods at the top of the calculator page:
    <ul>
        <li><b>Batch File Upload:</b> For processing one or more (multiple) claims contained in a single CSV file.</li>
        <li><b>Single Claim Entry:</b> For processing the details of only one claim at a time via a detailed web form.</li>
    </ul>
</li>
<li>Select the input mode you wish to use.</li>
</ol>
""", unsafe_allow_html=True)

st.markdown("---")


st.markdown("""
<ol start="6">
<li>For <b>Batch File Upload,</b>, locate the upload box and select the CSV file you want to analyze.</li>
<li>The model will process all claims and display the results table.</li>
<li>The final results will include <b>four new columns</b> added to your original data:
    <ul>
        <li><b>"Fraud Risk Score (%)"</b>: The overall probability of fraud (0-100%).</li>
        <li><b>"Risk Level"</b>: Categorical risk assessment (e.g., High, Medium, Low).</li>
        <li><b>"Decision"</b>: Recommended action (**Investigate** or **Approve**).</li>
        <li><b>"Text Suspicion Score (%)"</b>: The score generated from the claim description text analysis.</li>
    </ul>
</li>
<li>Click on <b>"Download The Results as CSV"</b> to save the complete analyzed file to your system.</li>
</ol>
""", unsafe_allow_html=True)

st.markdown("---")


st.markdown("""
<ol start="10">
<li>For <b>Single Claim Entry</b>, carefully enter all required details into the form provided.</li>
<li>Click on <b>"Analyze Claim for Fraud"</b>.</li>
<li>The final results—<b>Decision, Fraud Risk Score, Risk Level, and Text Suspicion Score</b>—will be prominently displayed below the form.</li>
</ol>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<ol start="13">
<li>For logging out, click the <b>"Logout"</b> button located at the <b>top of the sidebar</b>, just below your welcome message.</li>
<li><b>For enhanced safety</b>, you will be automatically logged out and redirected to the login page once you close the browser tab or navigate away from the application.</li>
</ol>
""", unsafe_allow_html=True)
