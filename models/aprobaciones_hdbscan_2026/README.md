# BCIE Operational Clustering Model (HDBSCAN)

## 📌 Project Overview

Unsupervised machine learning model designed to segment BCIE operational approvals (1961-2025) based on financial patterns. It identifies strategic tiers (A/B/C) and detects anomalies (outliers) to support risk management and strategic resource allocation.

**Methodology:** Hierarchical Density-Based Spatial Clustering of Applications with Noise (HDBSCAN).

## 📂 Project Structure

```
.
├── backup_mvp_final_hdbscan/ # Consolidated backup of the deployed version
├── config/                   # Configuration files (logging, paths)
├── data/                     # Input datasets and intermediate parquets
├── docs/                     # Technical documentation and requirements
├── logs/                     # Execution logs
├── output/                   # Final model outputs (JSONs, Reports)
├── src/                      # Source code
│   ├── analysis/             # Analysis logic (outliers, profiles)
│   ├── dashboard/            # Web Dashboard generator (HTML/JS)
│   ├── models/               # HDBSCAN model wrapper
│   └── pipelines/            # ETL and Orchestration pipelines
├── tests/                    # Unit tests
├── requirements.txt          # Python dependencies
├── run.py                    # MAIN ENTRY POINT for full pipeline
├── regenerate_dashboard.py   # Utility to re-render dashboard without re-running model
└── README.md                 # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- Dependencies installed:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Running the Full Pipeline

To execute the complete process (ETL -> Modeling -> Profiling -> Dashboard):

```bash
python run.py
```

_Artifacts will be generated in `src/dashboard/dashboard_clustering.html`_

### 3. Regenerating Dashboard Only

If you adjusted HTML templates or want to refresh visuals without retraining the model:

```bash
python regenerate_dashboard.py
```

## 📊 Outputs & Artifacts

1.  **Dashboard:** `src/dashboard/dashboard_clustering.html` (Interactive Web Report)
2.  **Metrics:** `metrics.json` (DBCV, Stability ARI, Silhouette)
3.  **Profiles:** `cluster_profiles.json` (Strategic Tiers, Statistics)
4.  **Outliers:** `outliers.json` (Top anomalies list)

## 🛠 Model Configuration

Hyperparameters are optimized via Grid Search. Key defaults:

- **Min Cluster Size:** 7
- **Min Samples:** 2
- **Metric:** Manhattan
- **Algorithm:** HDBSCAN (Leaf method)

## 📝 Contact / Maintainers

- **Team:** 03-D (UNIR–BCIE Academic Collaboration)
- **Version:** 1.0.0 (MVP Final)
