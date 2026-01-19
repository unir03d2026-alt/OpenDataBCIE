"""
Módulo de Procesamiento de Datos

Este módulo actúa como el motor de cálculo. Se encarga de la ingesta,
limpieza, normalización y unificación de los datos históricos y predictivos.
"""

import pandas as pd
from datetime import datetime
from src.dashboard.config import SOCIO_MAP

def prepare_unified_data(df_hist, df_pred):
    """
    Unifica y normaliza los conjuntos de datos históricos y predictivos.

    Procesa los datos históricos reales y las predicciones del modelo,
    estandariza los nombres de columnas y valores, y combina ambos conjuntos
    en un único DataFrame estructurado para su visualización.

    Args:
        df_hist (pd.DataFrame): DataFrame con los datos históricos.
        df_pred (pd.DataFrame): DataFrame con las predicciones generadas.

    Returns:
        pd.DataFrame: DataFrame unificado y procesado con columnas estandarizadas.
    """
    hist = df_hist.copy()
    hist['Datos'] = 'Reales'
    hist['Predicción'] = 0
    hist['Inferior 80%'] = 0
    hist['Superior 80%'] = 0
    
    rename_hist = {
        'Fecha_Aprobacion': 'Fecha', 
        'Monto_Aprobado': 'Monto Total (USD)', 
        'Pais': 'País', 
        'Sector_Economico': 'Sector Institucional'
    }
    hist = hist.rename(columns={k: v for k, v in rename_hist.items() if k in hist.columns})
    
    pred = df_pred.copy()
    pred['Datos'] = 'Predicción'
    pred['Monto Total (USD)'] = 0
    
    rename_pred = {
        'ds': 'Fecha', 'yhat': 'Predicción', 
        'yhat_lower': 'Inferior 80%', 'yhat_upper': 'Superior 80%', 
        'Pais': 'País', 'País': 'País',
        'Sector': 'Sector Institucional', 'Tipo': 'Tipo de Socio'
    }
    pred = pred.rename(columns={k: v for k, v in rename_pred.items() if k in pred.columns})
    
    cols = ['Fecha', 'País', 'Sector Institucional', 'Tipo de Socio', 'Datos', 'Monto Total (USD)', 'Predicción', 'Inferior 80%', 'Superior 80%']
    
    for df in [hist, pred]:
        for c in cols:
            if c not in df.columns:
                if 'Sector' in c: df[c] = 'Proyección Global'
                elif 'Tipo' in c: df[c] = 'Otro'
                elif c in ['Monto Total (USD)', 'Predicción', 'Inferior 80%', 'Superior 80%']: df[c] = 0
                elif 'Datos' in c: df[c] = 'Predicción'
            
    df_unico = pd.concat([hist[cols], pred[cols]], ignore_index=True)
    
    df_unico['País_Upper'] = df_unico['País'].astype(str).str.upper().str.strip()
    df_unico['País_Upper'] = df_unico['País_Upper'].replace({
        'REPUBLICA DE CHINA (TAIWAN)': 'TAIWAN', 'REPUBLICA DE COREA': 'COREA', 'BELIZE': 'BELICE'
    })

    mask_missing = (df_unico['Tipo de Socio'] == 'Otro') | (df_unico['Tipo de Socio'].isnull())
    if mask_missing.any():
        df_unico.loc[mask_missing, 'Tipo de Socio'] = df_unico.loc[mask_missing, 'País_Upper'].map(SOCIO_MAP).fillna('Otro')
    
    df_unico['País'] = df_unico['País'].astype(str).str.title().str.strip()
    df_unico['País'] = df_unico['País'].replace({
        'Republica Dominicana': 'República Dominicana', 'Mexico': 'México', 'Panama': 'Panamá', 
        'Taiwan': 'Taiwán', 'Corea': 'Corea', 'Espana': 'España'
    })
    
    if 'Sector Institucional' in df_unico.columns:
        df_unico['Sector Institucional'] = df_unico['Sector Institucional'].astype(str).str.title().str.strip()
        df_unico['Sector Institucional'] = df_unico['Sector Institucional'].replace({
            'Publico': 'Sector Público', 'Sector Publico': 'Sector Público',
            'Privado': 'Sector Privado', 'Sector Privado': 'Sector Privado',
            'No Definido': 'No Definido'
        })

    df_unico['Fecha'] = pd.to_datetime(df_unico['Fecha'])
    df_unico['Año'] = df_unico['Fecha'].dt.year
    df_unico['Fecha_Str'] = df_unico['Fecha'].dt.strftime('%Y-%m-%d')
    
    return df_unico


