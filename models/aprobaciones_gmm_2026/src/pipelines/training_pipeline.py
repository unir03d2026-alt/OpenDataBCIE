"""
Machine Learning Training Pipeline Module.

This module executes the training and optimization of the Gaussian Mixture Model (GMM).
Key processes:
1. Data Loading: Reads processed data.
2. Feature Engineering: Log transformation and Standard Scaling.
3. Optimization: Iterates K components to find optimal K based on AIC/BIC.
4. Model Training: Fits GaussianMixture with selected K.
5. Evaluation: Calculates Silhouette, AIC, BIC, and Average Probability.
6. Stability: Evaluates robustness using subsampling.
7. Export: Saves clusters, centroids, and probability scores.
"""

import pandas as pd
import numpy as np
import yaml
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score, adjusted_rand_score
from scipy.stats import entropy
import json

# Configure module-level logger
logger = logging.getLogger(__name__)

def train_gmm(config_path):
    """
    Executes the Gaussian Mixture Model training workflow.
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
    logger.info("Applying Log Transformation to Amount Feature...")
    X[features[0]] = np.log1p(X[features[0]])
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Directory Setup
    plots_dir = Path(config['model']['plots_path'])
    plots_dir.mkdir(parents=True, exist_ok=True)
    predictions_dir = Path(config['model']['output_path']).parent
    predictions_dir.mkdir(parents=True, exist_ok=True)
    
    # --- PHASE 1: HYPERPARAMETER OPTIMIZATION (AIC/BIC) ---
    max_k = config['model']['max_k']
    logger.info(f"Running Optimization (Components=1 to {max_k})...")
    
    metrics_data = []
    
    aic_scores = []
    bic_scores = []
    
    # Optimization loop
    for k in range(1, max_k + 1):
        gmm = GaussianMixture(n_components=k, random_state=42, n_init=10)
        gmm.fit(X_scaled)
        
        aic = gmm.aic(X_scaled)
        bic = gmm.bic(X_scaled)
        
        aic_scores.append(aic)
        bic_scores.append(bic)
        
        metrics_data.append({
            "k": k,
            "aic": aic,
            "bic": bic
        })
        
    # Determine Optimal K (Elbow method on BIC or minimum BIC)
    # Theoretically minimal BIC is best, but sometimes it overfits. 
    # We will pick the K with minimum BIC for this implementation.
    optimal_k = np.argmin(bic_scores) + 1 # +1 because range starts at 1
    
    # Save Validation Metrics (Optimization History)
    opt_history_path = predictions_dir / "optimization_history.json"
    with open(opt_history_path, "w") as f:
        json.dump(metrics_data, f)
        
    with open(predictions_dir / "metrics.json", "w") as f:
        json.dump(metrics_data, f)
        
    # Plot AIC/BIC
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, max_k + 1), aic_scores, marker='o', label='AIC')
    plt.plot(range(1, max_k + 1), bic_scores, marker='x', label='BIC')
    plt.title('GMM Selection (AIC/BIC)')
    plt.xlabel('Number of Components')
    plt.ylabel('Score (Lower is Better)')
    plt.legend()
    plt.grid(True)
    plt.savefig(plots_dir / 'optimization_aic_bic.png')
    plt.close()
    
    # --- PHASE 2: FINAL MODEL TRAINING ---
    # Override optimal_k if specified in config
    if 'optimal_k' in config['model'] and config['model']['optimal_k']:
        optimal_k = config['model']['optimal_k']
        
    logger.info(f"Training Final Model with K={optimal_k}...")
    
    gmm_final = GaussianMixture(n_components=optimal_k, random_state=42, n_init=10)
    gmm_final.fit(X_scaled)
    
    # Predict clusters
    labels = gmm_final.predict(X_scaled)
    X['Cluster'] = labels
    
    # Soft Clustering Probabilities (Entropy Calculation)
    probs = gmm_final.predict_proba(X_scaled)
    max_probs = probs.max(axis=1) # Probability of belonging to the assigned cluster
    avg_prob = np.mean(max_probs)
    
    # Calculate Entropy (Uncertainty Measure)
    # H(x) = -sum(p * log(p))
    sample_entropy = entropy(probs, axis=1)
    avg_model_entropy = np.mean(sample_entropy)
    
    # Calculate Centroids
    cluster_centers_ = gmm_final.means_
        
    # Final Standard Metrics
    # Note: Silhouette is not natively "GMM" (which deals with density), but requested for comparison.
    if optimal_k > 1:
        final_sil = silhouette_score(X_scaled, labels)
        final_dbi = davies_bouldin_score(X_scaled, labels)
        final_ch = calinski_harabasz_score(X_scaled, labels)
    else:
        final_sil, final_dbi, final_ch = 0, 0, 0
    
    logger.info(f"Final Model (K={optimal_k}) - Avg Prob: {avg_prob:.4f}, AIC: {gmm_final.aic(X_scaled):.0f}")

    # --- RIGOROUS VALIDATION (Subsampling Stability) ---
    logger.info("Running Stability Analysis (Subsampling)...")
    
    stability_scores = []
    n_samples = len(X_scaled)
    subset_size = int(n_samples * 0.90) 
    
    for i in range(20):
        indices = np.random.choice(n_samples, subset_size, replace=False)
        X_sub = X_scaled[indices]
        
        gmm_stable = GaussianMixture(n_components=optimal_k, random_state=42+i, n_init=1)
        gmm_stable.fit(X_sub)
        labels_sub = gmm_stable.predict(X_sub)
        
        labels_orig_subset = labels[indices]
        
        ari = adjusted_rand_score(labels_orig_subset, labels_sub)
        stability_scores.append(ari)
        
    avg_stability = np.mean(stability_scores)
    
    # --- BALANCE ---
    unique, counts = np.unique(labels, return_counts=True)
    if len(counts) > 0:
        size_cv = np.std(counts) / np.mean(counts)
        min_size_pct = (np.min(counts) / len(labels)) * 100
    else:
        size_cv, min_size_pct = 0, 0
    
    # Save Advanced Metrics
    adv_metrics = {
        "aic": gmm_final.aic(X_scaled),
        "bic": gmm_final.bic(X_scaled),
        "avg_probability": avg_prob,
        "avg_entropy": avg_model_entropy,  # NEW
        "silhouette": final_sil,
        "davies_bouldin": final_dbi,
        "calinski_harabasz": final_ch,
        "stability_ari": avg_stability,
        "size_cv": size_cv,
        "min_size_pct": min_size_pct,
        "k": int(optimal_k)
    }
    
    with open(predictions_dir / "advanced_metrics.json", "w") as f:
        json.dump(adv_metrics, f)

    # --- EXPORT RESULTS ---
    df_export = df.loc[X.index].copy()
    df_export['Cluster'] = labels
    df_export['Probabilidad_Asignacion'] = max_probs
    df_export['Entropia'] = sample_entropy # NEW
    
    export_cols = ['Pais', 'Anio', 'Monto_Aprobado', 'CANTIDAD_APROBACIONES', 'Cluster', 'Probabilidad_Asignacion', 'Entropia']
    if 'Sector_Economico' in df_export.columns: export_cols.append('Sector_Economico')
        
    clustered_data = df_export[export_cols].to_dict(orient='records')
    
    with open(predictions_dir / "clusters.json", "w", encoding='utf-8') as f:
        json.dump(clustered_data, f)

    # Save Centroids (Mean of Gaussian components)
    centers_log = scaler.inverse_transform(cluster_centers_)
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
        
    # --- CALCULATE PROFILE SCORES (0-100) ---
    max_monto = np.max(centers_real[:, 0])
    max_aprob = np.max(centers_real[:, 1])
    
    profile_data = []
    for i, center in enumerate(centers_real):
        score_monto = (center[0] / max_monto) * 100 if max_monto > 0 else 0
        score_aprob = (center[1] / max_aprob) * 100 if max_aprob > 0 else 0
        
        # Calculate Risk Score (inverse of Probability confidence, heuristic)
        # We need the avg probability for this cluster
        subset_probs = df_export[df_export['Cluster'] == i]['Probabilidad_Asignacion']
        avg_conf = subset_probs.mean() if not subset_probs.empty else 0
        score_risk = (1 - avg_conf) * 100 # Higher Risk if lower confidence
        
        profile_data.append({
            "cluster": i,
            "score_monto": round(score_monto, 1),
            "score_aprob": round(score_aprob, 1),
            "score_risk": round(score_risk, 1)
        })
        
    with open(predictions_dir / "profile_scores.json", "w") as f:
        json.dump(profile_data, f)
        
    # Save Covariances for Confidence Ellipses
    # GMM 'full' covariances are (n_components, n_features, n_features)
    # We need to export them to be usable in JS
    covs = gmm_final.covariances_
    covariances_data = []
    
    for i in range(optimal_k):
        # We only need the 2D covariance for the 2 main features (LogAmount, Approvals)
        # Assuming X_scaled columns are in that order.
        c_matrix = covs[i].tolist()
        covariances_data.append({
            "cluster": i,
            "covariance": c_matrix
        })
        
    with open(predictions_dir / "covariances.json", "w") as f:
        json.dump(covariances_data, f)
        
    df_export.to_csv(config['model']['output_path'], index=False)
    logger.info(f"Results saved to: {config['model']['output_path']}")

if __name__ == "__main__":
    train_gmm("config/local.yaml")
