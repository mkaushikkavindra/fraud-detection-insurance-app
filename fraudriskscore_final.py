import joblib, re, numpy as np, pandas as pd
from sentence_transformers import SentenceTransformer
from typing import Dict, Any
from sklearn.pipeline import Pipeline
# Note: Importing only for type hinting. Ensure scikit-learn is in requirements.txt.

# --- GLOBAL CONFIGURATION AND DEPENDENCY LOADING ---
# NOTE: Update file names if your saved models differ slightly.
try:
    final_model = joblib.load("fraud_detection_model.joblib")
    model_lr = joblib.load("logisticregression.joblib")
    model_gbc = joblib.load("gbcmodel.joblib")
    text_model = joblib.load("text_model.joblib")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    class DummyModel:
        def predict_proba(self, df): return np.array([[1.0, 0.0]])
        # Fallback list containing base features plus engineered flags/ratios/text score.
        # Note: This is a minimal set; real deployment should use the full OHE list.
        def __init__(self): 
            self.feature_names_in_ = ['months_as_customer', 'age', 'policy_deductable', 'policy_annual_premium', 'umbrella_limit', 
                                      'capital-gains', 'capital-loss', 'incident_hour_of_the_day', 'number_of_vehicles_involved', 
                                      'bodily_injuries', 'witnesses', 'total_claim_amount', 'injury_claim', 'property_claim', 
                                      'vehicle_claim', 'auto_year', 'claim_to_premium_ratio', 'injury_ratio', 'property_ratio', 
                                      'vehicle_ratio', 'daysdiff', 'police_report_flag', 'property_damage_flag', 
                                      'authorities_contacted_flag', 'injury_flag', 'multiple_vehicles_flag', 'text_suspicion_score',
                                      'policy_state_CA', 'insured_sex_MALE', 'incident_severity_Total Loss']
    final_model, model_lr, model_gbc, text_model = DummyModel(), DummyModel(), DummyModel(), DummyModel()
    embedder = DummyModel()
    raise RuntimeError(f"Model Loading Failed: {e}") # Re-raise to show error in Streamlit

# --- SHARED HELPERS ---
def clean_text(t: Any) -> str:
    """Replicates text cleaning from the notebook (cell 30)"""
    if t is None: return ""
    s = str(t)
    s = re.sub(r'\S+@\S+\.\S+', '[EMAIL]', s) # Email replacement
    s = re.sub(r'\b\d{4,}\b', '[NUM]', s) # Number replacement
    s = re.sub(r'[^A-Za-z0-9 ]+', ' ', s)
    return s.lower().strip()

def _build_input_df(claim: Dict[str, Any], model_reference: Pipeline) -> pd.DataFrame:
    """
    Builds the standardized input DataFrame by manually replicating:
    1. Feature Engineering (ratios, flags, daysdiff).
    2. One-Hot Encoding (OHE) on 19 categorical columns.
    3. Final cleanup and column alignment.
    """
    df = pd.DataFrame([claim])
    
    # 1. FEATURE ENGINEERING (Replicates notebook cells 16-19)
    
    # Calculate engineered features (ratios)
    safe_total_claim = df['total_claim_amount'].iloc[0] if df['total_claim_amount'].iloc[0] > 0 else 1.0
    safe_annual_premium = df['policy_annual_premium'].iloc[0] if df['policy_annual_premium'].iloc[0] > 0 else 1.0
    
    df['claim_to_premium_ratio'] = df['total_claim_amount'] / safe_annual_premium
    df['injury_ratio'] = df['injury_claim'] / safe_total_claim
    df['property_ratio'] = df['property_claim'] / safe_total_claim
    df['vehicle_ratio'] = df['vehicle_claim'] / safe_total_claim
    
    # Calculate daysdiff (Handle object type dates from input)
    try:
        policy_bind_date = pd.to_datetime(df['policy_bind_date'].iloc[0])
        incident_date = pd.to_datetime(df['incident_date'].iloc[0])
        df['daysdiff'] = (incident_date - policy_bind_date).days
    except:
        df['daysdiff'] = 0 # Fallback if dates are invalid

    # Add text score placeholder (will be filled later)
    if "text_suspicion_score" not in df.columns:
        df["text_suspicion_score"] = np.nan

    # --- 2. ONE-HOT ENCODING (OHE) ---
    
    # A. Define Categorical Columns (from notebook cell 15)
    category_cols = [
        'policy_bind_date', 'policy_state', 'policy_csl', 'insured_sex', 
        'insured_education_level', 'insured_occupation', 'insured_hobbies', 
        'insured_relationship', 'incident_date', 'incident_type', 
        'collision_type', 'incident_severity', 'authorities_contacted', 
        'incident_state', 'incident_city', 'property_damage', 
        'police_report_available', 'auto_make', 'auto_model'
    ]
    
    # B. Handle missing values (the '?' string) by converting them to NaN first
    df = df.replace('?', np.nan) 
    
    # C. Apply OHE using pd.get_dummies() on the categorical columns
    # We explicitly treat NaNs as their own category (to handle missing data like authorities_contacted, collision_type)
    df_ohe = pd.get_dummies(df[category_cols], dummy_na=True)
    
    # D. Drop the raw string columns and combine OHE features
    df = df.drop(columns=category_cols, errors='ignore')
    df = pd.concat([df, df_ohe], axis=1)


    # --- 3. FINAL ALIGNMENT AND CLEANUP ---
    
    # E. Drop remaining ID/Text columns that should not be features (Replicates drops from notebook cell 12)
    cols_to_drop_final = ['policy_number', 'insured_zip', 'incident_location', 
                          'claim_description', 'policy_bind_date', 'incident_date', 
                          'policy_csl', 'incident_type', 'authorities_contacted', 
                          'property_damage', 'police_report_available', 'auto_make', 'auto_model']
    
    df = df.drop(columns=[c for c in cols_to_drop_final if c in df.columns], errors='ignore')
    
    # F. Get the definitive list of features the model pipeline expects.
    try:
        expected_features = list(model_reference.feature_names_in_)
    except Exception:
        # Fallback to current column set if model object structure is complex
        expected_features = df.columns.tolist() 

    # G. Ensure all expected features are present (set to 0 if missing)
    for col in expected_features:
        if col not in df.columns:
            df[col] = 0.0
            
    # H. Filter the DataFrame to include only expected features and ensure correct order
    df = df[expected_features]
            
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

    # 2. Build and Align DataFrame (calls the fixed function)
    df = _build_input_df(claim, model)

    # 3. Assign the calculated text_suspicion_score
    if "text_suspicion_score" in df.columns:
        df["text_suspicion_score"] = text_score

    # --- FINAL ROBUST CLEANUP ---
    try:
        # Force all data to float/numeric, coercing any lingering objects/strings to NaN
        df = df.apply(pd.to_numeric, errors='coerce') 
        
        # Fill all NaNs (either from coercion or feature alignment) with 0.0
        df = df.fillna(0.0) 
        
        # Final cast to ensure consistent float type
        df = df.astype(float)
    except Exception as e:
        raise RuntimeError(f"Data cleanup failed before prediction: {e}")
    # ----------------------------

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

# --- 4. FINAL SCORING FUNCTIONS (NOTE: fraudriskscore_final is aliased to RFC in app.py) ---

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
