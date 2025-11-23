import joblib, re, numpy as np, pandas as pd
from sentence_transformers import SentenceTransformer
from typing import Dict, Any
from sklearn.pipeline import Pipeline # FIX: Import Pipeline to resolve NameError

# --- GLOBAL CONFIGURATION AND DEPENDENCY LOADING ---
# NOTE: Update file names if your saved models differ slightly.
try:
    final_model = joblib.load("fraud_detection_model.joblib")
    model_lr = joblib.load("logisticregression.joblib")
    model_gbc = joblib.load("gbcmodel.joblib")
    text_model = joblib.load("text_model.joblib")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    # Use placeholder if loading fails (Streamlit will display the error)
    class DummyModel:
        def predict_proba(self, df): return np.array([[1.0, 0.0]])
        # Dummy features must include all features expected after preprocessing,
        # including the text score and any OHE columns.
        def __init__(self): self.feature_names_in_ = ['months_as_customer', 'age', 'policy_deductable', 'policy_annual_premium', 'umbrella_limit', 'insured_zip', 'capital-gains', 'capital-loss', 'incident_hour_of_the_day', 'number_of_vehicles_involved', 'bodily_injuries', 'witnesses', 'total_claim_amount', 'injury_claim', 'property_claim', 'vehicle_claim', 'auto_year', 'claim_to_premium_ratio', 'injury_ratio', 'property_ratio', 'vehicle_ratio', 'daysdiff', 'police_report_flag', 'property_damage_flag', 'authorities_contacted_flag', 'injury_flag', 'multiple_vehicles_flag', 'text_suspicion_score', 'policy_state_CA', 'insured_sex_MALE', 'incident_severity_Total Loss', 'collision_type_Front Collision', 'collision_type_Side Collision', 'collision_type_Rear Collision', 'insured_education_level_JD']
    final_model, model_lr, model_gbc, text_model = DummyModel(), DummyModel(), DummyModel(), DummyModel()
    embedder = DummyModel()
    print(f"Model Loading Error: {e}. Using dummy models.")

# --- SHARED HELPERS ---
_DEBUG = False # Set to True for detailed logs

def clean_text(t: Any) -> str:
    """Cleans text for NLP processing."""
    if t is None: return ""
    s = re.sub(r"[^a-zA-Z0-9\s\.]", " ", str(t))
    s = " ".join(s.split()).strip().lower()
    return s

def _build_input_df(claim: Dict[str, Any], model_reference: Pipeline) -> pd.DataFrame:
    """
    Builds the standardized input DataFrame required by all model pipelines.
    Includes manual OHE for critical categorical features.
    The final cleanup to float/fillna(0) is handled in _calculate_base_score.
    """
    df = pd.DataFrame([claim])
    
    # 1. Get text score placeholder (will be filled later)
    if "text_suspicion_score" not in df.columns:
        df["text_suspicion_score"] = np.nan

    # 2. Get the feature list the model *actually* expects
    try:
        expected_features = list(model_reference.feature_names_in_)
    except Exception:
        # Fallback for dummy models
        expected_features = [c for c in df.columns if c not in ("claim_description", "adjuster_notes", "notes", "text_all", "policy_number", "policy_bind_date", "incident_date", "insured_zip", "insured_occupation", "insured_hobbies", "insured_relationship", "incident_city", "incident_location")]

    # --- MANUAL ONE-HOT ENCODING (OHE) ---
    
    # A. policy_state
    for state in ['CA', 'WA', 'AZ']: # Add all relevant states from training here
        col_name = f'policy_state_{state}'
        df[col_name] = np.where(df['policy_state'] == state, 1, 0)
    
    # B. insured_sex
    for sex in ['MALE', 'FEMALE']:
        col_name = f'insured_sex_{sex}'
        df[col_name] = np.where(df['insured_sex'] == sex, 1, 0)

    # C. incident_severity
    for severity in ['Total Loss', 'Major Damage']:
        col_name = f'incident_severity_{severity}'.replace(' ', '_')
        df[col_name] = np.where(df['incident_severity'] == severity, 1, 0)
        
    # D. collision_type (Handle missing/unseen values)
    collision_types = ['Front Collision', 'Side Collision', 'Rear Collision']
    for c_type in collision_types:
        col_name = f'collision_type_{c_type}'.replace(' ', '_')
        # Check if the column exists in the final feature list before creating it (optional check)
        if col_name in expected_features:
             # Ensure '?' is treated as 0 (no match)
            df[col_name] = np.where(df['collision_type'] == c_type, 1, 0)

    # E. insured_education_level
    for edu in ['JD', 'Masters', 'PhD']:
        col_name = f'insured_education_level_{edu}'
        df[col_name] = np.where(df['insured_education_level'] == edu, 1, 0)
        
    # --- END OF MANUAL OHE ---
    
    # 3. Align Columns: ensure all expected features are present (now including OHE columns)
    for c in expected_features:
        if c not in df.columns: 
            df[c] = np.nan
    
    # 4. Filter and Finalize DataFrame (only keep features the model was trained on)
    df = df[expected_features]

    # 5. Imputation and Final Type Conversion
    # *** REMOVED: The conflicting type conversion block is removed. ***
            
    return df

