"""
02_build_model.py
--------------------
Trains a classifier to predict Machine failure from sensor readings.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib

df = pd.read_csv("data/ai4i2020.csv")

# ============================================================
# FEATURE ENGINEERING
# ============================================================

# WHY drop TWF, HDF, PWF, OSF, RNF: these are the 5 SPECIFIC failure
# subtypes that were used to construct the "Machine failure" label in
# the first place
leakage_cols = ["TWF", "HDF", "PWF", "OSF", "RNF"]

# UDI and Product ID are just identifiers, not physical signal --
# keeping them risks the model "memorizing" specific machines instead
# of learning general failure patterns.
id_cols = ["UDI", "Product ID"]

df_model = df.drop(columns=leakage_cols + id_cols)

# "Type" (L/M/H = product quality variant) IS real signal -- the dataset
# documentation says higher-quality tooling adds different amounts of
# wear. Convert it to a number the model can use.
df_model["Type"] = df_model["Type"].map({"L": 0, "M": 1, "H": 2})

X = df_model.drop(columns=["Machine failure"])
y = df_model["Machine failure"]

# ============================================================
# TRAIN/TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train size: {len(X_train)}, failures: {y_train.sum()}")
print(f"Test size: {len(X_test)}, failures: {y_test.sum()}")

# ============================================================
# MODEL
# ============================================================

# WHY RandomForest: it handles non-linear relationships between sensors well 

model = RandomForestClassifier(
    n_estimators=200,
    class_weight="balanced",
    random_state=42,
    max_depth=10,
)

model.fit(X_train, y_train)

# ============================================================
# EVALUATION
# ============================================================

y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred, target_names=["No Failure", "Failure"]))

print("\n--- Confusion Matrix ---")
print(confusion_matrix(y_test, y_pred))

print(f"\nROC-AUC: {roc_auc_score(y_test, y_proba):.3f}")

# ============================================================
# FEATURE IMPORTANCE
# ============================================================

importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
print("\n--- Feature Importance ---")
print(importances)

# ============================================================
# SAVE THE MODEL
# ============================================================

joblib.dump(model, "maintenance_model.pkl")
print("\nModel saved to maintenance_model.pkl")
