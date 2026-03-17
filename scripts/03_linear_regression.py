import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import joblib

print("=" * 60)
print("PHASE 3: MULTIPLE LINEAR REGRESSION")
print("=" * 60)

# ============================================================
# Step 3.1: Load Preprocessed Data
# ============================================================
print("\n[3.1] Loading preprocessed data...")
X_train_reg, X_test_reg, y_train_reg, y_test_reg = joblib.load('outputs/data/regression_splits.pkl')
X_train_reg_scaled, X_test_reg_scaled = joblib.load('outputs/data/regression_splits_scaled.pkl')
feature_names_reg = joblib.load('outputs/models/feature_names_regression.pkl')

print(f"Train: {X_train_reg.shape}, Test: {X_test_reg.shape}")

# ============================================================
# Step 3.2: Train Model
# ============================================================
print("\n[3.2] Training Linear Regression...")
model_lr = LinearRegression()
model_lr.fit(X_train_reg_scaled, y_train_reg)
print("Model trained.")

# ============================================================
# Step 3.3: Evaluate
# ============================================================
print("\n[3.3] Evaluating model...")
y_pred_reg = model_lr.predict(X_test_reg_scaled)

r2 = r2_score(y_test_reg, y_pred_reg)
rmse = np.sqrt(mean_squared_error(y_test_reg, y_pred_reg))
mae = mean_absolute_error(y_test_reg, y_pred_reg)

print(f"R² Score: {r2:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"MAE: {mae:.4f}")

metrics_text = f"Linear Regression Results\n{'='*40}\nR² Score: {r2:.4f}\nRMSE: {rmse:.4f}\nMAE: {mae:.4f}\n"
with open('outputs/data/regression_metrics.txt', 'w') as f:
    f.write(metrics_text)

# ============================================================
# Step 3.4: Statsmodels OLS for p-values
# ============================================================
print("\n[3.4] OLS Summary (statsmodels)...")
X_train_sm = sm.add_constant(X_train_reg_scaled)
ols_model = sm.OLS(y_train_reg, X_train_sm).fit()
print(ols_model.summary())

with open('outputs/data/ols_summary.txt', 'w') as f:
    f.write(str(ols_model.summary()))

# ============================================================
# Step 3.5: VIF
# ============================================================
print("\n[3.5] Variance Inflation Factors...")
vif_data = pd.DataFrame()
vif_data["Feature"] = feature_names_reg
vif_data["VIF"] = [variance_inflation_factor(X_train_reg_scaled, i) for i in range(X_train_reg_scaled.shape[1])]
vif_data = vif_data.sort_values('VIF', ascending=False)
print(vif_data)
vif_data.to_csv('outputs/data/vif_table.csv', index=False)

# ============================================================
# Step 3.6: Generate Charts
# ============================================================
print("\n[3.6] Generating regression charts...")

# Chart 9: Regression Coefficients
print("  Generating Chart 9: Regression Coefficients...")
coef_df = pd.DataFrame({
    'Feature': feature_names_reg,
    'Coefficient': model_lr.coef_
})
coef_df = coef_df.sort_values('Coefficient', key=abs, ascending=True)

fig, ax = plt.subplots(figsize=(10, 8))
colors = ['#2196F3' if c > 0 else '#F44336' for c in coef_df['Coefficient']]
ax.barh(coef_df['Feature'], coef_df['Coefficient'], color=colors)
ax.set_xlabel('Coefficient Value')
ax.set_title(f'Linear Regression Coefficients — Predicting BMI from Lifestyle Factors\n(R² = {r2:.4f})')
ax.axvline(x=0, color='black', linewidth=0.5)
plt.tight_layout()
plt.savefig('outputs/charts/09_regression_coefficients.png', dpi=150)
plt.close()

# Chart 10: Actual vs Predicted BMI
print("  Generating Chart 10: Actual vs Predicted...")
fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(y_test_reg, y_pred_reg, alpha=0.5, s=20, color='#2196F3')
min_val = min(y_test_reg.min(), y_pred_reg.min())
max_val = max(y_test_reg.max(), y_pred_reg.max())
ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
ax.set_xlabel('Actual BMI')
ax.set_ylabel('Predicted BMI')
ax.set_title('Actual vs Predicted BMI')
ax.legend()
plt.tight_layout()
plt.savefig('outputs/charts/10_regression_actual_vs_predicted.png', dpi=150)
plt.close()

# Chart 11: Residuals
print("  Generating Chart 11: Residuals...")
residuals = y_test_reg - y_pred_reg
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(y_pred_reg, residuals, alpha=0.5, s=20, color='#FF9800')
ax.axhline(y=0, color='red', linewidth=2, linestyle='--')
ax.set_xlabel('Predicted BMI')
ax.set_ylabel('Residuals')
ax.set_title('Residual Plot — Linear Regression')
plt.tight_layout()
plt.savefig('outputs/charts/11_regression_residuals.png', dpi=150)
plt.close()

# ============================================================
# Step 3.7: Save Model
# ============================================================
print("\n[3.7] Saving model...")
joblib.dump(model_lr, 'outputs/models/linear_regression_model.pkl')

# ============================================================
# Step 3.8: Key Findings
# ============================================================
print("\n[3.8] Key Findings")
coef_sorted = coef_df.sort_values('Coefficient', key=abs, ascending=False)
top_positive = coef_sorted[coef_sorted['Coefficient'] > 0].iloc[0]
top_negative = coef_sorted[coef_sorted['Coefficient'] < 0].iloc[0]

findings = []
findings.append(f"R² = {r2:.4f} — lifestyle factors explain {r2*100:.1f}% of BMI variance")
findings.append(f"Largest positive coefficient: {top_positive['Feature']} ({top_positive['Coefficient']:.4f})")
findings.append(f"Largest negative coefficient: {top_negative['Feature']} ({top_negative['Coefficient']:.4f})")
findings.append(f"RMSE: {rmse:.4f} kg/m²")
findings.append(f"MAE: {mae:.4f} kg/m²")

for f in findings:
    print(f)

with open('outputs/data/regression_findings.txt', 'w') as f:
    f.write('\n'.join(findings))

print("\n" + "=" * 60)
print("PHASE 3 COMPLETE: Linear Regression model trained and saved")
print("=" * 60)
