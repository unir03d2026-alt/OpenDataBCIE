"""
Pipeline para generar el Dashboard Ejecutivo Histórico (Datos Reales).
Ruta: src/pipelines/historical_pipeline.py
"""
import yaml
import pandas as pd
import logging
import os
from pathlib import Path

# Imports locales
from src.dashboard.logic import process_executive_data
from src.dashboard.logic import process_executive_data
from src.dashboard.layout import get_executive_html
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def generate_historical_report(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    base_dir = Path(os.getcwd())
    
    # RUTA ESPECIFICA PARA DATOS REALES LIMPIOS
    data_path = base_dir / "data/02-preprocessed/aprobaciones_limpias.csv"
    output_dir = base_dir / "src/dashboard"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not data_path.exists():
        logging.error(f"❌ No se encontró el archivo de datos reales en: {data_path}")
        return

    logging.info(f"Cargando datos reales desde: {data_path}")
    try:
        df = pd.read_csv(data_path, encoding='utf-8-sig')
    except:
        df = pd.read_csv(data_path, encoding='latin-1')

    logging.info("Procesando datos para indicadores ejecutivos...")
    data_processed = process_executive_data(df)
    
    logging.info("Generando HTML Ejecutivo...")
    fecha_actualizacion = datetime.now().strftime('%d/%m/%Y %H:%M')
    anio_actual = datetime.now().year
    
    html_content = get_executive_html(data_processed, fecha_actualizacion, anio_actual)
    
    output_file = output_dir / "dashboard_ejecutivo.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    logging.info(f"✅ Dashboard Ejecutivo generado exitosamente: {output_file}")

if __name__ == "__main__":
    generate_historical_report("config/local.yaml")