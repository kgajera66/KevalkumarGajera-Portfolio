"""
01_explore_data.py
--------------------
First pass: understand the data before touching a model.
"""

import pandas as pd

df = pd.read_csv("data/ai4i2020.csv")

print("Shape:", df.shape)
print("\nColumns:", list(df.columns))
print("\nFirst rows:\n", df.head())

# --- Class balance check ---
failure_rate = df["Machine failure"].mean()
print(f"\nMachine failure rate: {failure_rate:.2%}")
print(df["Machine failure"].value_counts())

# --- Which specific failure modes are present ---
failure_cols = ["TWF", "HDF", "PWF", "OSF", "RNF"]
print("\nFailure mode frequency:")
print(df[failure_cols].sum())

# --- Sensor ranges by failure status ---
# Comparing sensor readings between failed and healthy machines is the
# fastest way to build intuition for what the model will actually learn.
sensor_cols = ["Air temperature [K]", "Process temperature [K]",
               "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]"]

print("\nSensor averages: failed vs healthy machines")
print(df.groupby("Machine failure")[sensor_cols].mean())
