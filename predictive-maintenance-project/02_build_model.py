"""
02_build_model.py
--------------------
Trains a classifier to predict Machine failure from sensor readings.

Three real-world decisions baked into this script, explained inline:
1. Dropping the 5 failure-subtype columns (leakage prevention)
2. Handling severe class imbalance (class_weight, stratified split)
3. Using precision/recall instead of accuracy to judge the model
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
# the first place -- TWF=1 basically means "this row IS a tool wear
# failure." Including them as features would be DATA LEAKAGE: the model
# would just learn "if any of these flags is 1, predict failure," which
# is trivially perfect on this dataset but completely useless in the
# real world, where you don't have a "this machine is about to fail"
# flag ahead of time -- that's the whole thing you're trying to predict
# FROM sensor readings, not alongside them.
#
# This is one of the most common real ML mistakes, and catching it
# yourself is a strong thing to be able to describe in an interview.
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

# WHY stratify=y: with only 3.39% failures, a normal random split could
# easily put very few (or very lucky, too many) failures in the test
# set purely by chance, making your evaluation numbers unreliable.
# Stratifying guarantees the same ~3.39% failure rate in both the
# training and test sets -- a small technical detail that materially
# changes whether your evaluation results mean anything.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train size: {len(X_train)}, failures: {y_train.sum()}")
print(f"Test size: {len(X_test)}, failures: {y_test.sum()}")

# ============================================================
# MODEL
# ============================================================

# WHY RandomForest: it handles non-linear relationships between sensors
# well (failure isn't a simple straight-line function of torque, for
# instance), needs little feature scaling/preprocessing, and gives
# feature importances for free -- useful for the "why did the model
# flag this machine" explanation later.
#
# WHY class_weight="balanced": this tells the model to treat mistakes
# on the rare failure class as more costly than mistakes on the common
# healthy class, roughly proportional to how rare failures are. Without
# this, RandomForest (like most models) will happily just learn to
# mostly predict "no failure" and still score high on raw accuracy,
# because that's right 96%+ of the time by default.
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
# WHY these metrics over plain accuracy:
# - Precision (Failure row): of everything the model FLAGGED as a
#   failure, what % actually failed? Low precision = too many false
#   alarms, engineers stop trusting the system.
# - Recall (Failure row): of everything that ACTUALLY failed, what %
#   did the model catch? Low recall = missed real failures, the whole
#   point of the system.
# There's a real trade-off between these two -- worth being able to
# discuss which one matters more for a maintenance context (usually
# recall, since missing a real failure is more costly than one extra
# inspection -- but it depends on the cost of a false alarm too).

print("\n--- Confusion Matrix ---")
print(confusion_matrix(y_test, y_pred))

print(f"\nROC-AUC: {roc_auc_score(y_test, y_proba):.3f}")
# ROC-AUC summarizes how well the model ranks failures above non-failures
# across ALL possible decision thresholds, not just the default 0.5 cutoff --
# a useful single number for comparing models, though precision/recall
# at your ACTUAL chosen threshold matters more for real deployment decisions.

# ============================================================
# FEATURE IMPORTANCE
# ============================================================

importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
print("\n--- Feature Importance ---")
print(importances)
# This is a genuinely useful output to screenshot for your README/
# interview -- it tells you (and anyone reviewing your work) WHICH
# sensors the model actually relies on, which is exactly the kind of
# explainability question a client asks before trusting a model with
# real maintenance decisions.

# ============================================================
# SAVE THE MODEL
# ============================================================

joblib.dump(model, "maintenance_model.pkl")
print("\nModel saved to maintenance_model.pkl")
