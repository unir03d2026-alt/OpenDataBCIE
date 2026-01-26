import yaml
import pandas as pd
import numpy as np
import hdbscan
import logging
import json
import time
import platform
import sklearn
from pathlib import Path
from sklearn.preprocessing import StandardScaler, RobustScaler
from joblib import dump
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score, adjusted_rand_score

# Configure module-level logger
logger = logging.getLogger(__name__)

def _run_dir(config, run_id):
    """Helper to resolve the specific run directory."""
    return Path(config["runs"]["output_root"]) / run_id

def compute_stability_ari(X, params, n_iterations=20, sample_frac=0.8, random_state=42):
    """
    Compute clustering stability using subsample ARI.
    
    Args:
        X: Feature matrix
        params: HDBSCAN parameters dict
        n_iterations: Number of subsample iterations
        sample_frac: Fraction of data to subsample
        random_state: Random seed for reproducibility
    
    Returns:
        dict with ari_mean, ari_std, and ari_scores list
    """
    np.random.seed(random_state)
    n_samples = len(X)
    subsample_size = int(n_samples * sample_frac)
    
    ari_scores = []
    base_labels = None
    
    for i in range(n_iterations):
        # Subsample
        idx = np.random.choice(n_samples, subsample_size, replace=False)
        X_sub = X[idx]
        
        # Cluster
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=params.get('min_cluster_size', 5),
            min_samples=params.get('min_samples', 1),
            metric=params.get('metric', 'euclidean'),
            cluster_selection_epsilon=params.get('cluster_selection_epsilon', 0.0),
            cluster_selection_method=params.get('cluster_selection_method', 'eom')
        )
        labels_sub = clusterer.fit_predict(X_sub)
        
        if i == 0:
            base_labels = labels_sub
        else:
            # Calculate ARI (excluding noise points for cleaner comparison)
            valid_mask = (base_labels != -1) & (labels_sub != -1)
            if valid_mask.sum() > 1:  # Need at least 2 points
                ari = adjusted_rand_score(base_labels[valid_mask], labels_sub[valid_mask])
                ari_scores.append(ari)
    
    if len(ari_scores) == 0:
        return {"ari_mean": 0.0, "ari_std": 0.0, "ari_scores": []}
    
    return {
        "ari_mean": float(np.mean(ari_scores)),
        "ari_std": float(np.std(ari_scores)),
        "ari_scores": [float(x) for x in ari_scores]
    }

