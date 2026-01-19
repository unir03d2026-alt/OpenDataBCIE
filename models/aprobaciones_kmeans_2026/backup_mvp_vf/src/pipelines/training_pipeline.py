import pandas as pd
import numpy as np
import yaml
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def train_kmeans(config_path):
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
    
    X = df[features].dropna().copy()
    
    # --- TRANSFORMACION (LOG) ---
    # Aplicar Log a Monto_Aprobado (features[0]) para reducir sesgo
    logging.info("Aplicando Log Transformation a Monto_Aprobado...")
    X[features[0]] = np.log1p(X[features[0]])
    
    # Estandarizacion
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Directorio de plots y datos
    plots_dir = Path(config['model']['plots_path'])
    plots_dir.mkdir(parents=True, exist_ok=True)
    predictions_dir = Path(config['model']['output_path']).parent
    predictions_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Metodo del Codo y Silueta
    max_k = config['model']['max_k']
    logging.info(f"Ejecutando Optimizacion (1 a {max_k})...")
    
    metrics_data = []
    wcss_list = []
    
    for k in range(1, max_k + 1):
        kmeans = KMeans(n_clusters=k, init='k-means++', random_state=config['model']['random_state'])
        labels = kmeans.fit_predict(X_scaled)
        wcss = kmeans.inertia_
        wcss_list.append(wcss)
        
        sil_score = 0
        if k > 1:
            sil_score = silhouette_score(X_scaled, labels)
            
        metrics_data.append({
            "k": k,
            "wcss": wcss,
            "silhouette": sil_score
        })
        
    # Guardar Metricas (WCSS + Silhouette)
    with open(predictions_dir / "metrics.json", "w") as f:
        json.dump(metrics_data, f)

    # Plot Elbow
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, max_k + 1), wcss_list, marker='o', linestyle='--')
    plt.title('Metodo del Codo (Log-Transformed)')
    plt.xlabel('K')
    plt.ylabel('WCSS')
    plt.grid(True)
    plt.savefig(plots_dir / 'elbow_method.png')
    plt.close()
    
    # 2. Entrenamiento Final
    optimal_k = config['model']['optimal_k']
    logging.info(f"Entrenando K-Means con k={optimal_k}...")
    
    kmeans = KMeans(n_clusters=optimal_k, init='k-means++', random_state=config['model']['random_state'], n_init=10)
    # Fit y Predict
    X['Cluster'] = kmeans.fit_predict(X_scaled)
    labels = X['Cluster'].values
    
    # --- METRICAS DE ROBUSTEZ ---
    # 1. Distancia al Centroide (Interpretabilidad)
    # X_scaled y cluster_centers_ estan en la misma escala
    distances = np.linalg.norm(X_scaled - kmeans.cluster_centers_[labels], axis=1)
    
    # 2. Silhouette Score del modelo final
    sil_score = silhouette_score(X_scaled, labels)
    logging.info(f"Modelo Final - Silhouette Score: {sil_score:.4f}")
    
    # --- EXPORTACION DE DATOS ---
    # Recuperar datos originales para el JSON
    # df ya tiene los indices alineados con X (dropna)
    df_export = df.loc[X.index].copy()
    df_export['Cluster'] = labels
    df_export['Distancia_Centroide'] = distances
    
    # Columnas a exportar
    export_cols = ['Pais', 'Anio', 'Monto_Aprobado', 'CANTIDAD_APROBACIONES', 'Cluster', 'Distancia_Centroide']
    if 'Sector_Economico' in df_export.columns:
        export_cols.append('Sector_Economico')
    if 'Mes' in df_export.columns:
        export_cols.append('Mes')
        
    clustered_data = df_export[export_cols].to_dict(orient='records')
    
    # Guardar Clusters JSON
    with open(predictions_dir / "clusters.json", "w", encoding='utf-8') as f:
        json.dump(clustered_data, f)

    # --- CENTROIDES (Inverse Transform) ---
    centers_scaled = kmeans.cluster_centers_
    centers_log = scaler.inverse_transform(centers_scaled)
    centers_real = centers_log.copy()
    centers_real[:, 0] = np.expm1(centers_real[:, 0]) # Revertir Log
    
    centroids_data = []
    for i, center in enumerate(centers_real):
        centroids_data.append({
            "cluster": i,
            "monto": center[0],
            "aprobaciones": center[1]
        })
        
    with open(predictions_dir / "centroids.json", "w") as f:
        json.dump(centroids_data, f)
        
    # Guardar Metricas Globales (Solo si no existen o para actualizar)
    # Ya se guardaron en el paso de validacion, pero podriamos agregar el score global aqui
    # Por ahora confiamos en metrics.json generado arriba
    
    # Guardar CSV final
    df_export.to_csv(config['model']['output_path'], index=False)
    logging.info(f"Resultados guardados en: {config['model']['output_path']}")
    
    # 3. Scatter Plot (con datos originales para visualizacion humana)
    # Asegurar que df tenga la columna Cluster
    df.loc[X.index, 'Cluster'] = labels
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df, 
        x=features[0], 
        y=features[1], 
        hue='Cluster', 
        palette='viridis',
        s=100, 
        alpha=0.7
    )
    plt.title(f'Clustering K-Means (Log-Transformed Logic)')
    plt.savefig(plots_dir / 'kmeans_clusters.png')
    plt.close()

if __name__ == "__main__":
    train_kmeans("config/local.yaml")
