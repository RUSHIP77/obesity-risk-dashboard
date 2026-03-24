import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
import joblib

print("=" * 60)
print("PHASE 4: DECISION TREE CLASSIFIER")
print("=" * 60)

LABEL_ORDER = ['Insufficient_Weight', 'Normal_Weight', 'Overweight_Level_I',
               'Overweight_Level_II', 'Obesity_Type_I', 'Obesity_Type_II', 'Obesity_Type_III']

# ============================================================
# Step 4.1: Load Preprocessed Data
# ============================================================
print("\n[4.1] Loading preprocessed data...")
X_train_cls, X_test_cls, y_train_cls, y_test_cls = joblib.load('outputs/data/classification_splits.pkl')
feature_names_cls = joblib.load('outputs/models/feature_names_classification.pkl')
label_mapping = joblib.load('outputs/models/label_mapping.pkl')

print(f"Train: {X_train_cls.shape}, Test: {X_test_cls.shape}")

# ============================================================
# Step 4.2: Find Optimal max_depth
# ============================================================
print("\n[4.2] Cross-validation for optimal max_depth...")
depths = range(2, 25)
cv_scores = []
for d in depths:
    dt = DecisionTreeClassifier(max_depth=d, random_state=42,
                                min_samples_split=10, min_samples_leaf=5)
    scores = cross_val_score(dt, X_train_cls, y_train_cls, cv=5, scoring='f1_macro')
    cv_scores.append(scores.mean())
    print(f"  depth={d}: CV Macro F1={scores.mean():.4f}")

best_depth = list(depths)[np.argmax(cv_scores)]
print(f"\nBest max_depth: {best_depth} with CV Macro F1: {max(cv_scores):.4f}")

# Chart 12: Depth Tuning
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(list(depths), cv_scores, 'b-o', markersize=5)
ax.plot(best_depth, max(cv_scores), 'ro', markersize=12, label=f'Best depth={best_depth}')
ax.set_xlabel('Max Depth')
ax.set_ylabel('Cross-Validation Macro F1')
ax.set_title('Decision Tree: Cross-Validation Macro F1 vs Max Depth')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/charts/12_dt_depth_tuning.png', dpi=150)
plt.close()

# ============================================================
# Step 4.3: Train Final Model
# ============================================================
print("\n[4.3] Training final Decision Tree...")
dt_model = DecisionTreeClassifier(max_depth=best_depth, random_state=42,
                                   min_samples_split=10, min_samples_leaf=5)
dt_model.fit(X_train_cls, y_train_cls)

# ============================================================
# Step 4.4: Evaluate
# ============================================================
print("\n[4.4] Evaluating...")
y_pred_dt = dt_model.predict(X_test_cls)
acc = accuracy_score(y_test_cls, y_pred_dt)
f1_macro = f1_score(y_test_cls, y_pred_dt, average='macro')
f1_weighted = f1_score(y_test_cls, y_pred_dt, average='weighted')

print(f"Accuracy: {acc:.4f}")
print(f"Macro F1: {f1_macro:.4f}")
print(f"Weighted F1: {f1_weighted:.4f}")

report = classification_report(y_test_cls, y_pred_dt, target_names=LABEL_ORDER)
print(f"\nClassification Report:\n{report}")

metrics_text = f"Decision Tree Results\n{'='*40}\n"
metrics_text += f"Best max_depth: {best_depth}\n"
metrics_text += f"Accuracy: {acc:.4f}\n"
metrics_text += f"Macro F1: {f1_macro:.4f}\n"
metrics_text += f"Weighted F1: {f1_weighted:.4f}\n\n"
metrics_text += f"Classification Report:\n{report}\n"

with open('outputs/data/dt_metrics.txt', 'w') as f:
    f.write(metrics_text)

# ============================================================
# Step 4.5: Generate Charts
# ============================================================
print("\n[4.5] Generating Decision Tree charts...")

# Chart 13: Confusion Matrix
print("  Generating Chart 13: Confusion Matrix...")
cm = confusion_matrix(y_test_cls, y_pred_dt)
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=LABEL_ORDER, yticklabels=LABEL_ORDER, ax=ax)
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
ax.set_title('Decision Tree — Confusion Matrix')
plt.xticks(rotation=45, ha='right', fontsize=8)
plt.yticks(rotation=0, fontsize=8)
plt.tight_layout()
plt.savefig('outputs/charts/13_dt_confusion_matrix.png', dpi=150)
plt.close()

# Chart 14: Feature Importance
print("  Generating Chart 14: Feature Importance...")
importances = dt_model.feature_importances_
feat_imp = pd.DataFrame({'Feature': feature_names_cls, 'Importance': importances})
feat_imp = feat_imp.sort_values('Importance', ascending=True).tail(10)

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(feat_imp['Feature'], feat_imp['Importance'], color='#2196F3')
ax.set_xlabel('Importance')
ax.set_title('Decision Tree — Feature Importance (Top 10)')
plt.tight_layout()
plt.savefig('outputs/charts/14_dt_feature_importance.png', dpi=150)
plt.close()

# Chart 15: Tree Visualization
print("  Generating Chart 15: Tree Visualization...")
fig, ax = plt.subplots(figsize=(25, 12))
plot_tree(dt_model, max_depth=4, feature_names=feature_names_cls, class_names=LABEL_ORDER,
          filled=True, rounded=True, fontsize=8, ax=ax)
ax.set_title('Decision Tree (Top 4 Levels)')
plt.tight_layout()
plt.savefig('outputs/charts/15_dt_tree_visualization.png', dpi=150)
plt.close()

# ============================================================
# Step 4.6: Save Model
# ============================================================
print("\n[4.6] Saving model...")
joblib.dump(dt_model, 'outputs/models/decision_tree_model.pkl')

print("\n" + "=" * 60)
print("PHASE 4 COMPLETE: Decision Tree model trained and saved")
print(f"Accuracy: {acc:.4f} | Macro F1: {f1_macro:.4f}")
print("=" * 60)
