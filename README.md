# Predicting Childhood Obesity via Lifestyle Factors
## DSC 510 Final Project — Group 2
### Rushi Patel, Raffey Akram, Vishnu Doddapaneni
### Professor Casey Bennett | DePaul University | Winter 2025-2026

## Project Overview
This project uses machine learning to predict obesity risk based on lifestyle factors,
building on the CDC HI-5 framework as a Bucket 3 community-wide intervention.

## Dataset
Palechor & de la Hoz Manotas (2019) — 2,111 records, 17 features, 7 obesity classes.
UCI Machine Learning Repository ID: 544

## Models
1. **Multiple Linear Regression** — predicts BMI from lifestyle factors (R² = 0.466)
2. **Decision Tree Classifier** — classifies into 7 obesity levels (73.5% accuracy)
3. **KNN Classifier** — nearest-neighbor classification comparison (80.1% accuracy)
4. **K-Means Clustering** — identifies 4 behavioral risk groups

## Dashboard
```bash
cd dashboard && python dashboard.py
```
Navigate to: http://localhost:8050

### Dashboard Tabs
1. **Overview** — KPI cards, pie chart, BMI histogram
2. **Risk Factor Explorer** — Interactive feature distributions, scatter plots, correlation heatmap
3. **Model Results** — Comparison table, confusion matrices, regression coefficients
4. **Cluster Profiles** — PCA visualization, radar charts, cluster summaries
5. **Screening Tool** — Enter lifestyle factors to get personalized obesity risk prediction

## Project Structure
```
project/
├── data/
│   └── ObesityDataSet_raw_and_data_sinthetic.csv
├── scripts/
│   ├── 01_eda.py
│   ├── 02_preprocessing.py
│   ├── 03_linear_regression.py
│   ├── 04_decision_tree.py
│   ├── 05_knn.py
│   ├── 06_kmeans.py
│   └── 07_model_comparison.py
├── dashboard/
│   └── dashboard.py
├── outputs/
│   ├── charts/        (23 PNG charts)
│   ├── models/        (trained models + scalers)
│   └── data/          (processed data + metrics)
└── README.md
```

## Requirements
pandas, numpy, scikit-learn, matplotlib, seaborn, plotly, dash,
dash-bootstrap-components, joblib, statsmodels, scipy
