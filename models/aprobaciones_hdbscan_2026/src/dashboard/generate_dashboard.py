"""
Dashboard Generation Module.

This script assembles the final interactive HTML dashboard by injecting the processed data
(JSON clusters, metrics, profiles, outliers) from a specific execution run into the HTML template.

Key operations:
1. Identifies the specific run directory using `run_id`.
2. Loads all model outputs (metrics, profiles, distributions) from JSON files.
3. Injects the data into the template's placeholder variables.
4. Saves the standalone HTML file within the run directory.
"""

import logging
import os
import yaml
from pathlib import Path
from datetime import datetime

# Configure module-level logger
logger = logging.getLogger(__name__)

def generate_dashboard(config_path="config/local.yaml", run_id=None):
    """
    Generates the interactive HTML dashboard for a specific run.
    
    Args:
        config_path (str): Path to YAML config.
        run_id (str): Unique Run ID to generate dashboard for.
    """
    logger.info(f"Generating Dashboard for Run ID: {run_id}")
    
    # 1. Load Config & Resolve Paths
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    base_dir = Path(os.getcwd())
    
    if run_id:
        run_dir = base_dir / config["runs"]["output_root"] / run_id
    else:
        # Fallback to generic prediction path (legacy support or latest)
        # However, new pipeline strictness requires run_id.
        logger.warning("No run_id provided. Using default prediction path (might fail if new structure enforced).")
        run_dir = base_dir / "data/04-predictions"

    if not run_dir.exists():
        logger.error(f"Run directory not found: {run_dir}")
        return

    # Artifact Paths
    # Note: Using new naming convention defined in training_pipeline
    data_path = run_dir / f'{config["model"]["output_name"]}.csv' # CSV for reference if needed, but we typically inject JSON
    
    # We might read CSV to convert to JSON for the scatter plot data injection
    # Or expect a clusters.json. Training pipeline saves CSV. Let's load CSV and convert to JSON here.
    
    metrics_path = run_dir / "metrics.json"
    adv_metrics_path = run_dir / "advanced_metrics.json"
    profiles_path = run_dir / "cluster_profiles.json"
    outliers_path = run_dir / "outliers_top10.json"
    hist_path = run_dir / "outlier_histogram.json"
    opt_path = run_dir / "optimization_results.json"
    
    template_path = base_dir / "src/dashboard/dashboard_template.html"
    output_path = run_dir / "dashboard_clustering.html"

    # 2. Data Loading & Injection Preparation
    try:
        # A) Clusters Data (Main Dataset)
        if not data_path.exists():
            raise FileNotFoundError(f"Cluster data not found: {data_path}")
        
        import pandas as pd
        df = pd.read_csv(data_path)
        # Convert to JSON for injection
        data_clusters_json = df.to_json(orient='records')
        
        # B) Validation Metrics
        metrics_json = "{}"
        if metrics_path.exists():
            metrics_json = metrics_path.read_text(encoding='utf-8')
        
        # C) Advanced Metrics
        adv_metrics_json = "{}"
        if adv_metrics_path.exists():
            adv_metrics_json = adv_metrics_path.read_text(encoding='utf-8')

        # D) Cluster Profiles (fka Centroids)
        profiles_json = "[]"
        if profiles_path.exists():
            profiles_json = profiles_path.read_text(encoding='utf-8')

        # E) Outliers Top 10
        outliers_json = "[]"
        if outliers_path.exists():
            outliers_json = outliers_path.read_text(encoding='utf-8')

        # F) Outlier Histogram
        hist_json = "[]"
        if hist_path.exists():
            hist_json = hist_path.read_text(encoding='utf-8')

        # G) Optimization History
        opt_json = "[]"
        if opt_path.exists():
            opt_json = opt_path.read_text(encoding='utf-8')

        # 3. Template Rendering
        if not template_path.exists():
             raise FileNotFoundError(f"Template not found: {template_path}")

        html_content = template_path.read_text(encoding='utf-8')
        update_time = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Replacements using contract keys
        # Note: Template must trigger on these specific keys
        html_content = html_content.replace('{{DATA_CLUSTERS}}', data_clusters_json)
        html_content = html_content.replace('{{DATA_METRICS}}', metrics_json)
        html_content = html_content.replace('{{DATA_ADVANCED_METRICS}}', adv_metrics_json)
        html_content = html_content.replace('{{DATA_PROFILES}}', profiles_json) 
        html_content = html_content.replace('{{DATA_OUTLIERS}}', outliers_json) 
        html_content = html_content.replace('{{DATA_OUTLIER_HIST}}', hist_json) 
        html_content = html_content.replace('{{DATA_OPTIMIZATION}}', opt_json) 
        html_content = html_content.replace('{{UPDATE_TIME}}', update_time)

        # 4. Save Output
        output_path.write_text(html_content, encoding='utf-8')
        logger.info(f"Dashboard successfully generated: {output_path}")

    except Exception as e:
        logger.error(f"Dashboard generation failed: {e}")
        raise

if __name__ == "__main__":
    generate_dashboard()
