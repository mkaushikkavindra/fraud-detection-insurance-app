# app.py
import streamlit as st
from fraudriskscore_final import fraudriskscore_final
import pandas as pd, datetime

st.title("Vehicle Insurance Fraud Detection")

def smoke_check():
    sample = {
    "months_as_customer": 48,
    "age": 35,
    "policy_number": "12345",
    "policy_bind_date": "2018-07-15",
    "policy_state": "CA",
    "policy_csl": "250/500",
    "policy_deductable": 1000,
    "policy_annual_premium": 1200.0,
    "umbrella_limit": 0,
    "insured_zip": 90001,
    "insured_sex": "MALE",
    "insured_education_level": "College",
    "insured_occupation": "Engineer",
    "insured_hobbies": "reading",
    "insured_relationship": "husband",
    "capital-gains": 0,
    "capital-loss": 0,
    "incident_date": "2023-02-10",
    "incident_type": "Rear-End Collision",
    "collision_type": "Rear Collision",
    "incident_severity": "Major Damage",
    "authorities_contacted": "Police",
    "incident_state": "CA",
    "incident_city": "Los Angeles",
    "incident_location": "Main Street",
    "incident_hour_of_the_day": 14,
    "number_of_vehicles_involved": 2,
    "property_damage": "YES",
    "bodily_injuries": 1,
    "witnesses": 1,
    "police_report_available": "YES",
    "total_claim_amount": 15000,
    "injury_claim": 5000,
    "property_claim": 8000,
    "vehicle_claim": 2000,
    "auto_make": "Honda",
    "auto_model": "Civic",
    "auto_year": 2019,
    "claim_to_premium_ratio": 12.5,
    "injury_ratio": 0.33,
    "property_ratio": 0.53,
    "vehicle_ratio": 0.14,
    "daysdiff": 9000,
    "police_report_flag": 1,
    "property_damage_flag": 1,
    "authorities_contacted_flag": 1,
    "injury_flag": 1,
    "multiple_vehicles_flag": 1,
    "claim_description": "Rear-end collision while stopped at a red light. Airbag deployed. Claimant reported neck pain."
}
    try:
        out = fraudriskscore_final(sample)
        return True, out
    except Exception as e:
        return False, str(e)

ok, info = smoke_check()
if ok:
    st.sidebar.success("Model loaded & runnable")
    st.sidebar.json(info)
else:
    st.sidebar.error("Model load/predict failed")
    st.sidebar.write(info)

st.header("Submit a New Claim for Analysis")
st.write("Enter the required details to get a FRAUD RISK SCORE.")

with st.form(key="claim_values"):
    # --- Helper lists for selectboxes ---
    yes_no_options = ["NO", "YES"]
    state_options = ["CA", "WA", "AZ", "NV", "OR", "TX", "FL", "NY", "IL", "PA", "OH", "IN"]
    csl_options = ["100/300", "250/500", "500/1000", "1000/2000"]
    sex_options = ["MALE", "FEMALE", "OTHER"]
    education_options = ["Associate", "College", "High School", "JD", "MD", "Masters", "PhD"]
    severity_options = ["Major Damage", "Minor Damage", "Total Loss", "Trivial"]
    authorities_options = ["Police", "Fire", "Ambulance", "Other", "None"]
    incident_type_options = ["Single Vehicle Collision", "Multi-vehicle Collision", "Parked Car", "Rear-End Collision", "Side Collision"]
    
    # --- Form Layout ---
    st.subheader("1. Policy & Insured Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        policy_number = st.text_input("Policy Number *", "12345")
        policy_state = st.selectbox("Policy State *", state_options)
        policy_csl = st.selectbox("Policy CSL *", csl_options)
        policy_bind_date = st.date_input("Policy Bind Date *", datetime.date(2018, 7, 15))
    
    with col2:
        months_as_customer = st.number_input("Months as Customer *", min_value=0, value=48)
        age = st.number_input("Insured Age *", min_value=16, max_value=100, value=35)
        insured_sex = st.selectbox("Insured Sex *", sex_options)
        insured_education_level = st.selectbox("Insured Education *", education_options, index=1)

    with col3:
        policy_deductable = st.number_input("Policy Deductible *", min_value=0, step=100, value=1000)
        policy_annual_premium = st.number_input("Annual Premium *", min_value=0.0, format="%.2f", value=1200.0)
        umbrella_limit = st.number_input("Umbrella Limit", min_value=0, step=100000, value=0)
        insured_zip = st.text_input("Insured Zip Code *", "90001") # Text input for zips

    st.subheader("2. Insured's Profile & Financials")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        insured_occupation = st.text_input("Insured Occupation", "Engineer")
        insured_hobbies = st.text_input("Insured Hobbies", "reading")
        insured_relationship = st.text_input("Insured Relationship", "husband")
    with col2:
        capital_gains = st.number_input("Capital Gains", format="%.2f", value=0.0)
    with col3:
        capital_loss = st.number_input("Capital Loss", format="%.2f", value=0.0)


    st.subheader("3. Incident & Claim Details")
    col1, col2, col3 = st.columns(3)

    with col1:
        incident_date = st.date_input("Incident Date *", datetime.date(2023, 2, 10))
        incident_type = st.selectbox("Incident Type *", incident_type_options, index=3)
        collision_type = st.selectbox("Collision Type *", ["Rear Collision", "Side Collision", "Front Collision", "?"], index=0)
        incident_severity = st.selectbox("Incident Severity *", severity_options, index=0)

    with col2:
        incident_state = st.selectbox("Incident State *", state_options)
        incident_city = st.text_input("Incident City", "Los Angeles")
        incident_location = st.text_input("Incident Location (Street)", "Main Street")
        incident_hour_of_the_day = st.number_input("Incident Hour (0-23) *", min_value=0, max_value=23, value=14)

    with col3:
        authorities_contacted = st.selectbox("Authorities Contacted", authorities_options)
        number_of_vehicles_involved = st.number_input("Vehicles Involved *", min_value=1, value=2)
        property_damage = st.selectbox("Property Damage? *", yes_no_options, index=1)
        police_report_available = st.selectbox("Police Report Available? *", yes_no_options, index=1)


    st.subheader("4. Injuries & Financials")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        bodily_injuries = st.number_input("Bodily Injuries (count) *", min_value=0, value=1)
        witnesses = st.number_input("Witnesses (count) *", min_value=0, value=1)
    with col2:
        total_claim_amount = st.number_input("Total Claim Amount *", min_value=0.0, format="%.2f", value=15000.0)
    with col3:
        injury_claim = st.number_input("Injury Claim Amount *", min_value=0.0, format="%.2f", value=5000.0)
    with col4:
        property_claim = st.number_input("Property Claim Amount *", min_value=0.0, format="%.2f", value=8000.0)
        vehicle_claim = st.number_input("Vehicle Claim Amount *", min_value=0.0, format="%.2f", value=2000.0)

    st.subheader("5. Vehicle & Description")
    col1, col2, col3 = st.columns(3)
    with col1:
        auto_make = st.text_input("Auto Make", "Honda")
    with col2:
        auto_model = st.text_input("Auto Model", "Civic")
    with col3:
        auto_year = st.number_input("Auto Year", min_value=1950, max_value=datetime.date.today().year + 1, value=2019)

    claim_description = st.text_area("Claim Description *", "Rear-end collision while stopped at a red light. Airbag deployed. Claimant reported neck pain.")
    
    # --- Submit Button ---
    submitted = st.form_submit_button("Analyze Claim for Fraud")
















