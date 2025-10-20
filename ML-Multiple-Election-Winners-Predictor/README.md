# Kemeny-Young Method-Based ML for Ranked-Choice Voting

## Project Overview
This project implements a complete machine learning pipeline to analyze ranked-choice voting data, predict the single winner, and determine the full rank order of 8 candidates. The core innovation is using the **Kemeny-Young voting system** to generate ground-truth labels and rankings for training and validating classification models.

## Key Features
* [cite_start]**Data Preparation:** Preprocessing of raw electoral preference data, including imputation and transformation of 8-candidate data into a 7-candidate format[cite: 881, 899].
* [cite_start]**Kemeny-Young Implementation:** Calculates the Kemeny-Young optimal order (target) for aggregated preference data segments[cite: 937].
* **Feature Engineering:** Extracts meaningful features from voter preference chunks to prepare the data for the machine learning models.
* [cite_start]**Model Training:** Trains and compares multiple classification models, including Logistic Regression, Naive Bayes, Decision Tree, Random Forest, and SVM, for both multi-winner (order prediction) and single-winner (label prediction) tasks[cite: 1071, 1086, 1229].
* [cite_start]**Hyperparameter Optimization:** Includes parameter tuning for the best-performing models to maximize predictive accuracy[cite: 1111].

## Technologies Used
* **Language:** Python
* **Libraries:** Pandas, NumPy, Scikit-learn, Itertools
* **Environment:** Google Colaboratory (Jupyter Notebook)
