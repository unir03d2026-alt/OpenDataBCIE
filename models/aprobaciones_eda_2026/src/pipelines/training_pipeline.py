"""
Training Pipeline Module.

This module executes the Hierarchical Clustering training process using Gower Distance.
It implements a custom 'Composite Score' optimization strategy to balance:
1. Quality (Silhouette + Cohesion/Separation).
2. Stability (Bootstrap ARI).
3. Balance (Cluster size distribution).

MLOps Standards:
- Google-style docstrings.
- Reproducible random seeds.
- Metric logging.
"""

import pandas as pd
import numpy as np
import yaml
import logging
import os
import json
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
from sklearn.metrics import silhouette_score, adjusted_rand_score, silhouette_samples
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

# Local imports
sys.path.append(os.path.join(os.getcwd(), 'src'))
from utils.gower_dist import compute_gower_distance
from utils.embedding import generate_embedding

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Helper Functions ---

def hierarchical_labels_from_distance(D: np.ndarray, k: int, method: str = "average") -> np.ndarray:
    """
    Generates cluster labels from a precomputed distance matrix using Hierarchical Clustering.

    Args:
        D (np.ndarray): Square distance matrix.
        k (int): Number of clusters to form.
        method (str): Linkage method (e.g., 'average', 'ward', 'complete').

    Returns:
        np.ndarray: Array of cluster labels (0 to k-1).
    """
    # scipy linkage requires condensed distance matrix for some inputs, or square form
    condensed = squareform(D, checks=False)
    Z = linkage(condensed, method=method)
    # fcluster returns labels 1..k -> convert to 0..k-1
    labels = fcluster(Z, t=k, criterion="maxclust") - 1
    return labels

def mean_intra_inter(D: np.ndarray, labels: np.ndarray) -> Tuple[float, float]:
    """
    Calculates Mean Intra-cluster distance (W) and Mean Inter-cluster distance (B).

    Args:
        D (np.ndarray): Square distance matrix.
        labels (np.ndarray): Cluster labels.

    Returns:
        Tuple[float, float]: (W, B) - Mean Intra and Mean Inter distances.
    """
    n = D.shape[0]
    # Generate indices for the upper triangle (excluding diagonal)
    iu = np.triu_indices(n, k=1)
    dvals = D[iu]
    
    # Check pairwise label equality
    l_i = labels[iu[0]]
    l_j = labels[iu[1]]
    same = (l_i == l_j)
    
    # Calculate means, handling empty cases safely
    W = dvals[same].mean() if np.any(same) else 1.0
    B = dvals[~same].mean() if np.any(~same) else 0.0
    return W, B

def balance_score(labels: np.ndarray) -> float:
    """
    Calculates a Balance Score based on the Coefficient of Variation (CV) of cluster sizes.
    Formula: 1 / (1 + CV)

    Args:
        labels (np.ndarray): Cluster labels.

    Returns:
        float: Balance score in [0, 1]. Higher is more balanced.
    """
    sizes = np.bincount(labels)
    if sizes.size <= 1:
        return 0.0
    cv = sizes.std() / (sizes.mean() + 1e-12)
    return 1.0 / (1.0 + cv)

def stability_bootstrap_ari(
    D: np.ndarray, 
    labels_full: np.ndarray, 
    k: int, 
    method: str = "average", 
    B: int = 50, 
    frac: float = 0.6, 
    seed: int = 42
) -> Dict[str, float]:
    """
    Estimates Clustering Stability using Bootstrap Adjusted Rand Index (ARI).

    Args:
        D (np.ndarray): Distance matrix.
        labels_full (np.ndarray): Original cluster labels.
        k (int): Number of clusters.
        method (str): Linkage method.
        B (int): Number of bootstrap iterations. Default 50 (High Rigor).
        frac (float): Fraction of samples to subsample. Default 0.6.
        seed (int): Random seed for reproducibility.

    Returns:
        Dict: Statistics of ARI scores (mean, std, min, max).
    """
    rng = np.random.default_rng(seed)
    n = D.shape[0]
    aris = []
    
    for _ in range(B):
        # Subsample indices
        idx = rng.choice(n, size=int(frac*n), replace=False)
        
        # Extract sub-matrix
        D_sub = D[np.ix_(idx, idx)]
        
        # Re-cluster the subset
        labels_sub = hierarchical_labels_from_distance(D_sub, k, method=method)
        
        # Compare with the original labels restricted to the subset
        aris.append(adjusted_rand_score(labels_full[idx], labels_sub))
        
    aris = np.array(aris, dtype=float)
    return {
        "mean": float(np.mean(aris)),
        "std":  float(np.std(aris)),
        "min":  float(np.min(aris)),
        "max":  float(np.max(aris))
    }

