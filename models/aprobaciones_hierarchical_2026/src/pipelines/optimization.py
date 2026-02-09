import hdbscan
import logging
import pandas as pd
import numpy as np
import yaml
import json
import itertools
from pathlib import Path
from sklearn.preprocessing import StandardScaler, RobustScaler

logger = logging.getLogger(__name__)

def run_optimization(config_path, run_id):
    """
    Runs a grid search for HDBSCAN hyperparameters.
    Iterates over min_cluster_size and min_samples.
    Logs results and returns the best configuration based on DBCV.
    """
    logger.info(f"Starting Hyperparameter Optimization. Run ID: {run_id}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Load Data
    processed_path = Path(config["data"]["processed_path"])
    df = pd.read_csv(processed_path)
    
    features = config["model"]["features"]
    log_col = config["model"].get("log_transform_feature")
    
    X = df[features].copy()
    if log_col and log_col in X.columns:
        X[log_col] = np.log1p(X[log_col])
        
    scaler_type = config["model"].get("scaler", "standard").lower()
    scaler = RobustScaler() if scaler_type == "robust" else StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Grid Definition
    # You can expand this grid as needed
    param_grid = {
        "min_cluster_size": list(range(15, 51)), # 15 to 50
        "min_samples": list(range(1, 21)),       # 1 to 20
        "metric": ["euclidean", "manhattan"],
        "cluster_selection_epsilon": [0.0, 0.1, 0.3],
        "cluster_selection_method": ["eom", "leaf"]
    }
    
    results = []
    
    keys, values = zip(*param_grid.items())
    combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    
    logger.info(f"Testing {len(combinations)} combinations...")
    
    for i, params in enumerate(combinations):
        mcs = params["min_cluster_size"]
        ms = params["min_samples"]
        metric = params["metric"]
        eps = params["cluster_selection_epsilon"]
        method = params["cluster_selection_method"]
        
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=mcs,
            min_samples=ms,
            metric=metric,
            cluster_selection_epsilon=eps,
            cluster_selection_method=method,
            gen_min_span_tree=True,
            core_dist_n_jobs=-1
        )
        try:
            clusterer.fit(X_scaled)
            labels = clusterer.labels_
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            noise_pct = (labels == -1).sum() / len(labels)
            # DBCV (Relative Validity)
            score = clusterer.relative_validity_
            
            # Additional heuristic: Penalize if too much noise
            score = score * (1 - noise_pct) # Balance density vs coverage
            
            results.append({
                "iteration": i,
                "min_cluster_size": mcs, 
                "min_samples": ms,
                "metric": metric,
                "epsilon": eps,
                "method": method,
                "n_clusters": n_clusters,
                "noise_pct": round(noise_pct * 100, 2),
                "dbcv_score": float(score)
            })
            # LOG LESS FREQUENTLY to avoid console spam (every 100 iters)
            if i % 100 == 0:
                logger.debug(f"Iter {i}: mcs={mcs}, ms={ms}, metric={metric} -> DBCV={score:.3f}")
            
        except Exception as e:
            logger.error(f"Failed optim config {params}: {e}")

    # Find Best
    df_results = pd.DataFrame(results)
    # Filter for reasonable cluster count (e.g., > 1) if desired. For now, strict best DBCV.
    df_results = df_results[df_results["n_clusters"] > 1]
    
    if df_results.empty:
        logger.warning("No valid configurations found (n_clusters > 1). Returning default.")
        best_params = {
            "min_cluster_size": 15, 
            "min_samples": 5, 
            "metric": "euclidean", 
            "cluster_selection_epsilon": 0.0,
            "cluster_selection_method": "eom"
        }
    else:
        best_run = df_results.loc[df_results["dbcv_score"].idxmax()]
        best_params = {
            "min_cluster_size": int(best_run["min_cluster_size"]),
            "min_samples": int(best_run["min_samples"]),
            "metric": str(best_run["metric"]),
            "cluster_selection_epsilon": float(best_run["epsilon"]),
            "cluster_selection_method": str(best_run["method"])
        }
        logger.info(f"Optimization Complete. Best Config: {best_params} (DBCV={best_run['dbcv_score']:.3f})")

    # Save Optimization Artifacts to Run Dir
    run_dir = Path(config["runs"]["output_root"]) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    
    with open(run_dir / "optimization_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    return best_params
