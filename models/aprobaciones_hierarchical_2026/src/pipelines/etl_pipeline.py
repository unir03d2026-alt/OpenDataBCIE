"""
ETL Pipeline Module.

This module handles the Extraction, Transformation, and Loading (ETL) of data from the BCIE CKAN API.
It performs the following steps:
1. Connects to the API endpoint configured in local.yaml.
2. Extracts raw records.
3. Cleans and transforms the dataset (renaming columns, converting types, filtering valid records).
4. Saves both raw and processed datasets to the local filesystem.
"""

import logging
import requests
import pandas as pd
import yaml
import json
from pathlib import Path
from datetime import datetime

# Configure module-level logger
logger = logging.getLogger(__name__)

def run_etl(config_path, run_id=None):
    """
    Executes the ETL process based on the provided configuration file.

    Args:
        config_path (str): Path to the YAML configuration file.
        run_id (str): Optional Run ID for traceability (not currently used in ETL but passed by orchestrator).
    
    Raises:
        Exception: If API connection fails or critical columns are missing.
    """
    # Load configuration
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    processed_path = Path(config['data']['processed_path'])

    # --- EXTRACTION WITH PAGINATION ---
    url = config['api']['base_url']
    resource_id = config['api']['resource_id']
    limit = config['api'].get('limit', 5000)  # Default to 5000 per page

    logger.info("Connecting to BCIE CKAN API...")
    
    try:
        all_records = []
        offset = 0
        page = 1
        
        while True:
            params = {
                'resource_id': resource_id, 
                'limit': limit,
                'offset': offset
            }
            
            logger.info(f"Fetching page {page} (offset={offset}, limit={limit})...")
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data_json = response.json()
            if not data_json['success']:
                raise Exception(f"API Error on page {page}: Query failed.")
                
            records = data_json['result']['records']
            
            if not records:
                logger.info(f"No more records returned. Pagination complete.")
                break
                
            all_records.extend(records)
            logger.info(f"Page {page}: retrieved {len(records)} records (total so far: {len(all_records)})")
            
            # Stop if fewer records than limit (last page)
            if len(records) < limit:
                logger.info(f"Received {len(records)} < {limit}, stopping pagination.")
                break
                
            offset += limit
            page += 1
        
        df = pd.DataFrame(all_records)
        logger.info(f"Download complete: {len(df)} total records retrieved across {page} pages.")

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

    # --- DATA QUALITY TRACKING ---
    total_downloaded = len(all_records)
    valid_records = len(df)
    
    data_quality = {
        "timestamp": datetime.now().isoformat(),
        "total_records_downloaded": total_downloaded,
        "valid_records": valid_records,
        "filtered_records": total_downloaded - valid_records,
        "date_range": {
            "min_year": int(df['Anio'].min()) if len(df) > 0 else None,
            "max_year": int(df['Anio'].max()) if len(df) > 0 else None
        },
        "top_countries": df[group_col].value_counts().head(10).to_dict() if len(df) > 0 else {},
        "sector_distribution": df['Sector_Economico'].value_counts().to_dict() if 'Sector_Economico' in df.columns else {}
    }
    
    # Save DQ
    dq_path = processed_path.parent / "data_quality.json"
    with open(dq_path, 'w', encoding='utf-8') as f:
        json.dump(data_quality, f, indent=2)
    logger.info(f"Data quality report saved to: {dq_path}")
    
    # --- RUN METADATA ---
    run_meta = {
        "timestamp": datetime.now().isoformat(),
        "run_id": run_id,
        "resource_id": resource_id,
        "total_records": total_downloaded,
        "valid_records": valid_records,
        "config_snapshot": config
    }
    
    meta_path = processed_path.parent / "run_meta.json"
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(run_meta, f, indent=2)
    logger.info(f"Run metadata saved to: {meta_path}")

    # --- LOADING ---
    # processed_path already defined at top
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)
    
    logger.info(f"ETL Completed. Processed data saved to: {processed_path}")

if __name__ == "__main__":
    # For standalone testing
    run_etl("config/local.yaml")