def process_executive_data(df_raw):
    """
    Procesa los datos para el Dashboard Ejecutivo Histórico.
    Genera agregaciones por Año, Sector, País y Tipo.
    """
    df = df_raw.copy()
    
    # Renombrar columnas para estandarizar
    rename_cols = {
        'Fecha_Aprobacion': 'Fecha', 
        'Monto_Aprobado': 'Monto', 
        'Pais': 'País', 
        'Pais': 'País', 
        'Sector_Economico': 'Sector', 
        'Tipo_Socio': 'Tipo',
        'CANTIDAD_APROBACIONES': 'Cantidad'
    }
    df = df.rename(columns={k: v for k, v in rename_cols.items() if k in df.columns})
    
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df['Año'] = df['Fecha'].dt.year
    df = df.dropna(subset=['Año', 'Monto'])
    df['Año'] = df['Año'].astype(int)
    
    # 1. Agregación Anual
    if 'Cantidad' in df.columns:
        agg_year = df.groupby('Año')[['Monto', 'Cantidad']].sum().reset_index()
    else:
        agg_year = df.groupby('Año')['Monto'].agg(['sum', 'count']).reset_index()
        agg_year.columns = ['Año', 'Monto', 'Cantidad']
    agg_year = agg_year.sort_values('Año')
    agg_year['Promedio'] = agg_year['Monto'] / agg_year['Cantidad']
    agg_year['Var_YOY'] = agg_year['Monto'].pct_change() * 100
    agg_year['Var_YOY_Cant'] = agg_year['Cantidad'].pct_change() * 100
    
    # 2. Agregación Sector
    if 'Cantidad' in df.columns:
        agg_sector = df.groupby('Sector')[['Monto', 'Cantidad']].sum().reset_index().sort_values('Monto', ascending=False)
    else:
        agg_sector = df.groupby('Sector')['Monto'].agg(['sum', 'count']).reset_index()
        agg_sector.columns = ['Sector', 'Monto', 'Cantidad']
    
    # 3. Agregación Tipo Socio (Usando Mapa si es necesario)
    # 3. Agregación Tipo Socio
    if 'Tipo' not in df.columns:
        df['País_Upper'] = df['País'].astype(str).str.upper().str.strip()
        df['Tipo'] = df['País_Upper'].map(SOCIO_MAP).fillna('Otro')
        
    if 'Cantidad' in df.columns:
        agg_tipo = df.groupby('Tipo')[['Monto', 'Cantidad']].sum().reset_index().sort_values('Monto', ascending=True)
        agg_pais = df.groupby('País')[['Monto', 'Cantidad']].sum().reset_index().sort_values('Monto', ascending=False)
    else:
        agg_tipo = df.groupby('Tipo')['Monto'].agg(['sum', 'count']).reset_index()
        agg_tipo.columns = ['Tipo', 'Monto', 'Cantidad']
        agg_tipo = agg_tipo.sort_values('Monto', ascending=True)
        
        agg_pais = df.groupby('País')['Monto'].agg(['sum', 'count']).reset_index()
        agg_pais.columns = ['País', 'Monto', 'Cantidad']
        agg_pais = agg_pais.sort_values('Monto', ascending=False)
    
    # KPIs Globales
    kpis = {
        'total': df['Monto'].sum(),
        'count': int(df['Cantidad'].sum()) if 'Cantidad' in df.columns else len(df),
        'avg': df['Monto'].sum() / df['Cantidad'].sum() if 'Cantidad' in df.columns and df['Cantidad'].sum() > 0 else 0
    }
    
    return {
        'year': agg_year,
        'sector': agg_sector,
        'tipo': agg_tipo,
        'pais': agg_pais,
        'kpis': kpis,
        'raw': df[['Año', 'País', 'Sector', 'Monto', 'Tipo']]
    }
