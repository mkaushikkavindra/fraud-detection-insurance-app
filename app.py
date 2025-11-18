# app.py
import streamlit as st
from fraudriskscore_final import fraudriskscore_final
import pandas as pd, datetime

st.title("Fraud Detection - Local smoke test")

st.sidebar.header("Quick test & health checks")

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

st.write("Press the button to run a high-fraud preset")
if st.button("Run high-fraud preset"):
    high = {
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
        r = fraudriskscore_final(high)
        st.write("Result:", r)
    except Exception as e:
        st.error("Error during prediction")
        st.write(str(e))