def _calculate_base_score(claim: Dict[str, Any], model: Pipeline) -> tuple[float, float]:
    """Calculates text score and final prediction probability for any given model."""
    
    # 1. Extract text and calculate Text Suspicion Score
    text = ""
    for key in ("claim_description","adjuster_notes","notes","text_all"):
        if key in claim and claim[key] not in (None, ""):
            text = claim[key]
            break
            
    cleaned = clean_text(text)
    text_score = 0.0
    if cleaned != "":
        try:
            emb = embedder.encode([cleaned], show_progress_bar=False)
            emb = np.asarray(emb)
            if hasattr(text_model, "predict_proba"):
                text_score = float(text_model.predict_proba(emb)[:, 1][0])
            else:
                text_score = float(text_model.predict(emb)[0])
        except Exception:
            text_score = 0.0

    # 2. Build and Align DataFrame
    df = _build_input_df(claim, model) 

    # 3. Assign the calculated text_suspicion_score (UNCHANGED)
    if "text_suspicion_score" in df.columns:
        df["text_suspicion_score"] = text_score

    # --- FINAL ROBUST FIX: Ensure the DataFrame is strictly numerical ---
    try:
        # 1. Force all columns to numeric types. This handles non-OHE features
        # (like policy_csl, which might contain strings) that were not caught 
        # by the manual OHE and are still 'object' types.
        df = df.apply(pd.to_numeric, errors='coerce') 
        
        # 2. Fill all NaNs resulting from coercion or alignment with 0.0
        df = df.fillna(0.0) 
        
        # 3. Ensure the entire structure is a consistent float type for the model
        df = df.astype(float)
    except Exception as e:
        # If this fails, the error message will confirm the exact issue
        raise RuntimeError(f"Data cleanup failed before prediction: {e}")
    # -----------------------------------------------------------------------

    # 4. Predict
    try:
        proba = float(model.predict_proba(df)[0, 1])
    except Exception as e:
        raise RuntimeError(f"Model prediction error: {e}")

    return proba, text_score

def _apply_threshold_logic(proba: float, threshold: float, high_risk_limit: float) -> tuple[str, str]:
    """Applies standardized risk tier logic."""
    if proba < threshold:
        risk = "Low"
        decision = "Approve Automatically."
    elif proba < high_risk_limit:
        risk = "Medium"
        decision = "Manual Review Required."
    else:
        risk = "High"
        decision = "Flagged as Potential Fraud."
    return risk, decision

# --- 4. FINAL SCORING FUNCTIONS (One for Each Strategic Model) ---

def fraudriskscore_RFC(claim: Dict[str, Any]) -> Dict[str, Any]:
    """Scores a claim using the Random Forest Classifier (Safety Net) model."""
    proba, text_score = _calculate_base_score(claim, final_model)
    
    # Strategic Thresholds: Pushes sensitivity to catch blind spots
    THRESHOLD = 0.20 
    HIGH_RISK_LIMIT = 0.50
    risk, decision = _apply_threshold_logic(proba, THRESHOLD, HIGH_RISK_LIMIT)

    return {"fraud_risk_score": round(proba, 4),
            "text_suspicion_score": round(text_score, 4),
            "risk_level": risk,
            "decision": decision,
            "threshold_used": THRESHOLD}


def fraudriskscore_LR(claim: Dict[str, Any]) -> Dict[str, Any]:
    """Scores a claim using the Logistic Regression (Baseline) model."""
    proba, text_score = _calculate_base_score(claim, model_lr)
    
    # Strategic Thresholds: Baseline model, standard thresholds
    THRESHOLD = 0.50 
    HIGH_RISK_LIMIT = 0.70 # Higher limit for demonstration
    risk, decision = _apply_threshold_logic(proba, THRESHOLD, HIGH_RISK_LIMIT)

    return {"fraud_risk_score": round(proba, 4),
            "text_suspicion_score": round(text_score, 4),
            "risk_level": risk,
            "decision": decision,
            "threshold_used": THRESHOLD}


def fraudriskscore_GBC(claim: Dict[str, Any]) -> Dict[str, Any]:
    """Scores a claim using the GBC (Operational High Recall) model."""
    proba, text_score = _calculate_base_score(claim, model_gbc)
    
    # Strategic Thresholds: Best F1-Score/Operational Threshold
    THRESHOLD = 0.30 
    HIGH_RISK_LIMIT = 0.60 
    risk, decision = _apply_threshold_logic(proba, THRESHOLD, HIGH_RISK_LIMIT)

    return {"fraud_risk_score": round(proba, 4),
            "text_suspicion_score": round(text_score, 4),
            "risk_level": risk,
            "decision": decision,
            "threshold_used": THRESHOLD}





