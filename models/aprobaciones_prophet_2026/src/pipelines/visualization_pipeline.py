"""
Pipeline de generación de visualizaciones (PREDICCIONES PROPHET).
Ruta: src/pipelines/visualization_pipeline.py
"""
import yaml
import pandas as pd
import logging
import os
from pathlib import Path
from datetime import datetime

# Importación de los módulos locales del dashboard
from src.dashboard.logic import prepare_unified_data, process_executive_data
from src.dashboard.layout import get_dashboard_html, get_executive_html

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def generate_plots(config_path):
    """Genera el Dashboard de Predicciones (Prophet) y Ejecutivo."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    base_dir = Path(os.getcwd())
    data_path = base_dir / config['data']['processed_path']
    pred_path = base_dir / "data/04-predictions/predicciones_bcie.csv"
    
    # Nuevas rutas de salida
    output_dir_strat = base_dir / "src/dashboard/Estrategico"
    output_dir_exec = base_dir / "src/dashboard/Ejecutivo"
    
    output_dir_strat.mkdir(parents=True, exist_ok=True)
    output_dir_exec.mkdir(parents=True, exist_ok=True)

    if not pred_path.exists():
        logging.error(f"No se encontró el archivo de predicciones en: {pred_path}")
        return

    logging.info("Cargando datos para Predicción...")
    try:
        try:
            df_pred = pd.read_csv(pred_path, encoding='utf-8-sig')
            df_hist = pd.read_csv(data_path, encoding='utf-8-sig')
        except:
            df_pred = pd.read_csv(pred_path, encoding='latin-1')
            df_hist = pd.read_csv(data_path, encoding='latin-1')

        # --- DASHBOARD ESTRATÉGICO (PREDICTIVO) ---
        logging.info("Procesando datos unificados (Estratégico)...")
        df_unico = prepare_unified_data(df_hist, df_pred)

        logging.info("Generando HTML de Predicciones...")
        html_content = get_dashboard_html(df_unico)

        output_file_strat = output_dir_strat / "dashboard_estrategico.html"
        with open(output_file_strat, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logging.info(f"✅ Dashboard Estratégico generado: {output_file_strat}")

        # --- DASHBOARD EJECUTIVO (HISTÓRICO) ---
        logging.info("Procesando datos para Ejecutivo (Histórico)...")
        
        # Procesar datos históricos para el dashboard ejecutivo
        data_processed = process_executive_data(df_hist)
        
        # Variables de tiempo
        now = datetime.now()
        fecha_actualizacion = now.strftime("%d/%m/%Y %H:%M")
        anio_actual = now.year

        logging.info("Generando HTML Ejecutivo...")
        html_exec = get_executive_html(data_processed, fecha_actualizacion, anio_actual)

        output_file_exec = output_dir_exec / "dashboard_ejecutivo.html"
        with open(output_file_exec, "w", encoding="utf-8") as f:
            f.write(html_exec)

        logging.info(f"✅ Dashboard Ejecutivo generado: {output_file_exec}")

    except Exception as e:
        import traceback
        logging.error(f"❌ Error en la generación del dashboard: {e}")
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    # Si se ejecuta directamente, buscar config local
    if Path("local.yaml").exists():
        generate_plots("local.yaml")
    elif Path("config/local.yaml").exists():
        generate_plots("config/local.yaml")
    else:
        # Fallback o error
        logging.error("No se encontró local.yaml para ejecutar directamente.")