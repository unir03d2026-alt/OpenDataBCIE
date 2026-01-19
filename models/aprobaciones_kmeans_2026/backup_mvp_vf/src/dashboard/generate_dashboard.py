import pandas as pd
import json
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def generate_dashboard():
    logging.info("Generando Dashboard HTML...")
    
    # Rutas
    base_dir = Path(os.getcwd())
    data_path = base_dir / "data/04-predictions/aprobaciones_clusters.csv"
    metrics_path = base_dir / "data/04-predictions/metrics.json"
    centroids_path = base_dir / "data/04-predictions/centroids.json"
    template_path = base_dir / "src/dashboard/dashboard_template.html"
    output_path = base_dir / "src/dashboard/dashboard_clustering.html"

    if not data_path.exists():
        logging.error(f"No se encontraron datos de clusters: {data_path}")
        return

    # Leer Datos
    df = pd.read_csv(data_path)
    data_clusters_json = df.to_json(orient='records')
    
    # Leer Metricas (WCSS + Silhouette)
    metrics_json = "[]"
    if metrics_path.exists():
        with open(metrics_path, 'r') as f:
            metrics_json = f.read() # Already valid JSON
    
    # Leer Centroides
    centroids_json = "[]"
    if centroids_path.exists():
        with open(centroids_path, 'r') as f:
            centroids_json = f.read()

    # Leer Template
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Timestamp Actual
    from datetime import datetime
    update_time = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Inyectar Datos
    html_content = html_content.replace('{{DATA_CLUSTERS}}', data_clusters_json)
    html_content = html_content.replace('{{DATA_METRICS}}', metrics_json)
    html_content = html_content.replace('{{DATA_CENTROIDS}}', centroids_json)
    html_content = html_content.replace('{{UPDATE_TIME}}', update_time)

    # Guardar Output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logging.info(f"Dashboard generado exitosamente en: {output_path}")

if __name__ == "__main__":
    generate_dashboard()
