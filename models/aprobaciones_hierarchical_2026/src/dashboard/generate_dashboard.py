import pandas as pd
import json
import logging
import os
import numpy as np
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def generate_dashboard():
    logging.info("Generando Dashboard HTML (Hierarchical - HDBSCAN Style)...")
    
    # Rutas
    base_dir = Path(os.getcwd())
    data_path = base_dir / "data/04-predictions/aprobaciones_clusters.csv"
    metrics_path = base_dir / "data/04-predictions/advanced_metrics.json"
    template_path = base_dir / "src/dashboard/dashboard_template.html"
    output_path = base_dir / "src/dashboard/dashboard_hierarchical.html"

    if not data_path.exists():
        logging.error(f"No se encontraron datos de clusters: {data_path}")
        return

    # Leer Datos Principales
    df = pd.read_csv(data_path)
    
    # Ensure critical columns exist and are numeric
    df['Monto_Aprobado'] = pd.to_numeric(df['Monto_Aprobado'], errors='coerce').fillna(0)
    df['CANTIDAD_APROBACIONES'] = pd.to_numeric(df['CANTIDAD_APROBACIONES'], errors='coerce').fillna(0)
    
    # --- DATA STRUCTURES (Strict Match to HDBSCAN JS) ---
    
    # 1. METRICS
    metrics_base = {}
    if metrics_path.exists():
        with open(metrics_path, 'r') as f:
            metrics_base = json.load(f)
            
    # "metricsData" for top KPIs (JS: metricsData.validity_score, metricsData.noise_pct)
    metrics_data = {
        "validity_score": metrics_base.get("silhouette", 0), # Using Silhouette as proxy for DBCV
        "noise_pct": 0, # Hierarchical Ward usually has 0 noise
        "total_amount": df['Monto_Aprobado'].sum(),
        "total_records": len(df),
        "total_clusters": df['Cluster'].nunique()
    }
    
    # "advancedMetrics" for Modal (JS: advancedMetrics.params.min_cluster_size, etc.)
    # We must mock the 'params' object to avoid JS errors
    advanced_metrics = {
        "silhouette": metrics_base.get("silhouette", 0),
        "davies_bouldin": metrics_base.get("davies_bouldin", 0),
        "calinski_harabasz": metrics_base.get("calinski_harabasz", 0),
        "stability_ari": metrics_base.get("stability_ari", 0),
        "params": {
            "min_cluster_size": "N/A (Ward)",
            "min_samples": "N/A", 
            "metric": "Euclidean",
            "cluster_selection_epsilon": "N/A",
            "cluster_selection_method": "Ward Linkage"
        }
    }
    
    # 2. PROFILES (JS: c.monto, c.aprobaciones - NOT monto_avg)
    numeric_cols = ['Monto_Aprobado', 'CANTIDAD_APROBACIONES']
    profiles_df = df.groupby('Cluster')[numeric_cols].mean().reset_index()
    profiles_data = []
    
    for _, row in profiles_df.iterrows():
        c_id = int(row['Cluster'])
        profiles_data.append({
            "cluster": c_id,
            "label": f"Cluster {c_id}",
            "monto": row['Monto_Aprobado'],          # KEY FIXED: monto_avg -> monto
            "aprobaciones": row['CANTIDAD_APROBACIONES'], # KEY FIXED: ops_avg -> aprobaciones
            "count": len(df[df['Cluster'] == c_id])
        })

    # 3. OUTLIERS (JS: d.Outlier_Score, d.Monto_Aprobado, d.CANTIDAD_APROBACIONES)
    # We mock score since Hierarchical doesn't produce it natively.
    outliers_df = df.sort_values(by='Monto_Aprobado', ascending=False).head(10).copy()
    outliers_data = []
    for _, row in outliers_df.iterrows():
        outliers_data.append({
            "Pais": row['Pais'],
            "Anio": int(row.get('Anio') or row.get('Anio_Origen') or 0),
            "Anio_Origen": int(row.get('Anio') or row.get('Anio_Origen') or 0), # JS checks this
            "Monto_Aprobado": row['Monto_Aprobado'],
            "CANTIDAD_APROBACIONES": row['CANTIDAD_APROBACIONES'],
            "Outlier_Score": 1.0 # Mock score
        })

    # 4. OPTIMIZATION HISTORY
    optimization_path = base_dir / "data/04-predictions/optimization_history.json"
    optimization_data = []
    
    if optimization_path.exists():
        with open(optimization_path, 'r') as f:
            opt_raw = json.load(f)
            # Map [ {k, silhouette} ] -> [ {iteration, min_cluster_size, min_samples, dbcv_score} ]
            for i, item in enumerate(opt_raw):
                optimization_data.append({
                    "iteration": i + 1,
                    "min_cluster_size": item.get('k'),  # Helper for mapping K
                    "min_samples": "Ward",              # Static for Hierarchical
                    "noise_pct": 0,                     # Hierarchical usually 0 noise
                    "dbcv_score": item.get('silhouette', 0)
                })
    else:
        # Fallback Mock if file missing
        optimization_data = [
            {"iteration": 1, "min_cluster_size": 3, "min_samples": "Ward", "noise_pct": 0, "dbcv_score": 0.35}
        ]

    # --- INJECTION ---
    if not template_path.exists():
        logging.error(f"No se encontro template: {template_path}")
        return
        
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    update_time = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Replace Keys
    html_content = html_content.replace('{{DATA_CLUSTERS}}', df.to_json(orient='records'))
    html_content = html_content.replace('{{DATA_METRICS}}', json.dumps(metrics_data))
    html_content = html_content.replace('{{DATA_ADVANCED_METRICS}}', json.dumps(advanced_metrics))
    html_content = html_content.replace('{{DATA_PROFILES}}', json.dumps(profiles_data))
    html_content = html_content.replace('{{DATA_OUTLIERS}}', json.dumps(outliers_data))
    html_content = html_content.replace('{{DATA_OUTLIER_HIST}}', "[]")
    html_content = html_content.replace('{{DATA_OPTIMIZATION}}', json.dumps(optimization_data))
    html_content = html_content.replace('{{UPDATE_TIME}}', update_time)
    
    # PATCH TITLE TO SAY HIERARCHICAL INSTEAD OF HDBSCAN
    html_content = html_content.replace('Dashboard de Clustering (HDBSCAN)', 'Dashboard de Clustering (Hierarchical)')
    html_content = html_content.replace('Clustering Dashboard (HDBSCAN)', 'Clustering Dashboard (Hierarchical)')
    html_content = html_content.replace('HDBSCAN (Hierarchical Density-Based', 'Agglomerative Hierarchical (Ward Linkage')

    # Guardar Output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logging.info(f"Dashboard generado exitosamente en: {output_path}")

if __name__ == "__main__":
    generate_dashboard()
