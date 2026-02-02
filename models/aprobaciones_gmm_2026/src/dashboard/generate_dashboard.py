import json
import logging
from pathlib import Path
import pandas as pd
import numpy as np

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_dashboard():
    logging.info("Generando Dashboard GMM (Probabilistic Design)...")
    
    # Rutas Base
    base_dir = Path.cwd()
    # Adjust path if running from root or src
    if base_dir.name == 'src':
        base_dir = base_dir.parent.parent
    elif base_dir.name == 'dashboard':
        base_dir = base_dir.parent.parent.parent
        
    # Project specific path
    project_dir = base_dir / "models" / "aprobaciones_gmm_2026"
    if not project_dir.exists():
         # Maybe we are already inside the project dir?
         if (base_dir / "src").exists():
             project_dir = base_dir

    data_dir = project_dir / "data" / "04-predictions"
    src_dir = project_dir / "src" / "dashboard"
    
    # Input Files
    files = {
        "clusters": data_dir / "clusters.json",
        "metrics": data_dir / "advanced_metrics.json",
        "optimization": data_dir / "optimization_history.json",
        "covariances": data_dir / "covariances.json",
        "centroids": data_dir / "centroids.json"
    }
    
    # Template & Output
    template_path = src_dir / "dashboard_gmm_template.html"
    output_path = src_dir / "dashboard_gmm.html"
    
    # Check existence
    for name, path in files.items():
        if not path.exists():
            logging.error(f"Missing file: {path}")
            return

    # Load Data
    data = {}
    for name, path in files.items():
        with open(path, 'r', encoding='utf-8') as f:
            data[name] = json.load(f)
            
    # Load Template
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    # Injection
    logging.info("Injecting data into template...")
    
    # Helper to safe inject JSON
    def inject(key, py_data):
        json_str = json.dumps(py_data)
        # Try both formats
        res = html.replace(f'{{{{{key}}}}}', json_str)
        res = res.replace(f'{{{{ {key} }}}}', json_str)
        return res
        
    html = inject('DATA_CLUSTERS', data['clusters'])
    html = inject('DATA_METRICS', data['metrics'])
    html = inject('DATA_OPTIMIZATION', data['optimization'])
    html = inject('DATA_COVARIANCES', data['covariances'])
    html = inject('DATA_CENTROIDS', data['centroids'])
    
    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    logging.info(f"Dashboard generated successfully: {output_path}")

if __name__ == "__main__":
    generate_dashboard()
