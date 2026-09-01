"""
03_threshold_tuning.py
--------------------
The model doesn't actually output "failure" or "no failure" -- it outputs
a PROBABILITY (0 to 1) that a machine will fail. scikit-learn's default
.predict() just applies a 0.5 cutoff: probability > 0.5 = "failure".
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score
import joblib

df = pd.read_csv("data/ai4i2020.csv")

leakage_cols = ["TWF", "HDF", "PWF", "OSF", "RNF"]
id_cols = ["UDI", "Product ID"]
df_model = df.drop(columns=leakage_cols + id_cols)
df_model["Type"] = df_model["Type"].map({"L": 0, "M": 1, "H": 2})

X = df_model.drop(columns=["Machine failure"])
y = df_model["Machine failure"]

# Must use the SAME split as training (same random_state) so we're
# evaluating on the same held-out test set the model has never seen.
_, X_test, _, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = joblib.load("maintenance_model.pkl")
y_proba = model.predict_proba(X_test)[:, 1]

print(f"{'Threshold':>10} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Failures caught':>16} {'False alarms':>14}")

for threshold in [0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]:
    y_pred_at_threshold = (y_proba >= threshold).astype(int)

    precision = precision_score(y_test, y_pred_at_threshold, zero_division=0)
    recall = recall_score(y_test, y_pred_at_threshold, zero_division=0)
    f1 = f1_score(y_test, y_pred_at_threshold, zero_division=0)

    true_positives = ((y_pred_at_threshold == 1) & (y_test == 1)).sum()
    false_positives = ((y_pred_at_threshold == 1) & (y_test == 0)).sum()

    print(f"{threshold:>10.2f} {precision:>10.2f} {recall:>10.2f} {f1:>10.2f} "
          f"{true_positives:>16} {false_positives:>14}")
