import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

print("=" * 60)
print("PHASE 1: EXPLORATORY DATA ANALYSIS")
print("=" * 60)

os.makedirs('outputs/charts', exist_ok=True)
os.makedirs('outputs/models', exist_ok=True)
os.makedirs('outputs/data', exist_ok=True)

# Standard chart settings
plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

OBESITY_ORDER = [
    'Insufficient_Weight', 'Normal_Weight',
    'Overweight_Level_I', 'Overweight_Level_II',
    'Obesity_Type_I', 'Obesity_Type_II', 'Obesity_Type_III'
]

OBESITY_COLORS = {
    'Insufficient_Weight': '#2196F3',
    'Normal_Weight': '#4CAF50',
    'Overweight_Level_I': '#FFC107',
    'Overweight_Level_II': '#FF9800',
    'Obesity_Type_I': '#FF5722',
    'Obesity_Type_II': '#F44336',
    'Obesity_Type_III': '#B71C1C'
}

# ============================================================
# Step 1.1: Load and Inspect Data
# ============================================================
print("\n[1.1] Loading dataset...")
df = pd.read_csv('data/ObesityDataSet_raw_and_data_sinthetic.csv')
print(f"Shape: {df.shape}")

# ============================================================
# Step 1.2: Dataset Overview
# ============================================================
print("\n[1.2] Dataset Overview")
print(f"\nData Types:\n{df.dtypes}")
print(f"\nNull Counts:\n{df.isnull().sum()}")
print(f"\nDescriptive Statistics:\n{df.describe()}")
print(f"\nTarget Variable Distribution:\n{df['NObeyesdad'].value_counts()}")

categorical_cols = ['Gender', 'family_history_with_overweight', 'FAVC', 'CAEC', 'SMOKE', 'SCC', 'CALC', 'MTRANS']
summary_lines = []
summary_lines.append(f"Dataset Shape: {df.shape}")
summary_lines.append(f"\nData Types:\n{df.dtypes.to_string()}")
summary_lines.append(f"\nNull Counts:\n{df.isnull().sum().to_string()}")
summary_lines.append(f"\nDescriptive Statistics:\n{df.describe().to_string()}")
summary_lines.append(f"\nTarget Variable Distribution:\n{df['NObeyesdad'].value_counts().to_string()}")

for col in categorical_cols:
    vc = df[col].value_counts()
    print(f"\n{col}:\n{vc}")
    summary_lines.append(f"\n{col}:\n{vc.to_string()}")

with open('outputs/data/dataset_summary.txt', 'w') as f:
    f.write('\n'.join(summary_lines))
print("\nSaved dataset_summary.txt")

# ============================================================
# Step 1.3: Feature Engineering
# ============================================================
print("\n[1.3] Feature Engineering for EDA...")
df['BMI'] = df['Weight'] / (df['Height'] ** 2)

print("\nBMI Statistics by Obesity Class:")
bmi_stats = df.groupby('NObeyesdad')['BMI'].describe()
print(bmi_stats)

# ============================================================
# Step 1.4: Generate ALL EDA Charts
# ============================================================
print("\n[1.4] Generating EDA Charts...")

# Chart 1: Target Variable Distribution
print("  Generating Chart 1: Target Distribution...")
fig, ax = plt.subplots(figsize=(10, 6))
counts = df['NObeyesdad'].value_counts().reindex(OBESITY_ORDER)
colors = [OBESITY_COLORS[c] for c in OBESITY_ORDER]
bars = ax.bar(range(len(OBESITY_ORDER)), counts.values, color=colors)
ax.set_xticks(range(len(OBESITY_ORDER)))
ax.set_xticklabels([c.replace('_', '\n') for c in OBESITY_ORDER], fontsize=9)
ax.set_ylabel('Count')
ax.set_title('Distribution of Obesity Levels in Dataset')
for bar, val in zip(bars, counts.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, str(val),
            ha='center', va='bottom', fontweight='bold', fontsize=10)
plt.tight_layout()
plt.savefig('outputs/charts/01_target_distribution.png', dpi=150)
plt.close()

# Chart 2: BMI Distribution by Obesity Class (Box Plot)
print("  Generating Chart 2: BMI Boxplot...")
fig, ax = plt.subplots(figsize=(12, 6))
data_for_box = [df[df['NObeyesdad'] == c]['BMI'].values for c in OBESITY_ORDER]
bp = ax.boxplot(data_for_box, patch_artist=True, labels=[c.replace('_', '\n') for c in OBESITY_ORDER])
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.set_ylabel('BMI (kg/m²)')
ax.set_title('BMI Distribution Across Obesity Categories')
plt.tight_layout()
plt.savefig('outputs/charts/02_bmi_boxplot.png', dpi=150)
plt.close()

