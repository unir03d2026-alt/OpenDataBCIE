"""
Pipeline de generación de visualizaciones (PREDICCIONES PROPHET).
Ruta: src/pipelines/visualization_pipeline.py
"""
import yaml
import pandas as pd
import logging
import os
from pathlib import Path

# Importación de los módulos locales del dashboard
from src.dashboard.logic import prepare_unified_data
from src.dashboard.layout import get_dashboard_html

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def generate_plots(config_path):
    """Genera el Dashboard de Predicciones (Prophet)."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    base_dir = Path(os.getcwd())
    data_path = base_dir / config['data']['processed_path']
    pred_path = base_dir / "data/04-predictions/predicciones_bcie.csv"
    output_dir = base_dir / "src/dashboard"
    
    output_dir.mkdir(parents=True, exist_ok=True)

    if not pred_path.exists():
        logging.error(f"No se encontró el archivo de predicciones en: {pred_path}")
        return

    logging.info("Cargando datos para Predicción...")
    try:
        df_pred = pd.read_csv(pred_path, encoding='utf-8-sig')
        df_hist = pd.read_csv(data_path, encoding='utf-8-sig')
    except:
        df_pred = pd.read_csv(pred_path, encoding='latin-1')
        df_hist = pd.read_csv(data_path, encoding='latin-1')

    logging.info("Procesando datos unificados...")
    df_unico = prepare_unified_data(df_hist, df_pred)

    logging.info("Generando HTML de Predicciones...")
    html_content = get_dashboard_html(df_unico)

    output_file = output_dir / "dashboard_estrategico.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    logging.info(f"✅ Dashboard Predicciones generado: {output_file}")