def train_hdbscan(config_path, run_id, params_override=None):
    """
    Executes the HDBSCAN training pipeline.
    
    Args:
        config_path (str): Path to the YAML configuration file.
        run_id (str): Unique identifier for this execution run.
        params_override (dict): Optional dictionary to override config params (e.g. from optimization).
    """
    logger.info(f"Starting HDBSCAN Training. Run ID: {run_id}")
    t0 = time.time()
    
    # 1. Load Config
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 2. Setup Directories
    # Fallback if specific keys missing, but assuming config updated
    base_dir = Path(config["data"]["processed_path"]).parent
    processed_path = Path(config["data"]["processed_path"])
    
    run_dir = _run_dir(config, run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Run Output Directory: {run_dir}")

    # Artifact Paths
    csv_out = run_dir / f'{config["model"]["output_name"]}.csv'
    metrics_out = run_dir / "metrics.json"
    adv_out = run_dir / "advanced_metrics.json"
    profiles_out = run_dir / "cluster_profiles.json"
    outliers_out = run_dir / "outliers_top10.json"
    hist_out = run_dir / "outlier_histogram.json"
    model_out = run_dir / "model_hdbscan.joblib"
    scaler_out = run_dir / "scaler.joblib"
    spec_out = run_dir / "feature_spec.json"

    # 3. Load Data
    logger.info(f"Loading data from {processed_path}")
    if not processed_path.exists():
        raise FileNotFoundError(f"Processed data not found at {processed_path}")
    
    df = pd.read_csv(processed_path)
    
    # 4. Feature Engineering
    features = config["model"]["features"]
    log_col = config["model"].get("log_transform_feature")
    
    # Create feature matrix
    X = df[features].copy()
    
    # Apply Log Transform if configured
    if log_col and log_col in X.columns:
        logger.info(f"Applying log1p transform to: {log_col}")
        X[log_col] = np.log1p(X[log_col])

    # Scaling
    scaler_type = config["model"].get("scaler", "standard").lower()
    if scaler_type == "robust":
        scaler = RobustScaler()
    else:
        scaler = StandardScaler()
        
    X_scaled = scaler.fit_transform(X)
    
    # 5. Model Training (HDBSCAN)
    # Priority: params_override > config
    min_cluster_size = params_override.get("min_cluster_size") if params_override else config["model"]["min_cluster_size"]
    min_samples = params_override.get("min_samples") if params_override else config["model"]["min_samples"]
    metric = params_override.get("metric") if params_override else config["model"]["metric"]
    epsilon = params_override.get("cluster_selection_epsilon") if params_override else config["model"]["cluster_selection_epsilon"]
    method = params_override.get("cluster_selection_method") if params_override else "eom"
    
    logger.info(f"Training HDBSCAN (mcs={min_cluster_size}, ms={min_samples}, metric={metric}, eps={epsilon}, method={method})...")
    
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric=metric,
        cluster_selection_epsilon=epsilon,
        cluster_selection_method=method,
        gen_min_span_tree=True, # Required for relative_validity
        core_dist_n_jobs=-1
    )
    
    clusterer.fit(X_scaled)
    
    # 6. Extract Results
    labels = clusterer.labels_
    membership = clusterer.probabilities_ # Membership Strength (0 to 1)
    
    # Correct Outlier Scores
    if hasattr(clusterer, "outlier_scores_"):
        outlier_score = clusterer.outlier_scores_
    else:
        outlier_score = hdbscan.outlier_scores(clusterer)

    # 7. Metrics Calculation
    n_noise = int((labels == -1).sum())
    noise_pct = (n_noise / len(labels)) * 100
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    
    # Largest Cluster Pct
    largest_cluster_pct = 0.0
    valid_counts = pd.Series(labels[labels != -1]).value_counts()
    if len(valid_counts) > 0:
        largest_cluster_pct = (valid_counts.iloc[0] / len(labels)) * 100

    # HDBSCAN Specific Metrics
    relative_validity = float(getattr(clusterer, "relative_validity_", -1))
    persistence = getattr(clusterer, "cluster_persistence_", None)
    
    persistence_mean = float(np.mean(persistence)) if persistence is not None and len(persistence) else None
    persistence_min = float(np.min(persistence)) if persistence is not None and len(persistence) else None
    persistence_max = float(np.max(persistence)) if persistence is not None and len(persistence) else None

    # Internal Validity (Silhouette, DBI, CH) - ONLY on valid clusters
    sil_score = -1.0
    dbi_score = -1.0
    ch_score = -1.0
    
    if n_clusters > 1:
        valid_mask = labels != -1
        X_valid = X_scaled[valid_mask]
        labels_valid = labels[valid_mask]
        
        if len(set(labels_valid)) > 1:
            sil_score = silhouette_score(X_valid, labels_valid)
            dbi_score = davies_bouldin_score(X_valid, labels_valid)
            ch_score = calinski_harabasz_score(X_valid, labels_valid)

    logger.info(f"Clusters: {n_clusters} | Noise: {noise_pct:.1f}% | DBCV: {relative_validity:.3f}")

    # 8. Prepare Export Data
    df_export = df.loc[X.index].copy()
    df_export["Cluster"] = labels
    df_export["Membership_Strength"] = membership
    df_export["Outlier_Score"] = outlier_score
    
    # Save CSV
    df_export.to_csv(csv_out, index=False)
    logger.info(f"Saved results to {csv_out}")

    # 9. Artifact Generation
    
    # A) Metrics JSON (Core)
    metrics_payload = {
        "run_id": run_id,
        "n_clusters": int(n_clusters),
        "noise_pct": float(noise_pct),
        "largest_cluster_pct": float(largest_cluster_pct),
        "dbcv_relative_validity": relative_validity,
        # Legacy/Compat keys
        "relative_validity": relative_validity,
        "persistence_mean": persistence_mean,
        "persistence_min": persistence_min,
        "persistence_max": persistence_max,
        "silhouette_valid": float(sil_score),
        "davies_bouldin_valid": float(dbi_score),
        "calinski_harabasz_valid": float(ch_score),
    }
    with open(metrics_out, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    # B) Advanced Metrics JSON (Audit)
    runtime_seconds = float(time.time() - t0)
    adv_payload = {
        **metrics_payload,
        "runtime_seconds": runtime_seconds,
        "features": features,
        "log_transform_feature": log_col,
        "scaler": scaler_type,
        "params": {
            "min_cluster_size": min_cluster_size,
            "min_samples": min_samples,
            "metric": metric,
            "cluster_selection_epsilon": epsilon,
        },
        "versions": {
            "python": platform.python_version(),
            "sklearn": sklearn.__version__,
            "hdbscan": getattr(hdbscan, "__version__", "unknown"),
            "pandas": pd.__version__,
            "numpy": np.__version__
        }
    }
    with open(adv_out, "w", encoding="utf-8") as f:
        json.dump(adv_payload, f, indent=2)

    # C) Cluster Profiles (fka Centroids)
    profiles = []
    
    # 1. Collect Basic Stats
    unique_valid_clusters = sorted([c for c in set(labels) if c != -1])
    
    # Calculate global medians for relative comparison (Insight Generation)
    mask_valid = df_export["Cluster"] != -1
    global_monto_med = df_export.loc[mask_valid, "Monto_Aprobado"].median()
    global_count_med = df_export.loc[mask_valid, "CANTIDAD_APROBACIONES"].median()

    temp_profiles = []
    for c_id in unique_valid_clusters:
        cid_int = int(c_id)
        sub = df_export[df_export["Cluster"] == cid_int]
        temp_profiles.append({
            "cluster": cid_int,
            "count": int(len(sub)),
            "monto": float(sub["Monto_Aprobado"].mean()), 
            "aprobaciones": float(sub["CANTIDAD_APROBACIONES"].mean()), 
            "monto_median": float(sub["Monto_Aprobado"].median()),
            "aprob_median": float(sub["CANTIDAD_APROBACIONES"].median()),
            "monto_p25": float(sub["Monto_Aprobado"].quantile(0.25)),
            "monto_p75": float(sub["Monto_Aprobado"].quantile(0.75)),
            "aprob_p25": float(sub["CANTIDAD_APROBACIONES"].quantile(0.25)),
            "aprob_p75": float(sub["CANTIDAD_APROBACIONES"].quantile(0.75)),
        })

    # 2. Add Tiers & Descriptions (Dynamic Persona Generation)
    # Sort by Monto Descending for Tier assignment
    temp_profiles.sort(key=lambda x: x["monto"], reverse=True)
    n_profs = len(temp_profiles)
    tier_chunk = np.ceil(n_profs / 3)
    
    for i, p in enumerate(temp_profiles):
        # Tier Assignment
        if i < tier_chunk:
            p["tier"] = "Tier A"
        elif i < tier_chunk * 2:
            p["tier"] = "Tier B"
        else:
            p["tier"] = "Tier C"
            
        # Descriptive Insight Generation
        desc_parts = []
        # Value Dimension
        if p["monto_median"] > global_monto_med * 1.2:
            desc_parts.append("High Value")
        elif p["monto_median"] < global_monto_med * 0.8:
            desc_parts.append("Low Value")
        else:
            desc_parts.append("Avg Value")
            
        # Frequency Dimension
        if p["aprob_median"] > global_count_med * 1.2:
            desc_parts.append("High Freq")
        elif p["aprob_median"] < global_count_med * 0.8:
            desc_parts.append("Low Freq")
        else:
            desc_parts.append("Avg Freq")
            
        p["description"] = " & ".join(desc_parts)
        p["label"] = f"Cluster {p['cluster']} ({p['tier']})"

    # Write Profiles (Back to sorted by ID for consistency if needed, strictly front-end can handle sort)
    # Let's sort by ID to match generic expectation
    profiles = sorted(temp_profiles, key=lambda x: x["cluster"])

    with open(profiles_out, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)

    # D) Top 10 Outliers
    # Ensure numerical
    top = df_export.sort_values("Outlier_Score", ascending=False).head(10)
    # Ensure all data types are JSON serializable
    top_records = top[["Pais", "Anio",  "Monto_Aprobado", "CANTIDAD_APROBACIONES", "Cluster", "Outlier_Score"]].to_dict("records") # Anio or Anio_Origen? Check ETL. Assuming Anio from file view
    with open(outliers_out, "w", encoding="utf-8") as f:
        json.dump(top_records, f, ensure_ascii=False, indent=2)

    # E) Outlier Histogram
    vals = df_export["Outlier_Score"].values
    hist, edges = np.histogram(vals, bins=20, range=(0, 1))
    hist_payload = [{"bin_left": float(edges[i]), "bin_right": float(edges[i+1]), "count": int(hist[i])} for i in range(len(hist))]
    with open(hist_out, "w", encoding="utf-8") as f:
        json.dump(hist_payload, f, indent=2)

    # F) Persist Model & Scaler
    dump(clusterer, model_out)
    dump(scaler, scaler_out)
    
    with open(spec_out, "w", encoding="utf-8") as f:
        json.dump({"features": features, "log_transform_feature": log_col}, f, indent=2)

    logger.info("Training Pipeline Completed Successfully.")
    return {"run_id": run_id, "output_dir": str(run_dir)}
