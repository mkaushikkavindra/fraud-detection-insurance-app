import streamlit as st
import time

st.set_page_config(
    page_title="User Guide & Protocol",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("User Guide")

st.markdown("""
This guide provides step-by-step instructions for utilizing the **Car Insurance Fraud Detection Platform** to submit claims and interpret the results.
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
        <li></b>Single Claim Entry:</b> For processing the details of only one claim at a time via a detailed web form.</li>
    </ul>
</li>
<li>Select the input mode you wish to use.</li>
</ol>
""", unsafe_allow_html=True)

st.markdown("---")


st.markdown("""
<ol start="6">
<li>For **Batch File Upload**, locate the upload box and select the CSV file you want to analyze.</li>
<li>The model will process all claims and display the results table.</li>
<li>The final results will include **four new columns** added to your original data:
    <ul>
        <li>**"Fraud Risk Score (%)"**: The overall probability of fraud (0-100%).</li>
        <li>**"Risk Level"**: Categorical risk assessment (e.g., High, Medium, Low).</li>
        <li>**"Decision"**: Recommended action (**Investigate** or **Approve**).</li>
        <li>**"Text Suspicion Score (%)"**: The score generated from the claim description text analysis.</li>
    </ul>
</li>
<li>Click on **"Download The Results as CSV"** to save the complete analyzed file to your system.</li>
</ol>
""", unsafe_allow_html=True)

st.markdown("---")


st.markdown("""
<ol start="10">
<li>For **Single Claim Entry**, carefully enter all required details into the form provided.</li>
<li>Click on **"Analyze Claim for Fraud"**.</li>
<li>The final results—**Decision, Fraud Risk Score, Risk Level, and Text Suspicion Score**—will be prominently displayed below the form.</li>
</ol>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<ol start="13">
<li>For logging out, click the **"Logout"** button located at the **top of the sidebar**, just below your welcome message.</li>
<li>**For enhanced safety,** you will be automatically logged out and redirected to the login page once you close the browser tab or navigate away from the application.</li>
</ol>
""")
