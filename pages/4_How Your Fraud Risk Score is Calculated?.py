import streamlit as st
import time

st.set_page_config(
    page_title="How Your Fraud Risk Score is Calculated?",
    layout="centered",
    initial_sidebar_state="collapsed" 
)

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.info("Logged out successfully. Returning to Login Page.")
    st.switch_page("Login.py")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Login to access the platform!!")
    time.sleep(2.5)
    st.switch_page("Login.py")

st.sidebar.markdown(
    f"<div style='font-weight: bold; font-size: 1.1em; ;margin-bottom: 10px;'>Welcome, {st.session_state.username}!</div>",
    unsafe_allow_html=True
)

st.sidebar.button("Logout", on_click=logout, key="sidebar_logout_btn")

st.title("How Your Fraud Risk Score is Calculated?")

#contents begin from here

st.markdown("""
This document provides transparency into the proprietary system used to calculate the Fraud Risk Score, ensuring users understand the robustness and intelligence behind every decision.""")

st.markdown("---")

st.markdown("""<h2><b>The Core Engine: An Ensemble Approach</b></h2>""", unsafe_allow_html=True)

st.markdown("""The Fraud Risk Score is generated not by a single model, but by a highly optimized Ensemble System comprising three distinct machine learning algorithms. 
This approach ensures maximum accuracy, reliability, and coverage against various fraud patterns.""")

st.markdown("""
<ol>

<li><b>Primary Decision Maker: Gradient Boosting Classifier (GBC)</b>
<ul> 
<li>Role: Highest Reliability and Loss Prevention. The GBC is the primary tool for daily operations.</li>
<li>Performance: It is tuned to provide the highest overall F1-Score, achieving the best balance between accurate detection (Recall) and minimizing false alarms (Precision). 
It provides the most robust and consistent risk assessment.</li>
</ul>
</li>

<li><b>The Safety Net: Random Forest Classifier (RFC)</b>
<ul> 
<li>Role: Maximized Fraud Detection (High Recall). The RFC acts as a safety net for complex or novel fraud.</li>
<li>Performance: It is specifically configured to be the most sensitive model. 
It's essential for catching unusual or sophisticated fraud that the primary GBC might overlook, ensuring the system pushes the boundary to prevent False Negatives (missed fraud cases).</li>
</ul>
</li>

<li><b>The Audit Baseline: Logistic Regression (LR)</b>
<ul> 
<li>Role: Conservative Validation and System Justification.</li>
<li>Performance: Serving as the simplest, most conservative model, the LR provides a vital baseline. 
Its scores demonstrate that simple, linear relationships alone are inadequate for modern fraud detection, 
thus justifying the complexity and superior performance of the Ensemble system.</li>
</ul>
</li>

</ol>
""", unsafe_allow_html=True)

st.markdown("---")
