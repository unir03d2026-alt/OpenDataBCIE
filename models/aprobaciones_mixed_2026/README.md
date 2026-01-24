# BCIE Segmentation Model (Mixed Clustering 2026) -> Production

## 📋 Overview

This project implements a **Hierarchical Clustering** pipeline on Mixed Data (Numeric + Categorical) to segment the BCIE portfolio. It uses **Gower Distance** for similarity and optimizing a custom **Composite Score** (Quality, Stability, Balance).

## 🏗️ Project Structure (MLOps Standard)

```
.
├── config/                 # Configuration files
│   └── local.yaml          # API keys, hyperparameters, and paths
├── data/                   # Data artifacts (Raw -> Processed -> Predictions)
├── src/
│   ├── pipelines/          # Core ETL and Training Pipelines (Modular)
│   │   ├── etl_pipeline.py
│   │   └── training_pipeline.py
│   ├── dashboard/          # Visualization Logic
│   │   ├── dashboard_template.html
│   │   └── generate_dashboard.py
│   └── utils/              # Helper functions (Gower, Embedding)
├── src_backup_*/           # versioned backups
├── run.py                  # Main Entry Point (Orchestrator)
└── requirements.txt        # Python Dependencies
```

## 🚀 Usage

### Requirements

- Python 3.9+
- See `requirements.txt`

### Execution

Run the full pipeline (ETL -> Train -> Dashboard) via the orchestrator:

```bash
python run.py
```

### Pipelines Detail

1.  **ETL (`src/pipelines/etl_pipeline.py`)**
    - **Extract**: Pulls data from BCIE CKAN API (or local cache).
    - **Transform**: Cleans text, imputes values, calculates features (`Tipo_Pais`, `Quadrants`).
    - **Load**: Saves `processed.csv`.

2.  **Training (`src/pipelines/training_pipeline.py`)**
    - **Logic**: Hierarchical Clustering (Average Linkage).
    - **Optimization**: Search Grid (K=2..15). Maximizes Composite Score.
    - **Validation**:
      - **Bootstrap**: B=50 iterations (ARI).
      - **Silhouette**: Gower-based.
      - **Balance**: CV of sizes.

3.  **Dashboard**
    - Generates a standalone HTML file (`src/dashboard/dashboard_clustering.html`).
    - Features: Cross-filtering, 2D MDS Map, and Statistical profiles.

## 🛡️ Robustness & Validation

- **Stability**: The model achieves **ARI ~1.0** under bootstrap, indicating extensive structural robustness.
- **Metric Transparency**: All metrics (Silhouette, Stress, CV) are reported in "Raw" format for auditability.