# Chart 3: Correlation Heatmap
print("  Generating Chart 3: Correlation Heatmap...")
df_encoded = df.copy()
df_encoded['Gender'] = df_encoded['Gender'].map({'Female': 0, 'Male': 1})
df_encoded['family_history_with_overweight'] = df_encoded['family_history_with_overweight'].map({'no': 0, 'yes': 1})
df_encoded['FAVC'] = df_encoded['FAVC'].map({'no': 0, 'yes': 1})
df_encoded['CAEC'] = df_encoded['CAEC'].map({'no': 0, 'Sometimes': 1, 'Frequently': 2, 'Always': 3})
df_encoded['SMOKE'] = df_encoded['SMOKE'].map({'no': 0, 'yes': 1})
df_encoded['SCC'] = df_encoded['SCC'].map({'no': 0, 'yes': 1})
df_encoded['CALC'] = df_encoded['CALC'].map({'no': 0, 'Sometimes': 1, 'Frequently': 2, 'Always': 3})
# MTRANS encoded as ordinal here for correlation heatmap only.
# The preprocessing pipeline (02_preprocessing.py) uses one-hot encoding for modeling.
df_encoded['MTRANS'] = df_encoded['MTRANS'].map({
    'Walking': 0, 'Bike': 1, 'Motorbike': 2, 'Public_Transportation': 3, 'Automobile': 4
})

numeric_cols = ['Gender', 'Age', 'Height', 'Weight', 'family_history_with_overweight',
                'FAVC', 'FCVC', 'NCP', 'CAEC', 'SMOKE', 'CH2O', 'SCC', 'FAF', 'TUE',
                'CALC', 'MTRANS', 'BMI']
corr_matrix = df_encoded[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(14, 12))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            square=True, linewidths=0.5, ax=ax)
ax.set_title('Feature Correlation Heatmap')
plt.tight_layout()
plt.savefig('outputs/charts/03_correlation_heatmap.png', dpi=150)
plt.close()

# Chart 4: Key Feature Distributions by Obesity Level
print("  Generating Chart 4: Feature Distributions...")
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# 1. FAF
sns.violinplot(data=df, x='NObeyesdad', y='FAF', order=OBESITY_ORDER,
               palette=OBESITY_COLORS, ax=axes[0, 0])
axes[0, 0].set_title('Physical Activity Frequency (FAF)')
axes[0, 0].set_xticklabels([c.replace('_', '\n') for c in OBESITY_ORDER], fontsize=7, rotation=45)
axes[0, 0].set_xlabel('')

# 2. TUE
sns.violinplot(data=df, x='NObeyesdad', y='TUE', order=OBESITY_ORDER,
               palette=OBESITY_COLORS, ax=axes[0, 1])
axes[0, 1].set_title('Technology Use (TUE)')
axes[0, 1].set_xticklabels([c.replace('_', '\n') for c in OBESITY_ORDER], fontsize=7, rotation=45)
axes[0, 1].set_xlabel('')

# 3. FCVC
sns.violinplot(data=df, x='NObeyesdad', y='FCVC', order=OBESITY_ORDER,
               palette=OBESITY_COLORS, ax=axes[0, 2])
axes[0, 2].set_title('Vegetable Consumption (FCVC)')
axes[0, 2].set_xticklabels([c.replace('_', '\n') for c in OBESITY_ORDER], fontsize=7, rotation=45)
axes[0, 2].set_xlabel('')

# 4. CH2O
sns.violinplot(data=df, x='NObeyesdad', y='CH2O', order=OBESITY_ORDER,
               palette=OBESITY_COLORS, ax=axes[1, 0])
axes[1, 0].set_title('Water Consumption (CH2O)')
axes[1, 0].set_xticklabels([c.replace('_', '\n') for c in OBESITY_ORDER], fontsize=7, rotation=45)
axes[1, 0].set_xlabel('')

# 5. NCP
sns.violinplot(data=df, x='NObeyesdad', y='NCP', order=OBESITY_ORDER,
               palette=OBESITY_COLORS, ax=axes[1, 1])
axes[1, 1].set_title('Number of Main Meals (NCP)')
axes[1, 1].set_xticklabels([c.replace('_', '\n') for c in OBESITY_ORDER], fontsize=7, rotation=45)
axes[1, 1].set_xlabel('')

# 6. FAVC percentage per class
favc_pct = df.groupby('NObeyesdad')['FAVC'].apply(lambda x: (x == 'yes').mean() * 100).reindex(OBESITY_ORDER)
axes[1, 2].bar(range(len(OBESITY_ORDER)), favc_pct.values, color=colors)
axes[1, 2].set_xticks(range(len(OBESITY_ORDER)))
axes[1, 2].set_xticklabels([c.replace('_', '\n') for c in OBESITY_ORDER], fontsize=7, rotation=45)
axes[1, 2].set_title('High Caloric Food Consumption (% Yes)')
axes[1, 2].set_ylabel('Percentage (%)')

fig.suptitle('Key Lifestyle Factors Across Obesity Levels', fontsize=16, y=1.02)
plt.tight_layout()
plt.savefig('outputs/charts/04_feature_distributions.png', dpi=150, bbox_inches='tight')
plt.close()

