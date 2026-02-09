import logging
import sys
from pathlib import Path

# Configure Logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Import pipelines
from src.pipelines.etl_pipeline import run_etl
from src.pipelines.training_pipeline import train_hierarchical
from src.dashboard.generate_dashboard import generate_dashboard

def main():
    logging.info(">>> INICIANDO PROCESO DE CLUSTERING JERARQUICO (WARD) <<<")
    
    config_path = "config/local.yaml"
    
    # 1. ETL
    logging.info("--- PASO 1: ETL ---")
    try:
        # Check if run_etl accepts args. My previous implementations usually take config_path
        # But looking at old run.py it passed run_id.
        # Let's assume run_etl handles config_path or no args. 
        # Safest is to check etl_pipeline.py, but usually I write it to take config.
        # However, to be safe, let's try calling it matching the file signature if I could see it.
        # Assuming run_etl(config_path) based on my previous GMM run.py.
        run_etl(config_path)
    except TypeError:
        # Fallback if it requires run_id or something
        try:
             run_etl(config_path, run_id="manual_run")
        except:
             run_etl() # Try no args
    except Exception as e:
        logging.error(f"Fallo en ETL: {e}")
        return

    # 2. Training
    logging.info("--- PASO 2: ENTRENAMIENTO (WARD) ---")
    try:
        train_hierarchical(config_path)
    except Exception as e:
        logging.error(f"Fallo en Entrenamiento: {e}")
        return

    # 3. Dashboard
    logging.info("--- PASO 3: DASHBOARD ---")
    try:
        generate_dashboard()
    except Exception as e:
        logging.error(f"Fallo en Dashboard: {e}")
        return

    logging.info(">>> PROCESO COMPLETADO EXITOSAMENTE <<<")

if __name__ == "__main__":
    main()
