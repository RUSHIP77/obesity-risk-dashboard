import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

print("=" * 60)
print("PHASE 2: DATA PREPROCESSING")
print("=" * 60)

os.makedirs('outputs/models', exist_ok=True)
os.makedirs('outputs/data', exist_ok=True)

# ============================================================
# Step 2.1: Load Raw Data
# ============================================================
print("\n[2.1] Loading raw data...")
df = pd.read_csv('data/ObesityDataSet_raw_and_data_sinthetic.csv')
print(f"Loaded: {df.shape}")

# ============================================================
# Step 2.2: Feature Engineering
# ============================================================
print("\n[2.2] Feature Engineering...")

df['BMI'] = df['Weight'] / (df['Height'] ** 2)
# Note: Activity_Screen_Ratio and Dietary_Risk_Score were removed —
# they are not used in any feature matrix (classification, regression, or clustering).

print(f"BMI range: {df['BMI'].min():.2f} - {df['BMI'].max():.2f}")

# ============================================================
# Step 2.3: Encode Categorical Variables
# ============================================================
print("\n[2.3] Encoding categorical variables...")

df_processed = df.copy()

# Binary
df_processed['Gender'] = df_processed['Gender'].map({'Female': 0, 'Male': 1})
df_processed['family_history_with_overweight'] = df_processed['family_history_with_overweight'].map({'no': 0, 'yes': 1})
df_processed['FAVC'] = df_processed['FAVC'].map({'no': 0, 'yes': 1})
df_processed['SMOKE'] = df_processed['SMOKE'].map({'no': 0, 'yes': 1})
df_processed['SCC'] = df_processed['SCC'].map({'no': 0, 'yes': 1})

# Ordinal
df_processed['CAEC'] = df_processed['CAEC'].map({'no': 0, 'Sometimes': 1, 'Frequently': 2, 'Always': 3})
df_processed['CALC'] = df_processed['CALC'].map({'no': 0, 'Sometimes': 1, 'Frequently': 2, 'Always': 3})

# Target encoding
target_map = {
    'Insufficient_Weight': 0, 'Normal_Weight': 1,
    'Overweight_Level_I': 2, 'Overweight_Level_II': 3,
    'Obesity_Type_I': 4, 'Obesity_Type_II': 5, 'Obesity_Type_III': 6
}
reverse_label_mapping = {v: k for k, v in target_map.items()}
df_processed['NObeyesdad_encoded'] = df_processed['NObeyesdad'].map(target_map)

# One-hot encode MTRANS
mtrans_dummies = pd.get_dummies(df_processed['MTRANS'], prefix='MTRANS', drop_first=True)
# Ensure consistent column types
mtrans_dummies = mtrans_dummies.astype(int)
df_processed = pd.concat([df_processed, mtrans_dummies], axis=1)
df_processed.drop('MTRANS', axis=1, inplace=True)

print("Encoding complete.")
print(f"Columns after encoding: {list(df_processed.columns)}")

# ============================================================
# Step 2.4: Create Feature Matrix and Target Vector
# ============================================================
print("\n[2.4] Creating feature matrices...")

# Target vectors
y_class = df_processed['NObeyesdad_encoded']
y_bmi = df_processed['BMI']

# Classification features: LIFESTYLE ONLY (no Height, Weight, BMI — these cause data leakage
# because BMI directly determines the obesity class label)
cls_cols = ['Gender', 'Age', 'family_history_with_overweight', 'FAVC', 'FCVC', 'NCP',
            'CAEC', 'SMOKE', 'CH2O', 'SCC', 'FAF', 'TUE', 'CALC']
cls_mtrans_cols = [c for c in df_processed.columns if c.startswith('MTRANS_')]
cls_cols.extend(cls_mtrans_cols)
X_full = df_processed[cls_cols]

# Regression features: lifestyle only (no Weight, Height, BMI, Activity_Screen_Ratio, Dietary_Risk_Score)
# Actually per the prompt: use lifestyle features to predict BMI
lifestyle_cols = ['Gender', 'Age', 'family_history_with_overweight', 'FAVC', 'FCVC', 'NCP',
                  'CAEC', 'SMOKE', 'CH2O', 'SCC', 'FAF', 'TUE', 'CALC']
