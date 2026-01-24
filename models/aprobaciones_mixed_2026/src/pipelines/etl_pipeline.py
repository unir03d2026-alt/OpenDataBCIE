"""
ETL Pipeline Module.

This module handles the Extraction, Transformation, and Loading (ETL) of data
from the BCIE CKAN API to a processed CSV ready for machine learning.

MLOps Standards:
- Modular functions for Extract, Transform, Load.
- Type hinting.
- Google-style docstrings.
- Reproducible transformations.
"""

import pandas as pd
import requests
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure module-level logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> Dict[str, Any]:
    """Loads configuration from a YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def extract_data(config: Dict[str, Any]) -> pd.DataFrame:
    """
    Extracts data from the configured API source or local cache.

    Args:
        config (dict): Configuration dictionary containing API details.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the raw data records.
    
    Raises:
        Exception: If API query fails and no local cache is available.
    """
    url = config['api']['base_url']
    resource_id = config['api']['resource_id']
    limit = config['api']['limit']
    raw_path = Path(config['data']['raw_path'])

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

        # Save Raw Data Cache
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(raw_path, index=False)
        return df

    except Exception as e:
        logger.warning(f"Download failed: {e}. Attempting to load from local raw path...")
        if raw_path.exists():
            df = pd.read_csv(raw_path)
            logger.info(f"Loaded {len(df)} records from local cache: {raw_path}")
            return df
        else:
            logger.error("Local raw file not found. ETL failed.")
            raise

def clean_data(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Performs initial data cleaning and validation.

    Args:
        df: Raw DataFrame.
        config: Configuration dict.

    Returns:
        Cleaned DataFrame.
    """
    logger.info("Cleaning raw data...")
    
    # 1. Column Renaming
    rename_map = config['data']['column_renames']
    df.rename(columns=rename_map, inplace=True)

    # 2. Value Validation
    val_col = config['data']['value_col']
    if val_col not in df.columns:
        raise KeyError(f"Value column '{val_col}' not found in dataset.")
        
    df[val_col] = pd.to_numeric(df[val_col], errors='coerce')

    # 3. Date Engineering
    if 'Anio_Origen' in df.columns:
        df['Fecha_Aprobacion'] = pd.to_datetime(df['Anio_Origen'].astype(str) + '-01-01')
    else:
        raise KeyError("Original year column not found.")

    # 4. Null Handling
    df = df.dropna(subset=['Fecha_Aprobacion', val_col])
    
    # 5. String Standardization
    group_col = config['data']['group_col']
    if group_col in df.columns:
        df[group_col] = df[group_col].astype(str).str.upper().str.strip()

    # 6. Sector Cleaning
    if 'Sector_Economico' in df.columns:
        df['Sector_Economico'] = df['Sector_Economico'].astype(str).str.strip().str.title()
    
    return df

def feature_engineering(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Generates derived features and performs aggregations.

    Args:
        df: Cleaned record-level DataFrame.
        config: Configuration dict.

    Returns:
        Aggregated DataFrame with business features (Country-Year level).
    """
    logger.info("Generating features and aggregating...")
    
    # 1. Temporal Features
    df['Anio'] = df['Fecha_Aprobacion'].dt.year
    df['Decada'] = (df['Anio'] // 10 * 10).astype(str) + 's'

    # 2. Aggregation to Country-Year
    group_col = config['data']['group_col'] # 'Pais'
    val_col = config['data']['value_col']   # 'Monto_Aprobado'
    
    def top_sector(x):
        return x.value_counts().index[0] if len(x) > 0 else 'Unknown'

    group_keys = [group_col, 'Anio', 'Decada']
    
    # Identify unique ID column
    id_col = 'Numero_Identificacion' if 'Numero_Identificacion' in df.columns else '_id'
    if id_col not in df.columns:
        df['__dummy_id'] = 1
        id_col = '__dummy_id'

    df_agg = df.groupby(group_keys).agg(
        Monto_Aprobado=(val_col, 'sum'),
        CANTIDAD_APROBACIONES=(id_col, 'count'), 
        Sector_Economico=('Sector_Economico', top_sector)
    ).reset_index()

    # 3. Categorize Country Type
    def categorize_pais(pais: str) -> str:
        founders = ['GUATEMALA', 'HONDURAS', 'EL SALVADOR', 'NICARAGUA', 'COSTA RICA']
        if pais in founders: return 'Regional'
        if pais == 'REGIONAL': return 'Multi-country'
        return 'Extra-regional'

    if group_col in df_agg.columns:
        df_agg['Tipo_Pais'] = df_agg[group_col].apply(categorize_pais)

    # 4. Business Logic Bands (Frozen Breaks)
    # Using min, median, p95 as requested by business logic
    m_series = df_agg['Monto_Aprobado'][df_agg['Monto_Aprobado'] > 0]
    if not m_series.empty:
        q_med = m_series.median()
        q_p95 = m_series.quantile(0.95)
        
        frozen_bins = [0, q_med, q_p95, float('inf')]
        frozen_labels = ['Menores', 'Regulares', 'Estratégicos']

        df_agg['Monto_Banda'] = pd.cut(
            df_agg['Monto_Aprobado'],
            bins=frozen_bins,
            labels=frozen_labels,
            include_lowest=True,
            right=False 
        ).astype(str)
    
    # 5. Frequency Bands
    def categorize_freq(x: int) -> str:
        if x == 1: return 'Ocasional'
        elif x <= 3: return 'Baja'
        elif x <= 6: return 'Media'
        else: return 'Alta'
    
    df_agg['Frecuencia_Banda'] = df_agg['CANTIDAD_APROBACIONES'].apply(categorize_freq)

    # 6. Strategic Quadrant
    median_monto = df_agg['Monto_Aprobado'].median()
    median_freq = df_agg['CANTIDAD_APROBACIONES'].median()

    def get_quadrant(row):
        high_monto = row['Monto_Aprobado'] >= median_monto
        high_freq = row['CANTIDAD_APROBACIONES'] >= median_freq
        
        if high_monto and high_freq: return 'Core Strategic'
        if high_monto and not high_freq: return 'Big Deals'
        if not high_monto and high_freq: return 'Operativo'
        return 'Oportunidad'

    df_agg['Cuadrante_Estrategia'] = df_agg.apply(get_quadrant, axis=1)

    return df_agg

def load_data(df: pd.DataFrame, config: Dict[str, Any]) -> None:
    """
    Saves the processed dataframe to disk.

    Args:
        df: Processed DataFrame.
        config: Configuration dict.
    """
    processed_path = Path(config['data']['processed_path'])
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)
    logger.info(f"ETL Completed. Processed data saved to: {processed_path}")

def run_etl(config_path: str = "config/local.yaml"):
    """Orchestrates the ETL pipeline."""
    try:
        config = load_config(config_path)
        
        df_raw = extract_data(config)
        df_clean = clean_data(df_raw, config)
        df_final = feature_engineering(df_clean, config)
        load_data(df_final, config)
    
    except Exception as e:
        logger.error(f"ETL Pipeline Failed: {e}")
        raise

if __name__ == "__main__":
    run_etl()
