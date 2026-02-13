"""
ETL Pipeline Module.

This module handles the Extraction, Transformation, and Loading (ETL) of data from the BCIE CKAN API.
It performs the following steps:
1. Connects to the API endpoint configured in local.yaml.
2. Extracts raw records.
3. Cleans and transforms the dataset (renaming columns, converting types, filtering valid records).
4. Saves both raw and processed datasets to the local filesystem.
"""

import pandas as pd
import requests
import yaml
import logging
from pathlib import Path

# Configure module-level logger
logger = logging.getLogger(__name__)

def run_etl(config_path):
    """
    Executes the ETL process based on the provided configuration file.

    Args:
        config_path (str): Path to the YAML configuration file.
    
    Raises:
        Exception: If API connection fails or critical columns are missing.
    """
    # Load configuration
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # --- EXTRACTION ---
    url = config['api']['base_url']
    resource_id = config['api']['resource_id']
    limit = config['api']['limit']

    logger.info("Connecting to BCIE CKAN API...")
    
    try:
        params = {'resource_id': resource_id, 'limit': limit}
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data_json = response.json()
        if not data_json['success']:
            raise Exception("API Error: Query failed.")
            
        records = data_json['result']['records']
        df = pd.DataFrame(records)
        logger.info(f"Download complete: {len(df)} records retrieved.")

        # Save Raw Data
        raw_path = Path(config['data']['raw_path'])
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(raw_path, index=False)

    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise

    # --- TRANSFORMATION ---
    logger.info("Transforming and cleaning data...")

    # Column Renaming
    rename_map = config['data']['column_renames']
    df.rename(columns=rename_map, inplace=True)

    # Value Validation
    val_col = config['data']['value_col']
    if val_col not in df.columns:
        raise KeyError(f"Value column '{val_col}' not found in dataset.")
        
    df[val_col] = pd.to_numeric(df[val_col], errors='coerce')

    # Date Engineering
    # API returns 'Anio_Origen' (Approval Year)
    if 'Anio_Origen' in df.columns:
        df['Fecha_Aprobacion'] = pd.to_datetime(df['Anio_Origen'].astype(str) + '-01-01')
    else:
        raise KeyError("Original year column not found.")

    # Null Handling
    df = df.dropna(subset=['Fecha_Aprobacion', val_col])
    
    # Standardization (Group/Country)
    group_col = config['data']['group_col']
    if group_col in df.columns:
        df[group_col] = df[group_col].astype(str).str.upper().str.strip()

    # Derived Features
    df['Anio'] = df['Fecha_Aprobacion'].dt.year
    df['Mes'] = df['Fecha_Aprobacion'].dt.month

    # --- LOADING ---
    processed_path = Path(config['data']['processed_path'])
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)
    
    logger.info(f"ETL Completed. Processed data saved to: {processed_path}")

if __name__ == "__main__":
    # For standalone testing
    run_etl("config/local.yaml")

