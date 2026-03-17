import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
import joblib

print("=" * 60)
print("PHASE 5: KNN CLASSIFIER")
print("=" * 60)

LABEL_ORDER = ['Insufficient_Weight', 'Normal_Weight', 'Overweight_Level_I',
               'Overweight_Level_II', 'Obesity_Type_I', 'Obesity_Type_II', 'Obesity_Type_III']

# ============================================================
# Step 5.1: Load Preprocessed Data
# ============================================================
print("\n[5.1] Loading SCALED classification data...")
X_train_cls, X_test_cls, y_train_cls, y_test_cls = joblib.load('outputs/data/classification_splits.pkl')
X_train_cls_scaled, X_test_cls_scaled = joblib.load('outputs/data/classification_splits_scaled.pkl')

print(f"Train: {X_train_cls_scaled.shape}, Test: {X_test_cls_scaled.shape}")

# ============================================================
# Step 5.2: Find Optimal k
# ============================================================
print("\n[5.2] Cross-validation for optimal k...")
k_values = list(range(1, 31, 2))
cv_scores_knn = []
for k in k_values:
    knn = KNeighborsClassifier(n_neighbors=k)
    scores = cross_val_score(knn, X_train_cls_scaled, y_train_cls, cv=5, scoring='accuracy')
    cv_scores_knn.append(scores.mean())
    print(f"  k={k}: CV accuracy={scores.mean():.4f}")

best_k = k_values[np.argmax(cv_scores_knn)]
print(f"\nBest k: {best_k} with CV accuracy: {max(cv_scores_knn):.4f}")

# Chart 16: k Tuning
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(k_values, cv_scores_knn, 'b-o', markersize=5)
ax.plot(best_k, max(cv_scores_knn), 'ro', markersize=12, label=f'Best k={best_k}')
ax.set_xlabel('Number of Neighbors (k)')
ax.set_ylabel('Cross-Validation Accuracy')
ax.set_title('KNN: Cross-Validation Accuracy vs Number of Neighbors (k)')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/charts/16_knn_k_tuning.png', dpi=150)
plt.close()

# ============================================================
# Step 5.3: Train Final Model
# ============================================================
print("\n[5.3] Training final KNN model...")
knn_model = KNeighborsClassifier(n_neighbors=best_k)
knn_model.fit(X_train_cls_scaled, y_train_cls)

# ============================================================
# Step 5.4: Evaluate
# ============================================================
print("\n[5.4] Evaluating...")
y_pred_knn = knn_model.predict(X_test_cls_scaled)
acc = accuracy_score(y_test_cls, y_pred_knn)
f1_macro = f1_score(y_test_cls, y_pred_knn, average='macro')
f1_weighted = f1_score(y_test_cls, y_pred_knn, average='weighted')

print(f"Accuracy: {acc:.4f}")
print(f"Macro F1: {f1_macro:.4f}")
print(f"Weighted F1: {f1_weighted:.4f}")

report = classification_report(y_test_cls, y_pred_knn, target_names=LABEL_ORDER)
print(f"\nClassification Report:\n{report}")

metrics_text = f"KNN Results\n{'='*40}\n"
metrics_text += f"Best k: {best_k}\n"
metrics_text += f"Accuracy: {acc:.4f}\n"
metrics_text += f"Macro F1: {f1_macro:.4f}\n"
metrics_text += f"Weighted F1: {f1_weighted:.4f}\n\n"
metrics_text += f"Classification Report:\n{report}\n"

with open('outputs/data/knn_metrics.txt', 'w') as f:
    f.write(metrics_text)

# ============================================================
# Step 5.5: Generate Charts
# ============================================================
print("\n[5.5] Generating KNN charts...")

# Chart 17: Confusion Matrix
print("  Generating Chart 17: KNN Confusion Matrix...")
cm = confusion_matrix(y_test_cls, y_pred_knn)
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=LABEL_ORDER, yticklabels=LABEL_ORDER, ax=ax)
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
ax.set_title(f'KNN (k={best_k}) — Confusion Matrix')
plt.xticks(rotation=45, ha='right', fontsize=8)
plt.yticks(rotation=0, fontsize=8)
plt.tight_layout()
plt.savefig('outputs/charts/17_knn_confusion_matrix.png', dpi=150)
plt.close()

# ============================================================
# Step 5.6: Save Model
# ============================================================
print("\n[5.6] Saving model...")
joblib.dump(knn_model, 'outputs/models/knn_model.pkl')
joblib.dump(best_k, 'outputs/data/best_k_knn.pkl')

print("\n" + "=" * 60)
print("PHASE 5 COMPLETE: KNN model trained and saved")
print(f"Best k={best_k} | Accuracy: {acc:.4f} | Macro F1: {f1_macro:.4f}")
print("=" * 60)
