import pandas as pd
import numpy as np
import yaml
import logging
import json
import plotly.figure_factory as ff
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering
import scipy.cluster.hierarchy as sch

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def train_hierarchical(config_path):
    # Cargar config
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    data_path = Path(config['data']['processed_path'])
    if not data_path.exists():
        logging.error(f"No se encontro el archivo de datos: {data_path}")
        return

    logging.info("Cargando datos preprocesados...")
    df = pd.read_csv(data_path)
    
    # Seleccion de features
    features = config['model']['features']
    logging.info(f"Features seleccionados: {features}")
    X = df[features].dropna()
    
    # Estandarizacion
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Directorio de plots y datos
    plots_dir = Path(config['model']['plots_path'])
    output_dir = Path(config['model']['output_path']).parent
    plots_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Generar Dendrograma (Interactive JSON for Dashboard)
    logging.info("Generando Dendrograma...")
    # Sample if too large to avoid massive JSON
    # For < 1000 items, it's fine.
    
    # Use Plotly Figure Factory
    # Labels: Paises if sensible, otherwise default
    labels = df.loc[X.index, 'Pais'].tolist()
    
    fig = ff.create_dendrogram(X_scaled, labels=labels, orientation='bottom')
    fig.update_layout(
        title='Dendrograma de Aprobaciones',
        xaxis_title='Países',
        yaxis_title='Distancia Euclidiana (Ward)'
    )
    
    # Save as JSON for Dashboard injection
    import plotly
    dendro_path = output_dir / "dendrogram_chart.json"
    with open(dendro_path, "w") as f:
        json.dump(fig.to_dict(), f, cls=plotly.utils.PlotlyJSONEncoder)
    logging.info(f"Dendrograma guardado en: {dendro_path}")
    
    # 2. Entrenamiento Final (Agglomerative)
    n_clusters = config['model']['n_clusters']
    linkage = config['model']['linkage']
    logging.info(f"Entrenando AgglomerativeClustering (k={n_clusters}, linkage={linkage})...")
    
    hc = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
    clusters = hc.fit_predict(X_scaled)
    
    # Agregar clusters al dataframe original
    df.loc[X.index, 'Cluster'] = clusters
    df['Cluster'] = df['Cluster'].fillna(-1).astype(int)
    
    # Guardar resultados CSV
    output_path = Path(config['model']['output_path'])
    df.to_csv(output_path, index=False)
    logging.info(f"Resultados guardados en: {output_path}")

if __name__ == "__main__":
    train_hierarchical("config/local.yaml")
