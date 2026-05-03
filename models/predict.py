"""
predict.py - Load saved model and classify new tickets.
"""

import pandas as pd
import joblib
from glob import glob


def load_latest_model(model_dir="models/saved_models"):
    model_files = sorted(glob(f"{model_dir}/*.joblib"))
    if not model_files:
        raise FileNotFoundError(f"No saved models in {model_dir}/")
    latest = model_files[-1]
    bundle = joblib.load(latest)
    print(f"Loaded: {latest}")
    return bundle["pipeline"], bundle["label_encoder"], bundle["features"]


def predict_priority(pipeline, le, features_dict):
    df = pd.DataFrame([features_dict])
    pred_encoded = pipeline.predict(df)[0]
    prediction = le.inverse_transform([pred_encoded])[0]
    return {"prediction": prediction}


def predict_batch(pipeline, le, df, feature_cols, output_col="predicted_priority"):
    df = df.copy()
    X = df[feature_cols].fillna(0)
    encoded = pipeline.predict(X)
    df[output_col] = le.inverse_transform(encoded)
    print(f"Classified {len(df):,} tickets")
    print(df[output_col].value_counts().to_string())
    return df
