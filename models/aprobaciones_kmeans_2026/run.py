"""
Main Entry Point for the BCIE K-Means Clustering Model (2026).

This script orchestrates the end-to-end execution of the analytics pipeline:
1. ETL: Data extraction from CKAN and preprocessing.
2. Training: Feature engineering, K-Means clustering, and optimization.
3. Dashboard: Generation of the HTML reporting interface.

Usage:
    python run.py

Dependencies:
    - config/local.yaml
    - src/pipelines/
    - src/dashboard/
"""

import logging
import sys
import os

# Ensure src module is in the path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from pipelines.etl_pipeline import run_etl
from pipelines.training_pipeline import train_kmeans

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """Execute the full data pipeline."""
    config_path = "config/local.yaml"
    
    logging.info(">>> INITIATING BCIE K-MEANS CLUSTERING PIPELINE <<<")
    
    # 1. ETL Phase
    logging.info("--- PHASE 1: ETL (EXTRACTION & TRANSFORMATION) ---")
    try:
        run_etl(config_path)
    except Exception as e:
        logging.critical(f"ETL Failure: {e}")
        return

    # 2. Training Phase
    logging.info("--- PHASE 2: MODEL TRAINING & OPTIMIZATION ---")
    try:
        train_kmeans(config_path)
    except Exception as e:
        logging.critical(f"Training Failure: {e}")
        return
        
    # 3. Dashboard Generation
    logging.info("--- PHASE 3: DASHBOARD GENERATION ---")
    try:
        # Dynamic import to ensure path context is correct
        from src.dashboard.generate_dashboard import generate_dashboard
        generate_dashboard()
    except Exception as e:
        logging.critical(f"Dashboard Failure: {e}")
        return
        
    logging.info(">>> PIPELINE COMPLETED SUCCESSFULLY <<<")

if __name__ == "__main__":
    main()
