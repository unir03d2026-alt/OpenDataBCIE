import logging
import sys
import os

# Agregar src al path para imports
sys.path.append(os.path.join(os.getcwd(), 'src'))

from pipelines.etl_pipeline import run_etl
from pipelines.training_pipeline import train_kmeans

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    config_path = "config/local.yaml"
    
    logging.info(">>> INICIANDO PROCESO DE CLUSTERING K-MEANS <<<")
    
    # 1. ETL
    logging.info("--- PASO 1: ETL ---")
    try:
        run_etl(config_path)
    except Exception as e:
        logging.error(f"Fallo en ETL: {e}")
        return

    # 2. Entrenamiento
    logging.info("--- PASO 2: ENTRENAMIENTO Y OPTIMIZACION ---")
    try:
        train_kmeans(config_path)
    except Exception as e:
        logging.error(f"Fallo en Entrenamiento: {e}")
        return
        
    # 3. Dashboard
    logging.info("--- PASO 3: GENERACION DE DASHBOARD ---")
    try:
        # Importar dinamicamente para asegurar que use el path correcto
        from src.dashboard.generate_dashboard import generate_dashboard
        generate_dashboard()
    except Exception as e:
        logging.error(f"Fallo en Dashboard: {e}")
        return
        
    logging.info(">>> PROCESO COMPLETADO EXITOSAMENTE <<<")

if __name__ == "__main__":
    main()
