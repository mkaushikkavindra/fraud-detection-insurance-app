# fraudriskscore_final.py
import joblib, re, numpy as np, pandas as pd
from sentence_transformers import SentenceTransformer

# ----- load models (will raise on import if missing) -----
final_model = joblib.load("fraud_detection_model.joblib")
text_model = joblib.load("text_model.joblib")
gbc_model = joblib.load("gbcmodel.joblib")
lr_model = joblib.load("logisticregression.joblib")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

NUMERIC_COLS = [
    'months_as_customer', 'age', 'policy_deductable', 'policy_annual_premium', 
    'umbrella_limit', 'capital-gains', 'capital-loss', 'incident_hour_of_the_day', 
    'number_of_vehicles_involved', 'bodily_injuries', 'witnesses', 
    'total_claim_amount', 'injury_claim', 'property_claim', 'vehicle_claim', 
    'auto_year', 'text_suspicion_score','policy_number'
]

CATEGORICAL_COLS = [
    'policy_bind_date', 'policy_state', 'policy_csl', 'insured_sex', 
    'insured_education_level', 'insured_occupation', 'insured_hobbies', 
    'insured_relationship', 'incident_date', 'incident_type', 'collision_type', 
    'incident_severity', 'authorities_contacted', 'incident_state', 
    'incident_city', 'property_damage', 'police_report_available', 
    'auto_make', 'auto_model'
]

# threshold (optional)
try:
    with open("finalthresholdvalue.txt") as f:
        GLOBAL_THRESHOLD = float(f.read().strip())
except:
    GLOBAL_THRESHOLD = 0.3

# small debug flag (switch to True to print df/dtypes into logs)
_DEBUG = False

def clean_text(t):
    if t is None: 
        return ""
    s = re.sub(r"[^a-zA-Z0-9\s\.]", " ", str(t))
    s = " ".join(s.split()).strip().lower()
    return s

def _build_input_df(claim: dict) -> pd.DataFrame:
    # Build dataframe from dict
    df = pd.DataFrame([claim])

    # Ensure text_suspicion_score exists (it's in our NUMERIC_COLS list)
    if "text_suspicion_score" not in df.columns:
        df["text_suspicion_score"] = np.nan

    # Get the feature list the model *actually* expects
    try:
        expected_features = list(final_model.feature_names_in_)
    except Exception:
        # Fallback if .feature_names_in_ is not available
        expected_features = [c for c in (NUMERIC_COLS + CATEGORICAL_COLS) if c in df.columns]

    # Ensure all expected columns are present and add missing ones
    for c in expected_features:
        if c not in df.columns:
            df[c] = np.nan
    
    # Filter dataframe to *only* the expected features
    df = df[expected_features]

    # --- NEW EXPLICIT TYPE CONVERSION & IMPUTATION ---
    # Loop through all columns the model expects
    for c in df.columns:
        if c in NUMERIC_COLS:
            # This column MUST be numeric. Coerce and fill with 0.
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        elif c in CATEGORICAL_COLS:
            # This column MUST be categorical (string). Fill with "Unknown"
            df[c] = df[c].fillna("Unknown").astype(str)
        else:
            # This is a column the model expects but we don't have a type for.
            # (This shouldn't happen if the lists are correct, but it's a safe fallback)
            # Default to filling with "Unknown" as a string.
            df[c] = df[c].fillna("Unknown").astype(str)
            
    if _DEBUG:
        print("DEBUG _build_input_df result:")
        print(df.head(5))
        print(df.dtypes)

    return df

def fraudriskscore_final(claim: dict) -> dict:
    """
    Input: claim dict (must contain text in one of keys like 'claim_description').
    Returns: dict with fraud_risk_score, text_suspicion_score, risk_level, decision.
    """
    # Extract text
    text = ""
    for key in ("claim_description","adjuster_notes","notes","text_all"):
        if key in claim and claim[key] not in (None, ""):
            text = claim[key]
            break

    cleaned = clean_text(text)
    if cleaned == "":
        text_score = 0.0
    else:
        try:
            emb = embedder.encode([cleaned], show_progress_bar=False)
            emb = np.asarray(emb)  # shape (1, dim)
            # Make sure text_model supports predict_proba
            if hasattr(text_model, "predict_proba"):
                text_score = float(text_model.predict_proba(emb)[:, 1][0])
            else:
                # fallback: predict returns 0/1 -> return float
                text_score = float(text_model.predict(emb)[0])
        except Exception as e:
            # If embedding or text model fails, fall back to 0 and log
            text_score = 0.0
            if _DEBUG:
                print("Text model error:", e)

    # Build dataframe and safe conversions
    df = _build_input_df(claim)

    # Ensure we set the text_suspicion_score column if expected
    if "text_suspicion_score" in df.columns:
        # assign scalar (broadcasts to single-row df)
        df["text_suspicion_score"] = text_score

    if _DEBUG:
        print("DF before final predict:")
        print(df.head(3))
        print(df.dtypes)

    # Predict with final model (should be a full pipeline)
    try:
        proba = float(final_model.predict_proba(df)[0, 1])
    except Exception as e:
        # Provide a helpful error message back to the caller
        raise RuntimeError(f"Final model prediction error: {e}")

    # Determine risk level and decision (you can change thresholds here)
    if proba < 0.2:
        risk = "Low"; decision = "Approve Automatically"
    elif proba < 0.5:
        risk = "Medium"; decision = "Needs Manual Review"
    else:
        risk = "High"; decision = "Flagged as Potential Fraud"

    return {"fraud_risk_score": round(proba, 4),
            "text_suspicion_score": round(text_score, 4),
            "risk_level": risk,
            "decision": decision}





