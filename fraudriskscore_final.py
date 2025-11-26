import joblib, re, numpy as np, pandas as pd
from sentence_transformers import SentenceTransformer
from typing import Dict, Any
# Note: The presence of a working pipeline implies ColumnTransformer/Pipeline is handled by the model object.

# ----- load models (will raise on import if missing) -----
final_model = joblib.load("fraud_detection_model.joblib")
text_model = joblib.load("text_model.joblib")
model_gbc = joblib.load("gbcmodel.joblib") # Renamed from gbc_model to model_gbc for consistency
model_lr = joblib.load("logisticregression.joblib") # Renamed from lr_model to model_lr for consistency
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# --- Model Input Feature Definition (Used for alignment and fillna) ---
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
    GLOBAL_THRESHOLD = 0.2

# small debug flag (switch to True to print df/dtypes into logs)
_DEBUG = False

# --- SHARED HELPERS (UNCHANGED) ---

def clean_text(t: Any) -> str:
    if t is None: 
        return ""
    s = re.sub(r"[^a-zA-Z0-9\s\.]", " ", str(t))
    s = " ".join(s.split()).strip().lower()
    return s

def _build_input_df(claim: Dict[str, Any]) -> pd.DataFrame:
    """Uses the original, working feature alignment/imputation logic."""
    df = pd.DataFrame([claim])

    if "text_suspicion_score" not in df.columns:
        df["text_suspicion_score"] = np.nan

    # Get the feature list the model *actually* expects
    try:
        expected_features = list(final_model.feature_names_in_)
    except Exception:
        expected_features = [c for c in (NUMERIC_COLS + CATEGORICAL_COLS) if c in df.columns]

    for c in expected_features:
        if c not in df.columns:
            df[c] = np.nan
    
    df = df[expected_features]

    # --- ORIGINAL EXPLICIT TYPE CONVERSION & IMPUTATION (This must work as per your report) ---
    for c in df.columns:
        if c in NUMERIC_COLS:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        elif c in CATEGORICAL_COLS:
            df[c] = df[c].fillna("Unknown").astype(str)
        else:
            df[c] = df[c].fillna("Unknown").astype(str)
            
    return df

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

def _calculate_base_score(claim: Dict[str, Any], model: Any) -> tuple[float, float]:
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

    # 2. Build and Align DataFrame (Uses the working, original data prep)
    df = _build_input_df(claim)

    # 3. Assign the calculated text_suspicion_score
    if "text_suspicion_score" in df.columns:
        df["text_suspicion_score"] = text_score

    # 4. Predict
    try:
        proba = float(model.predict_proba(df)[0, 1])
    except Exception as e:
        # Re-raise the error with the model type
        raise RuntimeError(f"{type(model).__name__} prediction error: {e}")

    return proba, text_score

# --- 4. FINAL SCORING FUNCTIONS (One for Each Strategic Model) ---

def fraudriskscore_RFC(claim: Dict[str, Any]) -> Dict[str, Any]:
    """Scores a claim using the Random Forest Classifier (Safety Net) model."""
    proba, text_score = _calculate_base_score(claim, final_model)
    
    # RFC Strategic Thresholds
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
    
    # LR Strategic Thresholds (Set to match analysis)
    THRESHOLD = 0.50 
    HIGH_RISK_LIMIT = 0.70 
    risk, decision = _apply_threshold_logic(proba, THRESHOLD, HIGH_RISK_LIMIT)

    return {"fraud_risk_score": round(proba, 4),
            "text_suspicion_score": round(text_score, 4),
            "risk_level": risk,
            "decision": decision,
            "threshold_used": THRESHOLD}


def fraudriskscore_GBC(claim: Dict[str, Any]) -> Dict[str, Any]:
    """Scores a claim using the GBC (Operational High Recall) model."""
    proba, text_score = _calculate_base_score(claim, model_gbc)
    
    # GBC Strategic Thresholds (Set to match analysis)
    THRESHOLD = 0.30 
    HIGH_RISK_LIMIT = 0.60 
    risk, decision = _apply_threshold_logic(proba, THRESHOLD, HIGH_RISK_LIMIT)

    return {"fraud_risk_score": round(proba, 4),
            "text_suspicion_score": round(text_score, 4),
            "risk_level": risk,
            "decision": decision,
            "threshold_used": THRESHOLD}

fraudriskscore_final=fraudriskscore_RFC

def fraudriskscore_ensemble(claim: Dict[str, Any]) -> Dict[str, Any]:
    resultdicts = [
        fraudriskscore_RFC(claim),
        fraudriskscore_LR(claim),
        fraudriskscore_GBC(claim),
    ]

    max_score = -1
    max_result = None
    
    for resdict in resultdicts:
        score = resdict['fraud_risk_score']
        if score > max_score:
            max_score = score
            max_result = resdict
            
    if max_result is None:
        return {"fraud_risk_score": 0.0, "risk_level": "Error", "decision": "Process Failed"}
        
    final_ensemble_result = {
        "fraud_risk_score": max_result['fraud_risk_score'],
        "text_suspicion_score": max_result['text_suspicion_score'],
        "risk_level": max_result['risk_level'],
        "decision": max_result['decision']
        #"source_model": max_result['model'],
        #"all_model_results": {resdict['model']: resdict for resdict in resultdicts}
    }
    
    return final_ensemble_result



