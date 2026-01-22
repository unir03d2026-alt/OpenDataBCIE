"""
Pipeline de Visualización y Reportes

Este script es el responsable de unificar los datos históricos y las proyecciones generadas
para crear dashboards interactivos que faciliten la toma de decisiones.
Se generan dos tipos de reportes:
1. Predictivo: Enfocado en el futuro y la incertidumbre.
2. Ejecutivo: Enfocado en el desempeño histórico reciente.
"""

import pandas as pd
import yaml
import os
import logging
from pathlib import Path
from src.dashboard.logic import prepare_unified_data, process_executive_data
from src.dashboard.layout import get_dashboard_html, get_executive_html
from datetime import datetime

# Configuración del registro de eventos (logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_plots(config_path):
    try:
        logger.info("Iniciando la generación de reportes visuales...")
        config = load_config(config_path)
        
        # Definición de rutas de acceso a datos
        raw_path = config['data']['processed_path'] # Utilizamos los datos procesados como base histórica
        pred_path_dir = config.get('paths', {}).get('predictions_path', "data/04-predictions")
        pred_path = os.path.join(pred_path_dir, "predicciones_bcie.csv")
        
        if not os.path.exists(raw_path):
            raise FileNotFoundError(f"No se encontraron datos históricos en: {raw_path}")
            
        if not os.path.exists(pred_path):
            logger.warning(f"No se encontró el archivo de predicciones en {pred_path}. Se generará el dashboard únicamente con datos históricos.")
            # Creación de estructura vacía para evitar fallos en la lógica de unión
            df_pred = pd.DataFrame(columns=['ds', 'unique_id', 'yhat', 'yhat_lower', 'yhat_upper'])
        else:
            df_pred = pd.read_csv(pred_path)

        df_hist = pd.read_csv(raw_path)
        
        # 1. Generación del Dashboard Predictivo
        logger.info("Construyendo Dashboard Predictivo...")
        
        # Unificación de datos (históricos + predicciones) para el gráfico continuo
        df_final = prepare_unified_data(df_hist, df_pred)
        
        # Generación del código HTML del reporte
        html_predictivo = get_dashboard_html(df_final)
        
        output_pred = Path("data/05-reporting/dashboard_proyecciones_2026.html")
        output_pred.parent.mkdir(parents=True, exist_ok=True)
        with open(output_pred, "w", encoding="utf-8") as f:
            f.write(html_predictivo)
        logger.info(f"Reporte Predictivo generado exitosamente: {output_pred}")

        # 2. Generación del Dashboard Ejecutivo
        logger.info("Construyendo Dashboard Ejecutivo...")
        
        # Procesamiento de métricas clave para la vista ejecutiva
        data_exec = process_executive_data(df_hist)
        
        now = datetime.now()
        html_exec = get_executive_html(data_exec, now.strftime("%d/%m/%Y"), now.year)
        
        output_exec = Path("data/05-reporting/dashboard_ejecutivo_bcie.html")
        with open(output_exec, "w", encoding="utf-8") as f:
            f.write(html_exec)
        logger.info(f"Reporte Ejecutivo generado exitosamente: {output_exec}")
        
    except Exception as e:
        logger.error(f"Error durante la generación de gráficos: {str(e)}")
        raise e

if __name__ == "__main__":
    generate_plots("config/local.yaml")
