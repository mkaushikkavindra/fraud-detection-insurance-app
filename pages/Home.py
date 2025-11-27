import streamlit as st

st.set_page_config(
    page_title="Welcome to the Fraud Detection App",
    layout="centered",
    initial_sidebar_state="collapsed" 
)

st.title("Car Insurance Fraud Detection Tool")
st.markdown("---")

st.markdown("""
### Welcome to the Platform!
""")

st.info("This advanced platform is designed to provide immediate, data-driven risk assessment for car insurance claims.")

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

st.markdown(
    f"""
    <div style='background-color: #ff4b4b; padding: 15px; border-radius: 8px; color: white; text-align: center; font-size: 1.2em; font-weight: bold;'>
        ➡️ Click the hamburger menu (☰) in the top-left corner, and select the 'login page' to continue.
    </div>
    """, 
    unsafe_allow_html=True
)
