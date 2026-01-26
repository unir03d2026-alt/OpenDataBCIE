"""
Dashboard Generation Module.

This script assembles the final HTML dashboard by injecting the processed data
(JSON clusters, metrics, and centroids) into the HTML template.

Key operations:
1. Reads the HTML template.
2. Loads the model outputs (clusters, metrics, centroids) from JSON/CSV files.
3. Injects the data into the template's placeholder variables.
4. Saves the standalone HTML file for distribution.
"""

import pandas as pd
import logging
import os
from pathlib import Path
from datetime import datetime

# Configure module-level logger
logger = logging.getLogger(__name__)

def generate_dashboard():
    """
    Generates the interactive HTML dashboard.
    """
    logger.info("Generating Report Interface...")
    
    # Path Configuration
    base_dir = Path(os.getcwd())
    data_path = base_dir / "data/04-predictions/aprobaciones_clusters.csv"
    metrics_path = base_dir / "data/04-predictions/metrics.json"
    adv_metrics_path = base_dir / "data/04-predictions/advanced_metrics.json"
    centroids_path = base_dir / "data/04-predictions/centroids.json"
    template_path = base_dir / "src/dashboard/dashboard_template.html"
    output_path = base_dir / "src/dashboard/dashboard_clustering.html"

    # Validation
    if not data_path.exists():
        logger.error(f"Prediction data not found at: {data_path}")
        return

    # Data Injection Preparation
    try:
        # 1. Main Data (Clusters)
        df = pd.read_csv(data_path)
        data_clusters_json = df.to_json(orient='records')
        
        # 2. Validation Metrics
        metrics_json = "[]"
        if metrics_path.exists():
            with open(metrics_path, 'r', encoding='utf-8') as f:
                metrics_json = f.read()
        
        # 3. Centroids (Profiles)
        centroids_json = "[]"
        if centroids_path.exists():
            with open(centroids_path, 'r', encoding='utf-8') as f:
                centroids_json = f.read()

        # 4. Advanced Metrics
        adv_metrics_json = "{}"
        if adv_metrics_path.exists():
            with open(adv_metrics_path, 'r', encoding='utf-8') as f:
                adv_metrics_json = f.read()

        # 5. Template Rendering
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        update_time = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Injection
        html_content = html_content.replace('{{DATA_CLUSTERS}}', data_clusters_json)
        html_content = html_content.replace('{{DATA_METRICS}}', metrics_json)
        html_content = html_content.replace('{{DATA_ADVANCED_METRICS}}', adv_metrics_json)
        html_content = html_content.replace('{{DATA_CENTROIDS}}', centroids_json)
        html_content = html_content.replace('{{UPDATE_TIME}}', update_time)

        # Output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Dashboard successfully generated: {output_path}")

    except Exception as e:
        logger.error(f"Dashboard generation failed: {e}")
        raise

if __name__ == "__main__":
    generate_dashboard()
