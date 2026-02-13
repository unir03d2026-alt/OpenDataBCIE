"""
DBSCAN Clustering Pipeline - Main Orchestrator.

This script orchestrates the full DBSCAN clustering workflow:
1. ETL: Downloads and preprocesses data from the BCIE CKAN API.
2. Training: Runs the DBSCAN clustering model.
3. Dashboard: Generates the interactive HTML dashboard.

Usage:
    python entrypoint/main.py
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DBSCAN_Orchestrator")

def main():
    """Main orchestration function."""
    
    # Resolve config path
    if Path("config/local.yaml").exists():
        config_path = "config/local.yaml"
    elif Path("local.yaml").exists():
        config_path = "local.yaml"
    else:
        logger.error("No configuration file found (config/local.yaml or local.yaml)")
        sys.exit(1)

    # Generate unique Run ID
    run_id = datetime.now().strftime("run_%Y%m%d_%H%M%S")
    logger.info(f"=" * 60)
    logger.info(f"DBSCAN Pipeline - Run ID: {run_id}")
    logger.info(f"=" * 60)

    # --- PHASE 1: ETL ---
    logger.info("PHASE 1: ETL Pipeline")
    try:
        from src.pipelines.etl_pipeline import run_etl
        run_etl(config_path, run_id=run_id)
        logger.info("✅ ETL Pipeline completed successfully.")
    except Exception as e:
        logger.error(f"❌ ETL Pipeline failed: {e}")
        sys.exit(1)

    # --- PHASE 2: TRAINING ---
    logger.info("PHASE 2: Training Pipeline (DBSCAN)")
    try:
        from src.pipelines.training_pipeline import train_dbscan
        result = train_dbscan(config_path, run_id=run_id)
        logger.info(f"✅ Training Pipeline completed. Output: {result['output_dir']}")
    except Exception as e:
        logger.error(f"❌ Training Pipeline failed: {e}")
        sys.exit(1)

    # --- PHASE 3: DASHBOARD ---
    logger.info("PHASE 3: Dashboard Generation")
    try:
        from src.dashboard.generate_dashboard import generate_dashboard
        generate_dashboard(config_path, run_id=run_id)
        logger.info("✅ Dashboard generated successfully.")
    except Exception as e:
        logger.error(f"❌ Dashboard generation failed: {e}")
        # Non-fatal: training artifacts are already saved
        logger.warning("Training artifacts are preserved despite dashboard failure.")

    logger.info(f"=" * 60)
    logger.info(f"Pipeline Complete. Run ID: {run_id}")
    logger.info(f"=" * 60)

if __name__ == "__main__":
    main()
