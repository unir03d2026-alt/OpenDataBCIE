import pandas as pd
import requests
import yaml
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def run_etl(config_path):
    # Cargar configuracion
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Extraccion de datos
    url = config['api']['base_url']
    resource_id = config['api']['resource_id']
    limit = config['api']['limit']

    logging.info("Conectando al API CKAN del BCIE...")
    
    try:
        params = {'resource_id': resource_id, 'limit': limit}
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data_json = response.json()
        if not data_json['success']:
            raise Exception("API Error: La consulta fallo.")
            
        records = data_json['result']['records']
        df = pd.DataFrame(records)
        logging.info(f"Descarga completada: {len(df)} registros.")

        # Guardar copia cruda
        raw_path = Path(config['data']['raw_path'])
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(raw_path, index=False)

    except Exception as e:
        logging.error(f"Error descargando: {e}")
        raise

    # Limpieza y Transformacion
    logging.info("Adaptando columnas...")

    # Renombrar columnas
    rename_map = config['data']['column_renames']
    df.rename(columns=rename_map, inplace=True)

    # Validar columna de monto
    val_col = config['data']['value_col']
    if val_col not in df.columns:
        raise KeyError(f"La columna de valor '{val_col}' no se encontro.")
        
    df[val_col] = pd.to_numeric(df[val_col], errors='coerce')

    # Crear fecha a partir del anio
    # El API devuelve ANIO_APROBACION (renombrado a Anio_Origen)
    if 'Anio_Origen' in df.columns:
        # Convertir a fecha YYYY-01-01
        df['Fecha_Aprobacion'] = pd.to_datetime(df['Anio_Origen'].astype(str) + '-01-01')
    else:
        raise KeyError("No se encontro la columna de anio original.")

    # Limpieza final
    df = df.dropna(subset=['Fecha_Aprobacion', val_col])
    
    # Estandarizar columna de grupo (Pais)
    group_col = config['data']['group_col']
    if group_col in df.columns:
        df[group_col] = df[group_col].astype(str).str.upper().str.strip()

    # Variables adicionales
    df['Anio'] = df['Fecha_Aprobacion'].dt.year
    df['Mes'] = df['Fecha_Aprobacion'].dt.month

    # Guardar archivo procesado
    processed_path = Path(config['data']['processed_path'])
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)
    
    logging.info(f"ETL Terminado. Datos listos en: {processed_path}")

if __name__ == "__main__":
    run_etl("config/local.yaml")