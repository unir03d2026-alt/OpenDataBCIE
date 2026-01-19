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
    # User didn't specify, but for K-Means we used dashboard_clustering.html. Let's use dashboard_hierarchical.html to distinguish.
    output_path = base_dir / "src/dashboard/dashboard_hierarchical.html"

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

    # Timestamp
    update_time = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Inyectar Datos
    html_content = html_content.replace('{{DATA_CLUSTERS}}', data_clusters_json)
    html_content = html_content.replace('{{DATA_DENDRO}}', dendro_json)
    html_content = html_content.replace('{{UPDATE_TIME}}', update_time)

    # Guardar Output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logging.info(f"Dashboard generado exitosamente en: {output_path}")

if __name__ == "__main__":
    generate_dashboard()
