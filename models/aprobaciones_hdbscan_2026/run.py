import time
import uuid
import logging
import argparse
import sys
from datetime import datetime
from pathlib import Path

# Import pipelines
from src.pipelines.etl_pipeline import run_etl
from src.pipelines.training_pipeline import train_hdbscan
from src.dashboard.generate_dashboard import generate_dashboard
from src.pipelines.optimization import run_optimization

# Configure Logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="BCIE HDBSCAN Pipeline Runner")
    parser.add_argument("--config", type=str, default="config/local.yaml", help="Path to config file")
    parser.add_argument("--optimize", action="store_true", help="Run hyperparameter optimization (Grid Search)")
    parser.add_argument("--skip-etl", action="store_true", help="Skip ETL stage if data is already processed")
    args = parser.parse_args()

    # 1. Generate Run ID
    # Format: run_YYYYMMDD_HHMMSS_shortuuid
    run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    
    logger.info(f">>> INITIATING BCIE HDBSCAN CLUSTERING PIPELINE (Run ID: {run_id}) <<<")
    
    config_path = args.config
    
    # 2. Optimization Stage (Optional)
    best_params = None
    if args.optimize:
        logger.info("--- PHASE 0: HYPERPARAMETER OPTIMIZATION ---")
        best_params = run_optimization(config_path, run_id)
        logger.info(f"Optimization finished. Proceeding with params: {best_params}")

    # 3. ETL Stage
    if not args.skip_etl:
        logger.info("--- PHASE 1: ETL EXECUTION ---")
        try:
            run_etl(config_path, run_id=run_id)
            logger.info("ETL Completed Successfully.")
        except Exception as e:
            logger.error(f"ETL Failed: {e}")
            raise
    else:
        logger.info("--- PHASE 1: SKIPPED (ETL) ---")

    # 4. Training Stage (HDBSCAN)
    logger.info("--- PHASE 2: MODEL TRAINING (HDBSCAN) ---")
    try:
        # Pass best_params if optimization ran
        train_hdbscan(config_path, run_id=run_id, params_override=best_params)
        logger.info("Training Completed Successfully.")
    except Exception as e:
        logger.error(f"Training Failed: {e}")
        raise

    # 5. Dashboard Generation
    logger.info("--- PHASE 3: DASHBOARD GENERATION ---")
    try:
        generate_dashboard(config_path, run_id=run_id)
        logger.info("Dashboard Generated Successfully.")
    except Exception as e:
        logger.error(f"Dashboard Generation Failed: {e}")
        raise

    logger.info(">>> PIPELINE COMPLETED SUCCESSFULLY <<<")

if __name__ == "__main__":
    main()
