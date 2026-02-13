"""
Machine Learning Training Pipeline Module.

This module executes the training and optimization of the K-Medoids Clustering model.
Key processes:
1. Data Loading: Reads processed data from the ETL stage.
2. Feature Engineering: Applies Log transformation to amount fields and Standard Scaling.
3. Optimization: Runs the Elbow Method and Silhouette Score analysis to determine optimal K.
4. Model Training: Fits the K-Medoids model with the selected K.
5. Evaluation: Calculates final quality metrics (Silhouette, WCSS).
6. Export: Saves the trained model results (clusters, centroids) and visualization data.
"""

import pandas as pd
import numpy as np
import yaml
import logging
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn_extra.cluster import KMedoids
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score, adjusted_rand_score
from sklearn.utils import resample
import json

# Configure module-level logger
logger = logging.getLogger(__name__)

def train_kmedoids(config_path):
    """
    Executes the K-Medoids training workflow.

    Args:
        config_path (str): Path to the YAML configuration file.
    """
    # Load Configuration
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    data_path = Path(config['data']['processed_path'])
    if not data_path.exists():
        logger.error(f"Input data file not found: {data_path}")
        return

    logger.info("Loading preprocessed data...")
    df = pd.read_csv(data_path)
    
    # Feature Selection
    features = config['model']['features']
    logger.info(f"Selected Features: {features}")
    
    X = df[features].dropna().copy()
    
    # --- FEATURE ENGINEERING ---
    # Log Transformation on Amount (index 0) to reduce skewness
    logger.info("Applying Log Transformation to Amount Feature...")
    X[features[0]] = np.log1p(X[features[0]])
    
    # Standardization
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Directory Setup
    plots_dir = Path(config['model']['plots_path'])
    plots_dir.mkdir(parents=True, exist_ok=True)
    predictions_dir = Path(config['model']['output_path']).parent
    predictions_dir.mkdir(parents=True, exist_ok=True)
    
    # --- PHASE 1: HYPERPARAMETER OPTIMIZATION (ELBOW METHOD) ---
    max_k = config['model']['max_k']
    logger.info(f"Running Optimization (K=1 to {max_k})...")
    
    metrics_data = []
    wcss_list = []
    
    for k in range(1, max_k + 1):
        kmedoids = KMedoids(n_clusters=k, init='k-medoids++', random_state=config['model']['random_state'])
        labels = kmedoids.fit_predict(X_scaled)
        wcss = kmedoids.inertia_
        wcss_list.append(wcss)
        
        sil_score = 0
        if k > 1:
            sil_score = silhouette_score(X_scaled, labels)
            
        metrics_data.append({
            "k": k,
            "wcss": wcss,
            "silhouette": sil_score
        })
        
    # Save Validation Metrics
    with open(predictions_dir / "metrics.json", "w") as f:
        json.dump(metrics_data, f)

    # Plot Elbow Method
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, max_k + 1), wcss_list, marker='o', linestyle='--')
    plt.title('Elbow Method (Log-Transformed Data)')
    plt.xlabel('Number of Clusters (K)')
    plt.ylabel('WCSS')
    plt.grid(True)
    plt.savefig(plots_dir / 'elbow_method.png')
    plt.close()
    
    # --- PHASE 2: FINAL MODEL TRAINING ---
    optimal_k = config['model']['optimal_k']
    logger.info(f"Training Final Model with K={optimal_k}...")
    
    kmedoids = KMedoids(n_clusters=optimal_k, init='k-medoids++', random_state=config['model']['random_state'])
    X['Cluster'] = kmedoids.fit_predict(X_scaled)
    labels = X['Cluster'].values
    
    # Robustness Metrics: Centroid Distance (Interpretability)
    # Note: X_scaled and cluster_centers_ share the same scale
    distances = np.linalg.norm(X_scaled - kmedoids.cluster_centers_[labels], axis=1)
    
    # Final Silhouette Score
    final_sil_score = silhouette_score(X_scaled, labels)
    final_dbi_score = davies_bouldin_score(X_scaled, labels)
    final_ch_score = calinski_harabasz_score(X_scaled, labels)
    
    logger.info(f"Final Model Quality (Silhouette): {final_sil_score:.4f}")
    logger.info(f"Final Model Quality (Davies-Bouldin): {final_dbi_score:.4f}")
    logger.info(f"Final Model Quality (Calinski-Harabasz): {final_ch_score:.4f}")

    # --- RIGOROUS VALIDATION (Bootstrap 20 seeds) ---
    logger.info("Running Bootstrap Stability Analysis (20 iterations)...")
    
    stability_scores = []
    sil_scores = []
    dbi_scores = []
    
    for i in range(20):
        # 1. Resample Data (Bootstrap with replacement)
        X_resampled, _ = resample(X_scaled, labels, random_state=42 + i)
        
        # 2. Fit K-Medoids on Resampled Data
        km_stable = KMedoids(n_clusters=optimal_k, init='k-medoids++', random_state=42 + i)
        labels_stable_pred = km_stable.fit_predict(X_resampled)
        
        # 3. Predict Original Data using the Resampled Model (to compare vs original labels)
        predicted_orig_labels = km_stable.predict(X_scaled)
        
        # 4. Compare Original Labels vs Labels predicted by model trained on resampled data
        ari = adjusted_rand_score(labels, predicted_orig_labels)
        stability_scores.append(ari)
        
        # Metric Stats (on resampled distribution to see variance)
        sil_scores.append(silhouette_score(X_resampled, labels_stable_pred))
        dbi_scores.append(davies_bouldin_score(X_resampled, labels_stable_pred))
        
    avg_stability = np.mean(stability_scores)
    std_stability = np.std(stability_scores)
    min_ari = np.min(stability_scores)
    max_ari = np.max(stability_scores)
    
    # Statistical Ranges
    sil_mean = np.mean(sil_scores)
    sil_std = np.std(sil_scores)
    dbi_mean = np.mean(dbi_scores)
    dbi_std = np.std(dbi_scores)

    logger.info(f"Stability (ARI): {avg_stability:.4f} +/- {std_stability:.4f}")
    logger.info(f"Silhouette Stats: {sil_mean:.4f} +/- {sil_std:.4f}")
    
    # --- NEGATIVE SILHOUETTE % & BALANCE ---
    from sklearn.metrics import silhouette_samples
    sample_silhouette_values = silhouette_samples(X_scaled, labels)
    neg_sil_pct = (np.sum(sample_silhouette_values < 0) / len(labels)) * 100
    
    # Cluster Balance (CV of sizes)
    unique, counts = np.unique(labels, return_counts=True)
    size_cv = np.std(counts) / np.mean(counts)
    min_size_pct = (np.min(counts) / len(labels)) * 100
    max_size_pct = (np.max(counts) / len(labels)) * 100

    logger.info(f"Negative Silhouette: {neg_sil_pct:.2f}%")
    logger.info(f"Cluster Sizes CV: {size_cv:.4f} (Min: {min_size_pct:.1f}%, Max: {max_size_pct:.1f}%)")

    # Save Advanced Metrics
    adv_metrics = {
        "silhouette": final_sil_score,
        "silhouette_mean": sil_mean,
        "silhouette_std": sil_std,
        "davies_bouldin": final_dbi_score,
        "davies_bouldin_mean": dbi_mean,
        "davies_bouldin_std": dbi_std,
        "calinski_harabasz": final_ch_score,
        "stability_ari": avg_stability,
        "stability_std": std_stability,
        "ari_min": min_ari,
        "ari_max": max_ari,
        "neg_sil_pct": neg_sil_pct,
        "size_cv": size_cv,
        "min_size_pct": min_size_pct,
        "max_size_pct": max_size_pct,
        "inertia": kmedoids.inertia_,
        "iterations": kmedoids.n_iter_,
        "k": int(optimal_k)
    }
    
    with open(predictions_dir / "advanced_metrics.json", "w") as f:
        json.dump(adv_metrics, f)
    
    # --- PHASE 3: DATA EXPORT ---
    # Merge results back to original dataframe
    df_export = df.loc[X.index].copy()
    df_export['Cluster'] = labels
    df_export['Distancia_Centroide'] = distances
    
    # Select Columns for Export
    export_cols = ['Pais', 'Anio', 'Monto_Aprobado', 'CANTIDAD_APROBACIONES', 'Cluster', 'Distancia_Centroide']
    if 'Sector_Economico' in df_export.columns:
        export_cols.append('Sector_Economico')
    if 'Mes' in df_export.columns:
        export_cols.append('Mes')
        
    clustered_data = df_export[export_cols].to_dict(orient='records')
    
    # Save Main Clusters JSON
    with open(predictions_dir / "clusters.json", "w", encoding='utf-8') as f:
        json.dump(clustered_data, f)

    # Save Centroids Data (Inverse Transformed for Interpretability)
    centers_scaled = kmedoids.cluster_centers_
    centers_log = scaler.inverse_transform(centers_scaled)
    centers_real = centers_log.copy()
    centers_real[:, 0] = np.expm1(centers_real[:, 0]) # Revert Log
    
    centroids_data = []
    for i, center in enumerate(centers_real):
        centroids_data.append({
            "cluster": i,
            "monto": center[0],
            "aprobaciones": center[1]
        })
        
    with open(predictions_dir / "centroids.json", "w") as f:
        json.dump(centroids_data, f)
        
    # Save Final CSV Report
    df_export.to_csv(config['model']['output_path'], index=False)
    logger.info(f"Results successfully saved to: {config['model']['output_path']}")

if __name__ == "__main__":
    # For standalone testing
    train_kmedoids("config/local.yaml")

