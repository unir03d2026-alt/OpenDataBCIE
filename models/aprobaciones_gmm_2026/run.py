import logging
import sys
from pathlib import Path

# Configurar Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Agregar src al path
sys.path.append(str(Path(__file__).parent / 'src'))

from pipelines.etl_pipeline import run_etl
from pipelines.training_pipeline import train_gmm

def main():
    logging.info(">>> INICIANDO PROCESO DE CLUSTERING GMM <<<")
    config_path = "config/local.yaml"
    
    # 1. ETL
    logging.info("--- PASO 1: ETL ---")
    try:
        run_etl(config_path)
    except Exception as e:
        logging.error(f"Fallo en ETL: {e}")
        return

    # 2. Entrenamiento
    logging.info("--- PASO 2: ENTRENAMIENTO (GMM) ---")
    try:
        train_gmm(config_path)
    except Exception as e:
        logging.error(f"Fallo en Entrenamiento: {e}")
        return
        
    # 3. Dashboard
    logging.info("--- PASO 3: GENERACION DE DASHBOARD ---")
    try:
        from src.dashboard.generate_dashboard import generate_dashboard
        generate_dashboard()
    except Exception as e:
        logging.error(f"Fallo en Dashboard: {e}")
        return
        
    logging.info(">>> PROCESO COMPLETADO EXITOSAMENTE <<<")

if __name__ == "__main__":
    main()