def composite_score_for_k(
    D: np.ndarray, 
    k: int, 
    k_min: int, 
    k_max: int,
    method: str = "average",
    lam: float = 1.0,
    B: int = 50, 
    frac: float = 0.6,
    # Weights Configuration
    wS: float = 0.50, wC: float = 0.25, wSep: float = 0.25,   # Q components
    wQ: float = 0.60, wStab: float = 0.25, wBal: float = 0.15 # Final components
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculates a comprehensive Composite Score for a given K.

    Score = Penalty * (wQ*Quality + wStab*Stability + wBal*Balance)

    Args:
        D (np.ndarray): Distance Matrix.
        k (int): Number of clusters to evaluate.
        k_min (int): Minimum K in search range (for penalty scaling).
        k_max (int): Maximum K in search range.
        method (str): Linkage method.
        lam (float): Penalty lambda parameter.
        B (int): Bootstrap iterations.
        frac (float): Bootstrap subsample fraction.
        wS, wC, wSep: Weights for Quality sub-score.
        wQ, wStab, wBal: Weights for Final Score.

    Returns:
        Tuple[float, Dict]: Final Score (0-1) and dictionary of component details.
    """
    labels = hierarchical_labels_from_distance(D, k, method=method)

    # 1. Silhouette Score (Gower)
    s_raw = 0.0
    s_star = 0.0
    try:
        if len(np.unique(labels)) < 2:
            s_raw, s_star = 0.0, 0.0
        else:
            s_raw = float(silhouette_score(D, labels, metric="precomputed")) # [-1, 1]
            s_star = float(np.clip((s_raw + 1) / 2, 0, 1))                   # [0, 1] Normalized
    except Exception:
        s_raw, s_star = 0.0, 0.0

    # 2. Cohesion & Separation
    W, Bsep = mean_intra_inter(D, labels)
    C = np.clip(1 - W, 0, 1)     # Cohesion (1-Intra)
    Sep = np.clip(Bsep, 0, 1)    # Separation (Inter)

    Q = wS*s_star + wC*C + wSep*Sep

    # 3. Balance & Stability
    Bal = balance_score(labels)
    Stab_stats = stability_bootstrap_ari(D, labels, k, method=method, B=B, frac=frac)
    Stab = Stab_stats["mean"]

    # 4. Complexity Penalty
    P = np.exp(-lam * (k - k_min) / max(1, (k_max - k_min)))

    score = P * (wQ*Q + wStab*Stab + wBal*Bal)
    
    return float(np.clip(score, 0, 1)), {
        "S_raw": float(s_raw),
        "S_star": float(s_star), 
        "C": float(C), 
        "Sep": float(Sep),
        "Q": float(Q), 
        "Stab": float(Stab), 
        "Stab_details": Stab_stats,
        "Bal": float(Bal), 
        "P": float(P)
    }

def train_mixed_clustering(config_path: str = "config/local.yaml") -> None:
    """
    Executes the full training pipeline: Load -> Transform -> Optimize K -> Train -> Save.
    """
    
    # 1. Configuration & Data Load
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    input_path = Path(config['data']['processed_path'])
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return

    df = pd.read_csv(input_path)
    logger.info(f"Loaded {len(df)} records for training.")

    # 2. Feature Preparation
    req_cols = ['Monto_Aprobado', 'CANTIDAD_APROBACIONES', 'Sector_Economico']
    if not all(col in df.columns for col in req_cols):
        logger.error(f"Missing required columns. Found: {df.columns}")
        return

    # Log Transforms for Numerical Stability
    df_features = pd.DataFrame()
    df_features['log_Monto'] = np.log10(df['Monto_Aprobado'] + 1)
    df_features['log_Cant'] = np.log1p(df['CANTIDAD_APROBACIONES'])
    df['Sector_Economico'] = df['Sector_Economico'].fillna('Unknown')
    df_features['Sector'] = df['Sector_Economico']

    # 3. Gower Distance Matrix
    logger.info("Computing Gower Distance Matrix...")
    dist_matrix = compute_gower_distance(df_features, cat_features=['Sector'])

    # 4. K Optimization Loop
    logger.info("Starting Grid Search for Optimal K...")
    
    best_score = -1
    best_k = 2
    results = {}
    
    k_min, k_max = 2, 15
    k_range = range(k_min, k_max + 1)
    method = "average"
    
    for k in k_range:
        score, parts = composite_score_for_k(
            dist_matrix, k, k_min, k_max,
            method=method,
            lam=1.0,
            B=50, frac=0.6 # High Rigor Bootstrapping
        )
        
        logger.info(f"K={k}: Score={score:.3f} (Sil={parts['S_raw']:.3f}, Stab={parts['Stab']:.2f})")
        
        results[k] = {
            'composite_score': score, 
            'silhouette': parts['S_raw'],
            'silhouette_norm': parts['S_star'],
            'details': parts
        }
        
        if score > best_score:
            best_score = score
            best_k = k

    logger.info(f"mathematical Best K: {best_k} (Score: {best_score:.3f})")

    # 5. Business Rules logic
    # Rule 1: Complexity Penalty (Smallest K within 95% of best)
    threshold = 0.95 * best_score
    candidate_ks = [k for k in k_range if results[k]['composite_score'] >= threshold]
    if candidate_ks:
        best_k = min(candidate_ks)
        logger.info(f"Fair-K Rule selected: K={best_k}")
    
    # Rule 2: Strategic Override (Prefer K=3 if competitive)
    if 3 in results:
        score_k3 = results[3]['composite_score']
        if best_k != 3 and score_k3 >= (best_score * 0.90):
            logger.info(f"Strategic Override: Switching K={best_k} -> K=3 (Score {score_k3:.3f} is robust)")
            best_k = 3
    
    # 6. Final Model Application
    final_labels = hierarchical_labels_from_distance(dist_matrix, best_k, method=method)
    
    # 7. Embedding (MDS)
    df_emb, raw_stress = generate_embedding(dist_matrix)
    
    # Normalized Stress-1 Calculation
    d_sq_sum = np.sum(squareform(dist_matrix, checks=False)**2)
    stress_1 = np.sqrt(raw_stress / d_sq_sum) if d_sq_sum > 0 else 0.0
    
    # 8. Artifact Generation
    output_dir = Path("data/04-predictions")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df_out = df.copy()
    df_out['Cluster'] = final_labels
    
    # Per-sample Confidence score mapping
    try:
        sample_sils = silhouette_samples(dist_matrix, final_labels, metric="precomputed")
        df_out['Confidence'] = (sample_sils + 1) / 2 # Normalize [-1,1] -> [0,1]
    except Exception as e:
        logger.warning(f"Could not compute silhouette samples: {e}")
        df_out['Confidence'] = 1.0

    df_out['x'] = df_emb['x']
    df_out['y'] = df_emb['y']
    df_out.to_csv(output_dir / "aprobaciones_clusters.csv", index=False)
    
    # Metrics JSON
    final_metrics = results[best_k]
    final_metrics.update({
        'k_optimo': best_k, 
        'linkage': method, 
        'n_samples': len(df),
        'mds_stress': float(stress_1),
        'mds_stress_raw': float(raw_stress)
    })
    
    with open(output_dir / "metrics.json", 'w') as f:
        json.dump([final_metrics], f, indent=4)
        
    # Centroids/Profiles JSON
    profiles = []
    for c in range(best_k):
        sub = df_out[df_out['Cluster'] == c]
        if len(sub) > 0:
            top_sector = sub['Sector_Economico'].mode()[0] if not sub['Sector_Economico'].mode().empty else 'N/A'
            profile = {
                'cluster': int(c),
                'count': int(len(sub)),
                'monto': float(sub['Monto_Aprobado'].median()),
                'monto_total': float(sub['Monto_Aprobado'].sum()),
                'aprobaciones': float(sub['CANTIDAD_APROBACIONES'].median()),
                'top_sector': str(top_sector)
            }
            profiles.append(profile)
            
    with open(output_dir / "centroids.json", 'w') as f:
        json.dump(profiles, f, indent=4)
        
    # Advanced Metrics JSON
    adv_metrics = {
        'k_selection': [
            {
                'k': k, 
                'silhouette': v['silhouette'],
                'silhouette_norm': v.get('silhouette_norm'),
                'score': v['composite_score'],
                'details': v['details']
            } for k, v in results.items()
        ]
    }
    with open(output_dir / "advanced_metrics.json", 'w') as f:
        json.dump(adv_metrics, f, indent=4)

    logger.info("Training pipeline completed successfully.")

if __name__ == "__main__":
    train_mixed_clustering()
