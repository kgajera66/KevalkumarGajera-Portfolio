# Telecom Data Analysis (Detailed)

This folder contains a Jupyter notebook and outputs for a telecom data analysis project.

## Files
- `telecom_data_analysis.ipynb`: Jupyter notebook with analysis (cleaning, feature engineering, IsolationForest, Q1-Q10).
- `telecom_expert_notebook_outputs/`: Output folder created when running the notebook (CSVs, JSONs, PNGs).
- `telecom_data_large.csv`: Input dataset (place this file at the path `/mnt/data/telecom_data_large.csv` or adjust the notebook).

## How to run
1. Install required packages:
```
pip install pandas numpy matplotlib scipy scikit-learn
```
2. Open `telecom_data_analysis.ipynb` in Jupyter and run all cells.
3. Outputs will be saved to `telecom_expert_notebook_outputs/`.

## Project Summary
- Data cleaning (duplicates, missing values)
- Feature engineering (signal_quality, efficiency_score)
- Outlier handling (IQR capping)
- Anomaly detection (z-score and IsolationForest)
- 10 expert questions answered (see notebook)

## Next steps
- Build a dashboard (Power BI / Dash) using cleaned outputs.
- Link anomalies to maintenance logs for RCA.
- Add clustering and time-series forecasting for capacity planning.