# Add MTRANS dummies
mtrans_cols = [c for c in df_processed.columns if c.startswith('MTRANS_')]
lifestyle_cols.extend(mtrans_cols)
X_lifestyle = df_processed[lifestyle_cols]

# Clustering features: lifestyle/behavioral only (same as regression but without MTRANS maybe)
# Per prompt: FCVC, NCP, CAEC, CH2O, FAF, TUE, FAVC, SMOKE, SCC, CALC, family_history, Gender, Age
cluster_cols = ['Gender', 'Age', 'family_history_with_overweight', 'FAVC', 'FCVC', 'NCP',
                'CAEC', 'SMOKE', 'CH2O', 'SCC', 'FAF', 'TUE', 'CALC']
X_cluster = df_processed[cluster_cols]

print(f"X_full shape: {X_full.shape}")
print(f"X_lifestyle shape: {X_lifestyle.shape}")
print(f"X_cluster shape: {X_cluster.shape}")
print(f"y_class shape: {y_class.shape}")
print(f"y_bmi shape: {y_bmi.shape}")

# ============================================================
# Step 2.5: Train-Test Split
# ============================================================
print("\n[2.5] Train-Test Split...")

X_train_cls, X_test_cls, y_train_cls, y_test_cls = train_test_split(
    X_full, y_class, test_size=0.2, random_state=42, stratify=y_class
)

X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
    X_lifestyle, y_bmi, test_size=0.2, random_state=42
)

print(f"Classification: Train={X_train_cls.shape}, Test={X_test_cls.shape}")
print(f"Regression: Train={X_train_reg.shape}, Test={X_test_reg.shape}")

# ============================================================
# Step 2.6: Scale Features
# ============================================================
print("\n[2.6] Scaling features...")

scaler_cls = StandardScaler()
X_train_cls_scaled = scaler_cls.fit_transform(X_train_cls)
X_test_cls_scaled = scaler_cls.transform(X_test_cls)

scaler_reg = StandardScaler()
X_train_reg_scaled = scaler_reg.fit_transform(X_train_reg)
X_test_reg_scaled = scaler_reg.transform(X_test_reg)

scaler_cluster = StandardScaler()
X_cluster_scaled = scaler_cluster.fit_transform(X_cluster)

print("Scaling complete.")

# ============================================================
# Step 2.7: Save All Preprocessed Artifacts
# ============================================================
print("\n[2.7] Saving preprocessed artifacts...")

joblib.dump(scaler_cls, 'outputs/models/scaler_classification.pkl')
joblib.dump(scaler_reg, 'outputs/models/scaler_regression.pkl')
joblib.dump(scaler_cluster, 'outputs/models/scaler_clustering.pkl')

df_processed.to_csv('outputs/data/processed_data.csv', index=False)

joblib.dump(X_full.columns.tolist(), 'outputs/models/feature_names_classification.pkl')
joblib.dump(X_lifestyle.columns.tolist(), 'outputs/models/feature_names_regression.pkl')
joblib.dump(X_cluster.columns.tolist(), 'outputs/models/feature_names_clustering.pkl')
joblib.dump(target_map, 'outputs/models/label_mapping.pkl')
joblib.dump(reverse_label_mapping, 'outputs/models/reverse_label_mapping.pkl')

joblib.dump((X_train_cls, X_test_cls, y_train_cls, y_test_cls), 'outputs/data/classification_splits.pkl')
joblib.dump((X_train_reg, X_test_reg, y_train_reg, y_test_reg), 'outputs/data/regression_splits.pkl')
joblib.dump((X_train_cls_scaled, X_test_cls_scaled), 'outputs/data/classification_splits_scaled.pkl')
joblib.dump((X_train_reg_scaled, X_test_reg_scaled), 'outputs/data/regression_splits_scaled.pkl')
joblib.dump(X_cluster_scaled, 'outputs/data/clustering_data_scaled.pkl')
joblib.dump(X_cluster, 'outputs/data/clustering_data.pkl')
joblib.dump(y_bmi, 'outputs/data/y_bmi.pkl')
joblib.dump(y_class, 'outputs/data/y_class.pkl')

print("\nAll artifacts saved successfully!")
print("\n" + "=" * 60)
print("PHASE 2 COMPLETE: All preprocessing artifacts saved")
print("=" * 60)
