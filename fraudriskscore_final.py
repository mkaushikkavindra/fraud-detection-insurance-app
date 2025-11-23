import joblib, re, numpy as np, pandas as pd
from sentence_transformers import SentenceTransformer
from typing import Dict, Any

# --- GLOBAL CONFIGURATION AND DEPENDENCY LOADING ---
# NOTE: Update file names if your saved models differ slightly.
try:
    final_model = joblib.load("fraud_detection_model.joblib")        # Assuming this is your final model/RFC
    model_lr = joblib.load("logisticregression.joblib")    # New LR model
    model_gbc = joblib.load("gbcmodel.joblib")       # New GBC model (Optimized for 0.3)
    text_model = joblib.load("text_model.joblib")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    # Use placeholder if loading fails (Streamlit will display the error)
    class DummyModel:
        def predict_proba(self, df): return np.array([[1.0, 0.0]])
        def __init__(self): self.feature_names_in_ = ['months_as_customer', 'age', 'policy_number']
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
    This logic MUST match the feature engineering/imputation used in the training notebook.
    """
    df = pd.DataFrame([claim])
    
    # Get text score placeholder
    if "text_suspicion_score" not in df.columns:
        df["text_suspicion_score"] = np.nan

    try:
        # Get the feature list the model *actually* expects
        expected_features = list(model_reference.feature_names_in_)
    except Exception:
        # Fallback for models without feature_names_in_
        expected_features = [c for c in df.columns if c not in ("claim_description", "adjuster_notes", "notes", "text_all")]

    for c in expected_features:
        if c not in df.columns: df[c] = np.nan
    
    df = df[expected_features]

    # --- IMPUTATION AND TYPE CONVERSION ---
    for c in df.columns:
        # Attempt conversion to numeric, coercing errors
        try: df[c] = pd.to_numeric(df[c], errors='coerce')
        except: pass
            
        # Impute: 0 for numeric/float types, "Unknown" for categorical/object types
        if df[c].dtype in (np.dtype('float64'), np.dtype('int64')):
            df[c] = df[c].fillna(0)
        else:
            df[c] = df[c].fillna("Unknown").astype(str)
            
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

    # 3. Assign the calculated text_suspicion_score
    if "text_suspicion_score" in df.columns:
        df["text_suspicion_score"] = text_score

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
