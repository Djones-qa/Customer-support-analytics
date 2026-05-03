"""
train.py - Train resolution time and priority classifiers.
"""

import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score
import sys
sys.path.append(str(Path(__file__).parent.parent))
from src.utils import load_config


def prepare_features(df, config=None):
    if config is None:
        config = load_config()
    feature_cols = [
        "created_hour", "created_day_of_week", "created_month",
        "is_weekend", "is_business_hours",
        "description_word_count", "num_interactions", "reopen_count",
        "is_escalated", "customer_ticket_count",
    ]
    feature_cols = [c for c in feature_cols if c in df.columns]
    target = "priority"
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found")
    df_clean = df[feature_cols + [target]].dropna()
    le = LabelEncoder()
    y = le.fit_transform(df_clean[target])
    X = df_clean[feature_cols]
    return X, y, feature_cols, le


def get_models():
    return {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "RandomForest": RandomForestClassifier(
            n_estimators=200, max_depth=15, random_state=42, n_jobs=-1
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42
        ),
    }


def train_and_compare(df, config=None, save_best=True):
    if config is None:
        config = load_config()
    X, y, feature_cols, le = prepare_features(df, config)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train: {len(X_train):,} | Test: {len(X_test):,}")
    print(f"Classes: {dict(zip(le.classes_, np.bincount(y)))}\n")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    models = get_models()
    try:
        from xgboost import XGBClassifier
        models["XGBoost"] = XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            random_state=42, n_jobs=-1, verbosity=0,
            use_label_encoder=False, eval_metric="mlogloss"
        )
    except ImportError:
        pass
    results = []
    best_f1, best_name, best_pipe = 0, None, None
    for name, model in models.items():
        print(f"Training {name}...", end=" ")
        pipe = Pipeline([("scaler", StandardScaler()), ("clf", model)])
        cv = cross_val_score(pipe, X_train, y_train, cv=skf, scoring="f1_weighted", n_jobs=-1)
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")
        results.append({
            "model": name, "cv_f1": round(cv.mean(), 4),
            "test_accuracy": round(acc, 4), "test_f1": round(f1, 4)
        })
        print(f"F1={f1:.4f}")
        if f1 > best_f1:
            best_f1, best_name, best_pipe = f1, name, pipe
    results_df = pd.DataFrame(results).sort_values("test_f1", ascending=False)
    print(f"\nBest: {best_name} (F1={best_f1:.4f})")
    if save_best and best_pipe:
        save_dir = "models/saved_models"
        os.makedirs(save_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"{save_dir}/{best_name}_{ts}.joblib"
        joblib.dump({"pipeline": best_pipe, "label_encoder": le, "features": feature_cols}, path)
        print(f"Saved to {path}")
    return results_df, best_pipe, le, (X_test, y_test)
