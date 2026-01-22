import pandas as pd
import requests
import yaml
import logging
from pathlib import Path

# Configuración del registro de eventos (logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def run_etl(config_path):
    """
    Ejecuta el proceso ETL (Extracción, Transformación y Carga).
    1. Descarga los datos del API CKAN del BCIE.
    2. Normaliza y limpia los datos.
    3. Genera un archivo CSV procesado listo para el modelado.
    """
    # 1. Cargar archivo de configuración
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 2. Extracción de Datos
    url = config['api']['base_url']
    resource_id = config['api']['resource_id']
    limit = config['api']['limit']

    logging.info("Estableciendo conexión con el API de Datos Abiertos del BCIE...")
    
    try:
        params = {'resource_id': resource_id, 'limit': limit}
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data_json = response.json()
        if not data_json['success']:
            raise Exception("Error del API: La consulta no fue exitosa.")
            
        records = data_json['result']['records']
        df = pd.DataFrame(records)
        logging.info(f"Descarga exitosa: Se han obtenido {len(df)} registros.")

        # Guardar copia de seguridad de los datos crudos
        raw_path = Path(config['data']['raw_path'])
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(raw_path, index=False)

    except Exception as e:
        logging.error(f"Error durante la descarga de datos: {e}")
        raise

    # 3. Transformación y Limpieza
    logging.info("Iniciando proceso de limpieza y transformación de datos...")

    # Renombrar columnas según el mapeo de configuración
    rename_map = config['data']['column_renames']
    df.rename(columns=rename_map, inplace=True)

    # Validar existencia de la columna de valor monetario
    val_col = config['data']['value_col']
    if val_col not in df.columns:
        raise KeyError(f"La columna requerida '{val_col}' no se encuentra en el conjunto de datos.")
        
    df[val_col] = pd.to_numeric(df[val_col], errors='coerce')

    # Generación de la columna de fecha
    # El API proporciona 'ANIO_APROBACION' (renombrado a Anio_Origen)
    if 'Anio_Origen' in df.columns:
        # Se asume el primer día del año para construir la fecha
        df['Fecha_Aprobacion'] = pd.to_datetime(df['Anio_Origen'].astype(str) + '-01-01')
    else:
        raise KeyError("No se encontró la columna de año original para construir la fecha.")

    # Eliminación de registros con datos faltantes clave
    df = df.dropna(subset=['Fecha_Aprobacion', val_col])
    
    # Estandarización de la columna de agrupación (País)
    group_col = config['data']['group_col']
    if group_col in df.columns:
        df[group_col] = df[group_col].astype(str).str.upper().str.strip()

    # Creación de variables temporales adicionales
    df['Anio'] = df['Fecha_Aprobacion'].dt.year
    df['Mes'] = df['Fecha_Aprobacion'].dt.month

    # 4. Carga (Guardado de datos procesados)
    processed_path = Path(config['data']['processed_path'])
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)
    
    logging.info(f"Proceso ETL finalizado correctamente. Datos disponibles en: {processed_path}")

if __name__ == "__main__":
    run_etl("config/local.yaml")
