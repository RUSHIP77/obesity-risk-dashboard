import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import joblib

print("=" * 60)
print("PHASE 6: K-MEANS CLUSTERING")
print("=" * 60)

OBESITY_ORDER = ['Insufficient_Weight', 'Normal_Weight', 'Overweight_Level_I',
                 'Overweight_Level_II', 'Obesity_Type_I', 'Obesity_Type_II', 'Obesity_Type_III']

# ============================================================
# Step 6.1: Load Data
# ============================================================
print("\n[6.1] Loading clustering data...")
X_cluster_scaled = joblib.load('outputs/data/clustering_data_scaled.pkl')
X_cluster = joblib.load('outputs/data/clustering_data.pkl')
y_bmi = joblib.load('outputs/data/y_bmi.pkl')
y_class = joblib.load('outputs/data/y_class.pkl')
cluster_feature_names = joblib.load('outputs/models/feature_names_clustering.pkl')

print(f"Clustering data shape: {X_cluster_scaled.shape}")

# ============================================================
# Step 6.2: Elbow Method
# ============================================================
print("\n[6.2] Elbow Method...")
K_range = range(2, 11)
inertias = []
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_cluster_scaled)
    inertias.append(km.inertia_)
    print(f"  k={k}: Inertia={km.inertia_:.2f}")

# Chart 18: Elbow Plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(list(K_range), inertias, 'b-o', markersize=8)
ax.set_xlabel('Number of Clusters (k)')
ax.set_ylabel('Inertia')
ax.set_title('K-Means: Elbow Method for Optimal k')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/charts/18_kmeans_elbow.png', dpi=150)
plt.close()

# ============================================================
# Step 6.3: Silhouette Analysis
# ============================================================
print("\n[6.3] Silhouette Analysis...")
silhouette_scores = []
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_cluster_scaled)
    sil = silhouette_score(X_cluster_scaled, labels)
    silhouette_scores.append(sil)
    print(f"  k={k}: Silhouette Score = {sil:.4f}")

best_k_cluster = list(K_range)[np.argmax(silhouette_scores)]
print(f"\nBest k by silhouette: {best_k_cluster} (score: {max(silhouette_scores):.4f})")

# Use k=4 if best_k is 2 (since 2 clusters isn't very informative)
if best_k_cluster == 2:
    best_k_cluster = 4
    print(f"Overriding to k={best_k_cluster} for more meaningful clusters")

# Chart 19: Silhouette Scores
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(list(K_range), silhouette_scores, 'g-o', markersize=8)
ax.plot(best_k_cluster, silhouette_scores[best_k_cluster - 2], 'ro', markersize=12,
        label=f'Selected k={best_k_cluster}')
ax.set_xlabel('Number of Clusters (k)')
ax.set_ylabel('Silhouette Score')
ax.set_title('K-Means: Silhouette Score vs Number of Clusters')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/charts/19_kmeans_silhouette.png', dpi=150)
plt.close()

# ============================================================
# Step 6.4: Train Final Model
# ============================================================
print(f"\n[6.4] Training final K-Means with k={best_k_cluster}...")
final_km = KMeans(n_clusters=best_k_cluster, random_state=42, n_init=10)
cluster_labels = final_km.fit_predict(X_cluster_scaled)
print(f"Cluster distribution: {pd.Series(cluster_labels).value_counts().sort_index().to_dict()}")

# ============================================================
# Step 6.5: PCA Visualization
# ============================================================
print("\n[6.5] PCA Visualization...")
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_cluster_scaled)
print(f"Explained variance: PC1={pca.explained_variance_ratio_[0]:.4f}, PC2={pca.explained_variance_ratio_[1]:.4f}")

# Chart 20: PCA Cluster Plot
cluster_colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0', '#00BCD4', '#795548']
fig, ax = plt.subplots(figsize=(10, 8))
for i in range(best_k_cluster):
    mask = cluster_labels == i
    ax.scatter(X_pca[mask, 0], X_pca[mask, 1], c=cluster_colors[i],
               label=f'Cluster {i}', alpha=0.6, s=30)

# Add centroids
centroids_pca = pca.transform(final_km.cluster_centers_)
ax.scatter(centroids_pca[:, 0], centroids_pca[:, 1], c='black', marker='X',
           s=200, linewidths=2, edgecolors='white', label='Centroids')

ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)')
ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)')
ax.set_title('K-Means Clusters (PCA Projection)')
ax.legend()
plt.tight_layout()
plt.savefig('outputs/charts/20_kmeans_pca.png', dpi=150)
plt.close()

# ============================================================
# Step 6.6: Cluster Profiling
# ============================================================
print("\n[6.6] Cluster Profiling...")
df_clustered = X_cluster.copy()
df_clustered['Cluster'] = cluster_labels
df_clustered['BMI'] = y_bmi.values
df_clustered['Obesity_Level'] = y_class.values

