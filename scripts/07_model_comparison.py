import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import joblib

print("=" * 60)
print("PHASE 7: MODEL COMPARISON")
print("=" * 60)

# ============================================================
# Step 7.1: Load All Results
# ============================================================
print("\n[7.1] Loading all model results...")

# Read metrics files
with open('outputs/data/regression_metrics.txt', 'r') as f:
    reg_text = f.read()

with open('outputs/data/dt_metrics.txt', 'r') as f:
    dt_text = f.read()

with open('outputs/data/knn_metrics.txt', 'r') as f:
    knn_text = f.read()

# Parse key metrics
def parse_metric(text, keyword):
    for line in text.split('\n'):
        if keyword in line:
            try:
                return float(line.split(':')[-1].strip())
            except ValueError:
                raise ValueError(f"Could not parse '{keyword}' from line: {line}")
    raise ValueError(f"'{keyword}' not found in metrics text. Run the upstream script first.")

r2 = parse_metric(reg_text, 'R²')
dt_acc = parse_metric(dt_text, 'Accuracy')
dt_f1_macro = parse_metric(dt_text, 'Macro F1')
dt_f1_weighted = parse_metric(dt_text, 'Weighted F1')
knn_acc = parse_metric(knn_text, 'Accuracy')
knn_f1_macro = parse_metric(knn_text, 'Macro F1')
knn_f1_weighted = parse_metric(knn_text, 'Weighted F1')

best_k_knn = joblib.load('outputs/data/best_k_knn.pkl')
best_k_cluster = joblib.load('outputs/data/best_k_cluster.pkl')

# Load cluster silhouette
cluster_names = joblib.load('outputs/data/cluster_names.pkl')

# Load feature importances
dt_model = joblib.load('outputs/models/decision_tree_model.pkl')
feature_names_cls = joblib.load('outputs/models/feature_names_classification.pkl')
top_dt_feature = feature_names_cls[np.argmax(dt_model.feature_importances_)]

# Load regression top predictor
with open('outputs/data/regression_findings.txt', 'r') as f:
    reg_findings = f.read()

# ============================================================
# Step 7.2: Create Comparison Table
# ============================================================
print("\n[7.2] Model Comparison Table")

comparison = pd.DataFrame({
    'Model': ['Linear Regression', 'Decision Tree', f'KNN (k={best_k_knn})', f'K-Means (k={best_k_cluster})'],
    'Task': ['Regression (BMI)', 'Classification (7-class)', 'Classification (7-class)', 'Clustering'],
    'Primary Metric': [f'R² = {r2:.4f}', f'Accuracy = {dt_acc*100:.1f}%', f'Accuracy = {knn_acc*100:.1f}%', f'{best_k_cluster} risk groups'],
    'Macro F1': ['N/A', f'{dt_f1_macro:.4f}', f'{knn_f1_macro:.4f}', 'N/A'],
    'Key Insight': [
        'Lifestyle factors predict BMI',
        f'Top feature: {top_dt_feature}',
        f'Best k: {best_k_knn}',
        f'{best_k_cluster} risk groups found'
    ]
})

print(comparison.to_string(index=False))
comparison.to_csv('outputs/data/model_comparison.csv', index=False)

# ============================================================
# Step 7.3: Generate Comparison Chart
# ============================================================
print("\n[7.3] Generating comparison chart...")

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(3)
width = 0.25

dt_vals = [dt_acc, dt_f1_macro, dt_f1_weighted]
knn_vals = [knn_acc, knn_f1_macro, knn_f1_weighted]

bars1 = ax.bar(x - width/2, dt_vals, width, label='Decision Tree', color='#2196F3', alpha=0.8)
bars2 = ax.bar(x + width/2, knn_vals, width, label=f'KNN (k={best_k_knn})', color='#4CAF50', alpha=0.8)

ax.set_xticks(x)
ax.set_xticklabels(['Accuracy', 'Macro F1', 'Weighted F1'])
ax.set_ylabel('Score')
ax.set_title('Classification Model Comparison — Decision Tree vs KNN')
ax.legend()
ax.set_ylim(0, 1.1)

for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f'{bar.get_height():.3f}', ha='center', va='bottom', fontsize=9)
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f'{bar.get_height():.3f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('outputs/charts/23_model_comparison.png', dpi=150)
plt.close()

# ============================================================
# Step 7.4: Summary
# ============================================================
print("\n[7.4] Project Summary")

# Use Macro F1 as the primary comparison metric for multiclass classification —
# accuracy can be misleading with imbalanced classes.
best_classifier = "Decision Tree" if dt_f1_macro > knn_f1_macro else "KNN"
best_f1 = max(dt_f1_macro, knn_f1_macro)

summary = []
summary.append("=" * 60)
summary.append("PROJECT SUMMARY: Predicting Childhood Obesity via Lifestyle Factors")
summary.append("=" * 60)
summary.append(f"\n1. Linear Regression R² = {r2:.4f}")
summary.append(f"   → Lifestyle factors explain {r2*100:.1f}% of BMI variance")
summary.append(f"\n2. Best Classifier: {best_classifier} (by Macro F1)")
summary.append(f"   → Macro F1: {best_f1:.4f}")
summary.append(f"   → Decision Tree: Acc={dt_acc*100:.1f}%, F1={dt_f1_macro:.4f} | KNN: Acc={knn_acc*100:.1f}%, F1={knn_f1_macro:.4f}")
summary.append(f"\n3. K-Means identified {best_k_cluster} distinct behavioral risk groups")
summary.append(f"\n4. Top 3 Modifiable Risk Factors (from Decision Tree feature importance):")
importances = dt_model.feature_importances_
top3_idx = np.argsort(importances)[-3:][::-1]
for rank, idx in enumerate(top3_idx, 1):
    summary.append(f"   {rank}. {feature_names_cls[idx]} (importance: {importances[idx]:.4f})")

for line in summary:
    print(line)

with open('outputs/data/project_summary.txt', 'w') as f:
    f.write('\n'.join(summary))

print("\n" + "=" * 60)
print("PHASE 7 COMPLETE: All models compared and summary saved")
print("=" * 60)
