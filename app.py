# app.py
import streamlit as st
from fraudriskscore_final import fraudriskscore_final
import pandas as pd, datetime

st.title("Fraud Detection - Local smoke test")

st.sidebar.header("Quick test & health checks")

def smoke_check():
    sample = {"months_as_customer":12,"age":30,"policy_state":"CA",
              "policy_deductable":500,"policy_annual_premium":800.0,
              "incident_date":str(pd.Timestamp.today().date()),
              "incident_type":"Rear-End Collision","incident_severity":"Minor Damage",
              "incident_hour_of_the_day":14,"number_of_vehicles_involved":1,
              "property_damage":"NO","bodily_injuries":0,"witnesses":0,
              "police_report_available":"NO","total_claim_amount":1200.0,
              "claim_description":"Minor bumper scratch while parking."}
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
       "months_as_customer":1, "age":29, "policy_state":"FL",
       "policy_deductable":250,"policy_annual_premium":120.0,
       "incident_date":str(datetime.date.today()),
       "incident_type":"Theft","incident_severity":"Total Loss",
       "incident_hour_of_the_day":3,"number_of_vehicles_involved":0,
       "property_damage":"YES","bodily_injuries":0,"witnesses":0,
       "police_report_available":"YES","total_claim_amount":45000.0,
       "claim_description":"Bought car recently, stolen overnight; need payout fast."
    }
    try:
        r = fraudriskscore_final(high)
        st.write("Result:", r)
    except Exception as e:
        st.error("Error during prediction")
        st.write(str(e))