# Chart 5: Family History Impact
print("  Generating Chart 5: Family History Impact...")
fig, ax = plt.subplots(figsize=(12, 6))
fh_counts = pd.crosstab(df['NObeyesdad'], df['family_history_with_overweight'])
fh_counts = fh_counts.reindex(OBESITY_ORDER)
fh_pct = fh_counts.div(fh_counts.sum(axis=1), axis=0) * 100
x = np.arange(len(OBESITY_ORDER))
width = 0.35
ax.bar(x - width/2, fh_pct['no'], width, label='No Family History', color='#4CAF50', alpha=0.8)
ax.bar(x + width/2, fh_pct['yes'], width, label='Family History', color='#F44336', alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels([c.replace('_', '\n') for c in OBESITY_ORDER], fontsize=9)
ax.set_ylabel('Percentage (%)')
ax.set_title('Impact of Family History on Obesity Level Distribution')
ax.legend()
plt.tight_layout()
plt.savefig('outputs/charts/05_family_history.png', dpi=150)
plt.close()

# Chart 6: Transportation Mode Analysis
print("  Generating Chart 6: Transportation Mode...")
fig, ax = plt.subplots(figsize=(12, 6))
mt_counts = pd.crosstab(df['NObeyesdad'], df['MTRANS'])
mt_counts = mt_counts.reindex(OBESITY_ORDER)
mt_pct = mt_counts.div(mt_counts.sum(axis=1), axis=0) * 100
mt_pct.plot(kind='bar', stacked=True, ax=ax, colormap='Set2')
ax.set_xticklabels([c.replace('_', '\n') for c in OBESITY_ORDER], rotation=45, fontsize=9)
ax.set_ylabel('Percentage (%)')
ax.set_title('Transportation Mode vs Obesity Level')
ax.legend(title='Transportation', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('outputs/charts/06_transportation.png', dpi=150, bbox_inches='tight')
plt.close()

# Chart 7: Age vs Weight Scatter
print("  Generating Chart 7: Age vs Weight Scatter...")
fig, ax = plt.subplots(figsize=(12, 8))
for cls in OBESITY_ORDER:
    subset = df[df['NObeyesdad'] == cls]
    ax.scatter(subset['Age'], subset['Weight'], c=OBESITY_COLORS[cls],
               label=cls.replace('_', ' '), alpha=0.6, s=30)
ax.set_xlabel('Age (years)')
ax.set_ylabel('Weight (kg)')
ax.set_title('Age vs Weight by Obesity Classification')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
plt.tight_layout()
plt.savefig('outputs/charts/07_age_weight_scatter.png', dpi=150, bbox_inches='tight')
plt.close()

# Chart 8: Gender Distribution
print("  Generating Chart 8: Gender Distribution...")
fig, ax = plt.subplots(figsize=(12, 6))
gender_counts = pd.crosstab(df['NObeyesdad'], df['Gender']).reindex(OBESITY_ORDER)
x = np.arange(len(OBESITY_ORDER))
width = 0.35
ax.bar(x - width/2, gender_counts['Female'], width, label='Female', color='#E91E63', alpha=0.8)
ax.bar(x + width/2, gender_counts['Male'], width, label='Male', color='#2196F3', alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels([c.replace('_', '\n') for c in OBESITY_ORDER], fontsize=9)
ax.set_ylabel('Count')
ax.set_title('Gender Distribution Across Obesity Levels')
ax.legend()
for i, (f, m) in enumerate(zip(gender_counts['Female'], gender_counts['Male'])):
    ax.text(i - width/2, f + 1, str(f), ha='center', va='bottom', fontsize=8)
    ax.text(i + width/2, m + 1, str(m), ha='center', va='bottom', fontsize=8)
plt.tight_layout()
plt.savefig('outputs/charts/08_gender_distribution.png', dpi=150)
plt.close()

# ============================================================
# Step 1.5: Key EDA Findings
# ============================================================
print("\n[1.5] Key EDA Findings")

most_common = df['NObeyesdad'].value_counts().idxmax()
mean_bmi_per_class = df.groupby('NObeyesdad')['BMI'].mean().reindex(OBESITY_ORDER)
faf_bmi_corr = df_encoded['FAF'].corr(df_encoded['BMI'])
fh_pct_yes = (df['family_history_with_overweight'] == 'yes').mean() * 100
most_common_transport = df['MTRANS'].value_counts().idxmax()

findings = []
findings.append(f"Most common obesity class: {most_common} ({df['NObeyesdad'].value_counts()[most_common]} records)")
findings.append(f"\nMean BMI per class:\n{mean_bmi_per_class.to_string()}")
findings.append(f"\nCorrelation between FAF and BMI: {faf_bmi_corr:.4f}")
findings.append(f"\nPercentage with family history of overweight: {fh_pct_yes:.1f}%")
findings.append(f"\nMost common transportation mode: {most_common_transport} ({df['MTRANS'].value_counts()[most_common_transport]} records)")

for f in findings:
    print(f)

with open('outputs/data/eda_findings.txt', 'w') as f:
    f.write('\n'.join(findings))

print("\n" + "=" * 60)
print("PHASE 1 COMPLETE: All 8 EDA charts saved to outputs/charts/")
print("=" * 60)
