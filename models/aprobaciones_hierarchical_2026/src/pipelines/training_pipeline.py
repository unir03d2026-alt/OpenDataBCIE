"""
Machine Learning Training Pipeline Module.

This module executes the training and optimization of the Agglomerative Hierarchical Model.
Key processes:
1. Data Loading: Reads processed data.
2. Feature Engineering: Log transformation and Standard Scaling.
3. Optimization: Silhouette analysis for K selection (optional).
4. Model Training: Fits AgglomerativeClustering (Ward).
5. Evaluation: Calculates Silhouette, DB, CH, and Stability.
6. Export: Saves clusters and Dendrogram data.
"""

import pandas as pd
import numpy as np
import yaml
import logging
import json
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score, adjusted_rand_score
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt
import plotly.figure_factory as ff

# Configure module-level logger
logger = logging.getLogger(__name__)

def train_hierarchical(config_path):
    """
    Executes the Hierarchical Clustering training workflow.
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
    
    # --- PHASE 1: HYPERPARAMETER OPTIMIZATION (Silhouette) ---
    max_k = config['model'].get('max_k', 10)
    logger.info(f"Running Optimization (K=2 to {max_k})...")
    
    best_score = -1
    best_k = 2
    metrics_data = []
    
    for k in range(2, max_k + 1):
        model = AgglomerativeClustering(n_clusters=k, linkage='ward')
        labels = model.fit_predict(X_scaled)
        
        sil = silhouette_score(X_scaled, labels)
        metrics_data.append({"k": k, "silhouette": sil})
        
        if sil > best_score:
            best_score = sil
            best_k = k
            
    logger.info(f"Best K found: {best_k} (Silhouette: {best_score:.4f})")
    
    # Override K if specified in config validation
    if 'n_clusters' in config['model'] and config['model']['n_clusters'] > 0:
        best_k = config['model']['n_clusters']
        logger.info(f"Using Configured K: {best_k}")

    # --- PHASE 2: FINAL MODEL TRAINING ---
    logger.info(f"Training Final Linkage Matrix (Ward)...")
    
    # Compute linkage matrix for Dendrogram
    Z = linkage(X_scaled, method='ward')
    
    # Fit Final Model
    logger.info(f"Fitting Agglomerative Model with K={best_k}...")
    hc_final = AgglomerativeClustering(n_clusters=best_k, linkage='ward')
    labels = hc_final.fit_predict(X_scaled)
    X['Cluster'] = labels
    
    # Final Metrics
    final_sil = silhouette_score(X_scaled, labels)
    final_dbi = davies_bouldin_score(X_scaled, labels)
    final_ch = calinski_harabasz_score(X_scaled, labels)

    # --- RIGOROUS VALIDATION (Stability) ---
    logger.info("Running Stability Analysis (Subsampling)...")
    stability_scores = []
    n_samples = len(X_scaled)
    subset_size = int(n_samples * 0.90) 
    
    for i in range(20):
        try:
            indices = np.random.choice(n_samples, subset_size, replace=False)
            X_sub = X_scaled[indices]
            model_sub = AgglomerativeClustering(n_clusters=best_k, linkage='ward')
            labels_sub = model_sub.fit_predict(X_sub)
            labels_orig_subset = labels[indices]
            ari = adjusted_rand_score(labels_orig_subset, labels_sub)
            stability_scores.append(ari)
        except:
            continue
            
    avg_stability = np.mean(stability_scores) if stability_scores else 0
    
    # --- BALANCE ---
    unique, counts = np.unique(labels, return_counts=True)
    size_cv = np.std(counts) / np.mean(counts) if len(counts) > 0 else 0
    
    # Save Metrics
    adv_metrics = {
        "k": int(best_k),
        "silhouette": final_sil,
        "davies_bouldin": final_dbi,
        "calinski_harabasz": final_ch,
        "stability_ari": avg_stability,
        "size_cv": size_cv
    }
    
    with open(predictions_dir / "advanced_metrics.json", "w") as f:
        json.dump(adv_metrics, f)

    # --- EXPORT RESULTS ---
    df_export = df.loc[X.index].copy()
    df_export['Cluster'] = labels
    
    df_export.to_csv(config['model']['output_path'], index=False)
    
    # Save Dendrogram Data for Plotly (JSON)
    # Plotly's create_dendrogram returns a figure. We can save the figure data.
    logger.info("Generating Dendrogram JSON...")
    
    # We use a subset for dendrogram if data is too large, but for 600 rows it's fine.
    # Create Figure Factory dendrogram
    names = df_export['Pais'].astype(str).values
    fig = ff.create_dendrogram(X_scaled, labels=names)
    
    # Save chart JSON
    dendro_json_path = predictions_dir / "dendrogram_chart.json"
    with open(dendro_json_path, 'w') as f:
        # Convert to dictionary using plotly utils or simple json dump if serializable
        # We save the 'data' and 'layout' components needed for Plotly.newPlot
        # Remove big arrays to keep file size manageable if needed, but here we keep full data.
        json.dump(json.loads(fig.to_json()), f)
        
    logger.info(f"Results saved to: {config['model']['output_path']}")

if __name__ == "__main__":
    train_hierarchical("config/local.yaml")
