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
sys.path.append(str(Path(__file__).parent))

from src.pipelines.etl_pipeline import run_etl
from src.pipelines.training_pipeline import train_hierarchical

def main():
    logging.info(">>> INICIANDO PROCESO DE CLUSTERING JERARQUICO <<<")
    config_path = "config/local.yaml"
    
    # 1. ETL
    logging.info("--- PASO 1: ETL ---")
    try:
        run_etl(config_path)
    except Exception as e:
        logging.error(f"Fallo en ETL: {e}")
        return

    # 2. Entrenamiento
    logging.info("--- PASO 2: ENTRENAMIENTO (AGGLOMERATIVE) ---")
    try:
        train_hierarchical(config_path)
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
