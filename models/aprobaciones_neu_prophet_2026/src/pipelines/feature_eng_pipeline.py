import pandas as pd
import yaml
import logging

def load_and_prep_data(config):
    """
    Carga, limpia y agrupa los datos para Prophet.
    """
    logging.info("Cargando y preparando datos...")
    
    # Cargar CSV
    df = pd.read_csv(config['data']['filepath'])
    
    # Convertir fechas
    df[config['data']['date_col']] = pd.to_datetime(df[config['data']['date_col']])
    
    # Filtrar fechas inválidas o futuras si es necesario
    # df = df[df[config['data']['date_col']] <= pd.Timestamp.now()]

    # Agrupar (Resampling Mensual 'MS' o Anual 'YE')
    # Ajustamos esto para sumar los montos por mes y por grupo (ej. Pais)
    df_grouped = df.groupby([
        config['data']['group_col'], 
        pd.Grouper(key=config['data']['date_col'], freq=config['forecast']['freq'])
    ])[config['data']['value_col']].sum().reset_index()
    
    # Renombrar columnas para Prophet
    df_prepared = df_grouped.rename(columns={
        config['data']['date_col']: 'ds',
        config['data']['value_col']: 'y',
        config['data']['group_col']: 'group_id'
    })
    
    logging.info(f"Datos preparados: {len(df_prepared)} filas para {df_prepared['group_id'].nunique()} grupos.")
    return df_prepared