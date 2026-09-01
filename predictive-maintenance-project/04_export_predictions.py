"""
04_export_predictions.py
--------------------
Generates predictions for every machine in the test set (using our
chosen threshold, not scikit-learn's default 0.5) and saves everything
to a CSV that Power BI can connect to directly.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
import joblib

CHOSEN_THRESHOLD = 0.40 

df = pd.read_csv("data/ai4i2020.csv")

leakage_cols = ["TWF", "HDF", "PWF", "OSF", "RNF"]
id_cols_to_drop_for_model = ["UDI", "Product ID"]
df_model = df.drop(columns=leakage_cols + id_cols_to_drop_for_model)
df_model["Type"] = df_model["Type"].map({"L": 0, "M": 1, "H": 2})

X = df_model.drop(columns=["Machine failure"])
y = df_model["Machine failure"]

# Same split as before -- we need the ORIGINAL row indices too, so we
# can trace predictions back to the real Product ID for the dashboard.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = joblib.load("maintenance_model.pkl")

y_proba = model.predict_proba(X_test)[:, 1]
y_pred_at_threshold = (y_proba >= CHOSEN_THRESHOLD).astype(int)

# Rebuild a results table using the ORIGINAL columns (with real Product
# ID and Type as text, not encoded numbers) - Power BI users want
# readable labels, not the numeric encoding we needed for the model.
results = df.loc[X_test.index, ["Product ID", "Type", "Air temperature [K]",
                                  "Process temperature [K]", "Rotational speed [rpm]",
                                  "Torque [Nm]", "Tool wear [min]"]].copy()

results["actual_failure"] = y_test.values
results["predicted_failure_probability"] = y_proba
results["predicted_failure"] = y_pred_at_threshold
results["threshold_used"] = CHOSEN_THRESHOLD

# A readable label for dashboard filters/visuals.
results["prediction_outcome"] = results.apply(
    lambda row: (
        "True Positive (caught)" if row["predicted_failure"] == 1 and row["actual_failure"] == 1
        else "False Positive (false alarm)" if row["predicted_failure"] == 1 and row["actual_failure"] == 0
        else "False Negative (missed)" if row["predicted_failure"] == 0 and row["actual_failure"] == 1
        else "True Negative (correctly healthy)"
    ),
    axis=1
)

results.to_csv("predictions_for_powerbi.csv", index=False)
print(f"Saved {len(results)} predictions to predictions_for_powerbi.csv")
print(f"\nOutcome breakdown:")
print(results["prediction_outcome"].value_counts())

# Also export feature importance separately -- a small, simple table
# that's easy to turn into its own bar chart in Power BI.
importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
importances.to_csv("feature_importance.csv", header=["importance"])
print("\nSaved feature_importance.csv")
