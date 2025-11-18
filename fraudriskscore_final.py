# fraudriskscore_final.py
import joblib, re, numpy as np, pandas as pd
from sentence_transformers import SentenceTransformer

# ----- load models (will raise on import if missing) -----
final_model = joblib.load("fraud_detection_model.joblib")
text_model = joblib.load("text_model.joblib")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

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

def _looks_numeric_series(s: pd.Series) -> bool:
    """
    Return True if all non-null / non-empty-string values in the series 
    look like numbers.
    """
    # Get all non-null values
    non_null = s.dropna().astype(str).str.strip()
    
    # Filter out empty strings
    non_empty = non_null[non_null != ""]
    
    if len(non_empty) == 0:
        # Series contains only nulls, empty strings, or is empty.
        # It's safe to treat as numeric (will become 0 or NaN).
        return True 
        
    # Check if all remaining (non-empty) strings match numeric pattern
    is_num_like = non_empty.str.match(r"^-?\d+(\.\d+)?$")
    return is_num_like.all()

def _build_input_df(claim: dict) -> pd.DataFrame:
    # Build dataframe from dict
    df = pd.DataFrame([claim])

    # Ensure text_suspicion_score exists (model may expect it)
    if "text_suspicion_score" not in df.columns:
        df["text_suspicion_score"] = np.nan

    # Align columns to model if model exposes feature names
    try:
        expected = list(final_model.feature_names_in_)
    except Exception:
        expected = list(df.columns)

    # Ensure all expected columns present
    for c in expected:
        if c not in df.columns:
            df[c] = np.nan
    df = df[expected]

    # --- Consolidated Type Conversion & Imputation Step ---
    # Fill missing: numeric -> 0, object/categorical -> "Unknown"
    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]):
            # It's already numeric. Just fill NaNs.
            df[c] = df[c].fillna(0)
        else:
            # It's object dtype. Check if it *should* be numeric
            # using our new robust function.
            if _looks_numeric_series(df[c]):
                # Yes, it's numeric-like. Coerce and fill with 0.
                df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
            else:
                # No, it's categorical. Fill with "Unknown".
                df[c] = df[c].fillna("Unknown")

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


