import pandas as pd
import json
import logging
import os
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def generate_dashboard():
    logging.info("Generando Dashboard HTML...")
    
    # Rutas
    base_dir = Path(os.getcwd())
    data_path = base_dir / "data/04-predictions/aprobaciones_clusters.csv"
    dendro_path = base_dir / "data/05-plots/dendrogram_chart.json" # Saved in 05-plots by training pipeline? No, output_dir was 04-predictions usually, let's check training_pipeline.py.
    # Training pipeline said: output_dir = Path(config['model']['output_path']).parent -> data/04-predictions
    # But later: dendro_path = output_dir / "dendrogram_chart.json"
    # Actually, let's verify training_pipeline.py output location in logical check.
    # Correction: I will check where I saved it.
    
    # In training_pipeline.py:
    # output_dir = Path(config['model']['output_path']).parent  (which is data/04-predictions)
    # dendro_path = output_dir / "dendrogram_chart.json"
    
    dendro_path = base_dir / "data/04-predictions/dendrogram_chart.json"
    template_path = base_dir / "src/dashboard/dashboard_template.html"
    output_path = base_dir / "src/dashboard/dashboard_ranking.html" # Wait, Hierarchical dashboard naming? dashboard_clustering.html or dashboard_hierarchical.html?
    output_path = base_dir / "src/dashboard/dashboard_gmm.html"

    if not data_path.exists():
        logging.error(f"No se encontraron datos de clusters: {data_path}")
        return

    # Leer Datos
    df = pd.read_csv(data_path)
    data_clusters_json = df.to_json(orient='records')
    
    # Leer Dendrograma
    dendro_json = "{}"
    if dendro_path.exists():
        with open(dendro_path, 'r') as f:
            # It's already valid JSON
            dendro_json = f.read()
    else:
        logging.warning("No se encontro archivo de Dendrograma.")

    # Leer Template
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Leer Metricas Avanzadas
    metrics_path = base_dir / "data/04-predictions/advanced_metrics.json"
    metrics = {}
    if metrics_path.exists():
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
            
    # Timestamp
    update_time = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Inyectar Datos
    html_content = html_content.replace('{{DATA_CLUSTERS}}', data_clusters_json)
    html_content = html_content.replace('{{UPDATE_TIME}}', update_time)
    
    # Inyectar Metricas
    def fmt(val, decimals=2):
        return f"{val:.{decimals}f}" if isinstance(val, (int, float)) else "-"
        
    html_content = html_content.replace('{{METRIC_PROB}}', fmt(metrics.get("avg_probability", 0), 3))
    html_content = html_content.replace('{{METRIC_AIC}}', fmt(metrics.get("aic", 0), 0))
    html_content = html_content.replace('{{METRIC_BIC}}', fmt(metrics.get("bic", 0), 0))
    html_content = html_content.replace('{{METRIC_SIL}}', fmt(metrics.get("silhouette", 0), 4))
    html_content = html_content.replace('{{METRIC_ARI}}', fmt(metrics.get("stability_ari", 0), 4))

    # Guardar Output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logging.info(f"Dashboard generado exitosamente en: {output_path}")

if __name__ == "__main__":
    generate_dashboard()