cluster_profiles = df_clustered.groupby('Cluster').mean()
print("\nCluster Profiles (Mean values):")
print(cluster_profiles.to_string())
cluster_profiles.to_csv('outputs/data/cluster_profiles.csv')

# ============================================================
# Step 6.7: Name Clusters
# ============================================================
print("\n[6.7] Naming clusters...")

cluster_names = {}
for i in range(best_k_cluster):
    profile = cluster_profiles.loc[i]
    faf_val = profile['FAF']
    tue_val = profile['TUE']
    fcvc_val = profile['FCVC']
    favc_val = profile['FAVC']
    bmi_val = profile['BMI']

    if faf_val == cluster_profiles['FAF'].min() and tue_val >= cluster_profiles['TUE'].median():
        name = "High-Risk Sedentary"
    elif faf_val == cluster_profiles['FAF'].max() and fcvc_val >= cluster_profiles['FCVC'].median():
        name = "Active Healthy"
    elif favc_val >= cluster_profiles['FAVC'].median() and fcvc_val <= cluster_profiles['FCVC'].median():
        name = "Poor Diet Risk"
    else:
        name = "Moderate Risk"

    # Ensure unique names
    if name in cluster_names.values():
        name = f"{name} (Group {i})"

    cluster_names[i] = name
    print(f"  Cluster {i}: {name} (avg BMI={bmi_val:.1f}, FAF={faf_val:.2f}, TUE={tue_val:.2f})")

with open('outputs/data/cluster_names.txt', 'w') as f:
    for k, v in cluster_names.items():
        f.write(f"Cluster {k}: {v}\n")

joblib.dump(cluster_names, 'outputs/data/cluster_names.pkl')

# Chart 21: Radar Chart for Cluster Profiles
print("  Generating Chart 21: Cluster Radar Chart...")
radar_features = ['FAF', 'TUE', 'FCVC', 'FAVC', 'CH2O', 'NCP', 'CAEC', 'CALC']
radar_data = cluster_profiles[radar_features]

# Normalize to 0-1 for radar chart
radar_normalized = (radar_data - radar_data.min()) / (radar_data.max() - radar_data.min() + 1e-10)

angles = np.linspace(0, 2 * np.pi, len(radar_features), endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
for i in range(best_k_cluster):
    values = radar_normalized.loc[i].tolist()
    values += values[:1]
    ax.plot(angles, values, 'o-', linewidth=2, label=f'Cluster {i}: {cluster_names[i]}',
            color=cluster_colors[i])
    ax.fill(angles, values, alpha=0.1, color=cluster_colors[i])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(radar_features, fontsize=10)
ax.set_title('Cluster Risk Profiles — Lifestyle Factor Comparison', fontsize=14, pad=20)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.tight_layout()
plt.savefig('outputs/charts/21_cluster_radar.png', dpi=150, bbox_inches='tight')
plt.close()

# Chart 22: Cluster Obesity Distribution
print("  Generating Chart 22: Cluster Obesity Distribution...")
reverse_label_mapping = joblib.load('outputs/models/reverse_label_mapping.pkl')
df_clustered['Obesity_Name'] = df_clustered['Obesity_Level'].map(reverse_label_mapping)

fig, ax = plt.subplots(figsize=(12, 6))
ct = pd.crosstab(df_clustered['Cluster'], df_clustered['Obesity_Name'])
ct = ct.reindex(columns=OBESITY_ORDER, fill_value=0)
ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100

OBESITY_COLORS_LIST = ['#2196F3', '#4CAF50', '#FFC107', '#FF9800', '#FF5722', '#F44336', '#B71C1C']
ct_pct.plot(kind='bar', stacked=True, color=OBESITY_COLORS_LIST, ax=ax)
ax.set_xlabel('Cluster')
ax.set_ylabel('Percentage (%)')
ax.set_title('Obesity Level Distribution by Behavioral Cluster')
ax.legend(title='Obesity Level', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
ax.set_xticklabels([f'Cluster {i}\n{cluster_names[i]}' for i in range(best_k_cluster)],
                   rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig('outputs/charts/22_cluster_obesity_distribution.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================
# Step 6.8: Save Model
# ============================================================
print("\n[6.8] Saving models...")
joblib.dump(final_km, 'outputs/models/kmeans_model.pkl')
joblib.dump(pca, 'outputs/models/pca_model.pkl')
joblib.dump(cluster_labels, 'outputs/data/cluster_labels.pkl')
joblib.dump(best_k_cluster, 'outputs/data/best_k_cluster.pkl')

print("\n" + "=" * 60)
print(f"PHASE 6 COMPLETE: K-Means model (k={best_k_cluster}) trained and saved")
print(f"Best silhouette score: {max(silhouette_scores):.4f}")
print("=" * 60)
