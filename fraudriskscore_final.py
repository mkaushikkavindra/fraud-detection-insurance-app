# fraudriskscore_final.py
import joblib, re, numpy as np, pandas as pd
from sentence_transformers import SentenceTransformer

# Load models
final_model = joblib.load("fraud_detection_model.joblib")
text_model = joblib.load("text_model.joblib")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# threshold (optional)
try:
    with open("finalthresholdvalue.txt") as f:
        GLOBAL_THRESHOLD = float(f.read().strip())
except:
    GLOBAL_THRESHOLD = 0.3

def clean_text(t):
    if t is None: return ""
    s = re.sub(r"[^a-zA-Z0-9\s\.]", " ", str(t))
    s = " ".join(s.split()).strip().lower()
    return s

def _build_input_df(claim):
    # Build dataframe and coerce numeric types where possible
    df = pd.DataFrame([claim])
    # Ensure text_suspicion_score exists (model may expect it)
    if "text_suspicion_score" not in df.columns:
        df["text_suspicion_score"] = np.nan

    # Align columns to model if model exposes feature names
    try:
        expected = list(final_model.feature_names_in_)
    except Exception:
        expected = list(df.columns)

    for c in expected:
        if c not in df.columns:
            df[c] = np.nan
    df = df[expected]

    # Fill missing: categorical -> "Unknown", numeric -> 0
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].fillna("Unknown")
        else:
            df[c] = df[c].fillna(0)

    # Try numeric conversion where sensible
    for c in df.columns:
        try:
            df[c] = pd.to_numeric(df[c], errors="ignore")
        except:
            pass

    return df

def fraudriskscore_final(claim):
    # claim: dict (must include a text field e.g. claim_description)
    text = ""
    for key in ("claim_description","adjuster_notes","notes","text_all"):
        if key in claim and claim[key] not in (None,""):
            text = claim[key]; break

    cleaned = clean_text(text)
    if cleaned == "":
        text_score = 0.0
    else:
        emb = embedder.encode([cleaned], show_progress_bar=False)
        text_score = float(text_model.predict_proba(np.asarray(emb))[:,1][0])

    df = _build_input_df(claim)
    if "text_suspicion_score" in df.columns:
        df["text_suspicion_score"] = text_score

    # final predict — final_model should be full pipeline including preprocessing
    proba = float(final_model.predict_proba(df)[0,1])

    if proba < 0.2:
        risk = "Low"; decision = "Approve Automatically"
    elif proba < 0.5:
        risk = "Medium"; decision = "Needs Manual Review"
    else:
        risk = "High"; decision = "Flagged as Potential Fraud"

    return {"fraud_risk_score": round(proba,4),
            "text_suspicion_score": round(text_score,4),
            "risk_level": risk,
            "decision": decision}
