"""
DBSCAN Hyperparameter Optimization via Grid Search.

Explores eps and min_samples combinations to find the configuration
that maximizes Silhouette Score while maintaining:
- A meaningful number of clusters (3-10)
- Acceptable noise level (<40%)
- Good cluster balance

Output: optimization_results.json with all iterations + recommended params.
"""

import yaml
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def optimize_dbscan(config_path="config/local.yaml"):
    """Run grid search over DBSCAN hyperparameters."""
    
    # Load config
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # Load data
    processed_path = Path(config["data"]["processed_path"])
    if not processed_path.exists():
        raise FileNotFoundError(f"Data not found: {processed_path}")
    
    df = pd.read_csv(processed_path)
    features = config["model"]["features"]
    log_col = config["model"].get("log_transform_feature")
    
    X = df[features].copy()
    if log_col and log_col in X.columns:
        X[log_col] = np.log1p(X[log_col])
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    logger.info(f"Data loaded: {len(X_scaled)} samples, {X_scaled.shape[1]} features")
    logger.info(f"Feature ranges (scaled): min={X_scaled.min(axis=0)}, max={X_scaled.max(axis=0)}")
    
    # ---- GRID SEARCH ----
    # eps: controls neighborhood radius (smaller = more clusters, more noise)
    # min_samples: controls density threshold (larger = fewer clusters, more noise)
    
    eps_values = [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.80, 1.0]
    min_samples_values = [3, 4, 5, 7, 10]
    
    results = []
    iteration = 0
    
    for eps in eps_values:
        for ms in min_samples_values:
            iteration += 1
            
            clusterer = DBSCAN(eps=eps, min_samples=ms, metric='euclidean', n_jobs=-1)
            labels = clusterer.fit_predict(X_scaled)
            
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            n_noise = int((labels == -1).sum())
            noise_pct = (n_noise / len(labels)) * 100
            
            # Metrics (only computable with >= 2 clusters)
            sil = -1.0
            dbi = 99.0
            ch = 0.0
            
            if n_clusters >= 2:
                valid_mask = labels != -1
                X_valid = X_scaled[valid_mask]
                labels_valid = labels[valid_mask]
                
                if len(set(labels_valid)) >= 2:
                    sil = silhouette_score(X_valid, labels_valid)
                    dbi = davies_bouldin_score(X_valid, labels_valid)
                    ch = calinski_harabasz_score(X_valid, labels_valid)
            
            # Cluster sizes
            cluster_counts = pd.Series(labels[labels != -1]).value_counts().sort_index()
            sizes = cluster_counts.tolist() if len(cluster_counts) > 0 else []
            
            # Balance metric (CV of cluster sizes, lower = more balanced)
            cv = 0.0
            if len(sizes) > 1:
                mean_size = np.mean(sizes)
                std_size = np.std(sizes)
                cv = std_size / mean_size if mean_size > 0 else 99
            
            # Composite score for ranking
            # Penalize: too few clusters (<3), too many (>10), high noise (>40%), poor silhouette
            penalty = 0
            if n_clusters < 3:
                penalty += 0.3
            if n_clusters > 10:
                penalty += 0.1
            if noise_pct > 40:
                penalty += 0.2
            if noise_pct > 60:
                penalty += 0.3
            
            composite = max(0, sil - penalty) if sil > 0 else -1
            
            result = {
                "iteration": iteration,
                "eps": eps,
                "min_samples": ms,
                "n_clusters": n_clusters,
                "noise_pct": round(noise_pct, 1),
                "silhouette_score": round(sil, 4),
                "davies_bouldin": round(dbi, 4),
                "calinski_harabasz": round(ch, 2),
                "cluster_sizes": sizes,
                "balance_cv": round(cv, 3),
                "composite_score": round(composite, 4)
            }
            results.append(result)
            
            marker = " ★" if composite > 0.3 and 3 <= n_clusters <= 8 else ""
            logger.info(
                f"[{iteration:3d}] eps={eps:.2f} ms={ms:2d} → "
                f"K={n_clusters:2d} noise={noise_pct:5.1f}% "
                f"sil={sil:6.3f} dbi={dbi:5.2f} ch={ch:7.1f} "
                f"composite={composite:6.3f}{marker}"
            )
    
    # ---- RANKING ----
    # Sort by composite score (descending)
    ranked = sorted(results, key=lambda x: x["composite_score"], reverse=True)
    
    # Filter candidates: 3-8 clusters, noise < 40%, sil > 0
    candidates = [r for r in ranked if 3 <= r["n_clusters"] <= 8 and r["noise_pct"] < 40 and r["silhouette_score"] > 0]
    
    if not candidates:
        # Relax: try 2-10 clusters, noise < 50%
        candidates = [r for r in ranked if 2 <= r["n_clusters"] <= 10 and r["noise_pct"] < 50 and r["silhouette_score"] > 0]
    
    if not candidates:
        # Ultimate fallback
        candidates = [r for r in ranked if r["silhouette_score"] > 0]
    
    best = candidates[0] if candidates else ranked[0]
    
    logger.info("=" * 80)
    logger.info(f"🏆 BEST CONFIG: eps={best['eps']}, min_samples={best['min_samples']}")
    logger.info(f"   Clusters: {best['n_clusters']}, Noise: {best['noise_pct']}%")
    logger.info(f"   Silhouette: {best['silhouette_score']}, DBI: {best['davies_bouldin']}")
    logger.info(f"   Composite: {best['composite_score']}")
    logger.info(f"   Sizes: {best['cluster_sizes']}")
    logger.info("=" * 80)
    
    # ---- TOP 10 ----
    logger.info("\n🔝 TOP 10 Configurations:")
    for i, r in enumerate(candidates[:10]):
        logger.info(
            f"  #{i+1}: eps={r['eps']:.2f} ms={r['min_samples']} "
            f"K={r['n_clusters']} noise={r['noise_pct']}% "
            f"sil={r['silhouette_score']} composite={r['composite_score']}"
        )
    
    # ---- SAVE ----
    output = {
        "best_params": {
            "eps": best["eps"],
            "min_samples": best["min_samples"],
            "metric": "euclidean"
        },
        "best_metrics": {
            "n_clusters": best["n_clusters"],
            "noise_pct": best["noise_pct"],
            "silhouette_score": best["silhouette_score"],
            "davies_bouldin": best["davies_bouldin"],
            "calinski_harabasz": best["calinski_harabasz"],
            "cluster_sizes": best["cluster_sizes"],
            "composite_score": best["composite_score"]
        },
        "total_iterations": iteration,
        "all_results": results,
        "top_10": candidates[:10]
    }
    
    out_path = Path("data/04-predictions/optimization_results.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\nResults saved to: {out_path}")
    return output


if __name__ == "__main__":
    result = optimize_dbscan()
