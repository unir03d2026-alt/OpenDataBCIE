# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Machine Learning laboratory for reproducible experiments using open data from BCIE (Banco Centroamericano de Integración Económica). The repository contains multiple independent ML models focused on approvals forecasting and clustering analysis.

**Data Source:** BCIE Open Data Portal (CKAN API) - https://datosabiertos.bcie.org/

## Commands

### Running a Model Pipeline

Each model in `models/` is self-contained. Navigate to the model directory and run:

```bash
cd models/<model_name>
python run.py                           # Full pipeline: ETL → Training → Dashboard
python run.py --skip-etl                # Skip data extraction if already cached
python run.py --optimize                # Run with hyperparameter optimization
python run.py --config config/local.yaml  # Specify config file
```

### Environment Verification

```bash
python verify_env.py   # Check all required ML libraries are installed
```

### Creating a New Model Project

Edit `setup_project.py` to change `PROJECT_NAME`, then run:

```bash
python setup_project.py
```

### Installing Dependencies

Each model has its own requirements.txt:

```bash
cd models/<model_name>
pip install -r requirements.txt
```

## Architecture

### Model Directory Structure

Every model follows a standardized 3-phase pipeline pattern:

```
models/<model_name>/
├── config/local.yaml       # API endpoints, hyperparameters, paths
├── data/
│   ├── 01-raw/            # Raw data from CKAN API
│   ├── 02-preprocessed/   # Cleaned/transformed data
│   ├── 03-features/       # Feature engineering output
│   ├── 04-predictions/    # Model outputs (runs/ for versioned results)
│   └── 05-plots/          # Generated HTML dashboards
├── src/
│   ├── pipelines/         # ETL, training, optimization orchestration
│   ├── dashboard/         # Plotly HTML generation
│   └── utils/             # Helpers (Gower distance, embeddings, etc.)
├── run.py                 # Main orchestrator
└── requirements.txt
```

### Pipeline Phases

1. **ETL** (`src/pipelines/etl_pipeline.py`): Fetch from CKAN API → Clean → Save to `data/02-preprocessed/`
2. **Training** (`src/pipelines/training_pipeline.py`): Load data → Fit model → Save predictions to `data/04-predictions/`
3. **Dashboard** (`src/dashboard/generate_dashboard.py`): Generate interactive HTML visualizations

### Configuration

Models use YAML configuration (`config/local.yaml`) for:
- API settings (base_url, resource_id, limit)
- Data paths and column mappings
- Model hyperparameters
- Output directories

### Model Types Implemented

- **Time Series:** Prophet, NeuralProphet, StatsForecast (AutoARIMA/Theta), TimesFM
- **Clustering:** K-Means, HDBSCAN, Hierarchical, DBSCAN, GMM, K-Medoids
- **Mixed Data Clustering:** Gower Distance for categorical + numeric features

### Key Libraries

pandas, numpy, scikit-learn, prophet, neuralprophet, statsforecast, hdbscan, xgboost, plotly, torch, transformers

## Development Notes

- Run IDs are auto-generated with format `run_YYYYMMDD_HHMMSS_<uuid6>` for versioning outputs
- Validation uses Bootstrap ARI, Silhouette scores, and Composite Score optimization
- Dashboards are standalone HTML files with interactive Plotly charts
- Models track status in `models/checklist_modelos.csv`
