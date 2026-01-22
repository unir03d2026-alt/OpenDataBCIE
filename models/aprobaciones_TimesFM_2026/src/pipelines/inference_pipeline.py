"""
Pipeline de Inferencia y Pronóstico

Este módulo es responsable de cargar los datos históricos procesados, agruparlos por país y año,
y utilizar el modelo TimesFM de Google (mediante Hugging Face Transformers) para proyectar
valores futuros. Además, calcula intervalos de confianza basados en la variabilidad histórica.
"""

import pandas as pd
import numpy as np
import yaml
import torch
from transformers import AutoModel, AutoConfig
import os
from datetime import datetime
import logging
import traceback

# Configuración del registro de eventos (logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_residual_stats(config):
    """
    Carga las estadísticas de los residuales calculadas previamente en la etapa de evaluación.
    Estas métricas son fundamentales para establecer intervalos de confianza realistas.
    """
    evaluation_path = config.get('paths', {}).get('evaluation_path', "data/05-evaluation")
    stats_path = os.path.join(evaluation_path, "residual_stats.csv")
    
    if os.path.exists(stats_path):
        stats_df = pd.read_csv(stats_path)
        # Crear mapa de desviación estándar por país
        residual_dict = dict(zip(stats_df['País'], stats_df['Residual_Std']))
        logger.info(f"Se han cargado estadísticas de variabilidad para {len(residual_dict)} países.")
        return residual_dict
    else:
        logger.warning(f"No se encontró el archivo de estadísticas en {stats_path}. Se utilizará un método de estimación alternativo.")
        return None


def calculate_confidence_intervals(predictions, country, residual_stats, confidence_level=0.95):
    """
    Genera los intervalos de confianza para las predicciones.
    
    Metodología:
    1. Si existen datos históricos de error (residuales), se utiliza su desviación estándar.
    2. Si no existen, se aplica una estimación conservadora basada en un porcentaje de la predicción.
    
    Args:
        predictions: Array con los valores pronosticados.
        country: Identificador del país.
        residual_stats: Diccionario con la desviación estándar de los residuales por país.
        confidence_level: Nivel de confianza deseado (por defecto 95%).
    
    Returns:
        lower_bounds, upper_bounds: Límites inferior y superior del intervalo.
    """
    # Valor Z para el nivel de confianza (1.96 para 95%)
    z_score = 1.96 if confidence_level == 0.95 else 1.645
    
    if residual_stats and country in residual_stats:
        # Método principal: Basado en la historia de errores del modelo para este país
        std_residual = residual_stats[country]
        
        # Validación para evitar desviaciones nulas o inválidas
        if pd.isna(std_residual) or std_residual < 1e-6:
            std_residual = np.std(predictions) * 0.2  # Estimación de respaldo
            
        lower_bounds = predictions - (z_score * std_residual)
        upper_bounds = predictions + (z_score * std_residual)
        
        logger.debug(f"  {country}: Intervalos basados en desviación histórica (std={std_residual:,.0f})")
        
    else:
        # Método de respaldo: Estimación proporcional
        # Se asume un coeficiente de variación del 15%
        cv = 0.15
        std_estimated = np.abs(predictions) * cv
        
        lower_bounds = predictions - (z_score * std_estimated)
        upper_bounds = predictions + (z_score * std_estimated)
        
        logger.debug(f"  {country}: Intervalos estimados por proporción (CV={cv})")
    
    # Ajuste: Los montos financieros no pueden ser negativos
    lower_bounds = np.maximum(lower_bounds, 0)
    
    return lower_bounds, upper_bounds


def run_forecasting(config_path):
    try:
        logger.info("Iniciando proceso de proyección con modelo TimesFM...")
        config = load_config(config_path)
        
        # Cargar estadísticas para intervalos de confianza
        residual_stats = load_residual_stats(config)
        
        # 1. Carga de Datos Procesados
        processed_path = config['data']['processed_path']
        if not os.path.exists(processed_path):
            raise FileNotFoundError(f"No se encuentra el archivo de datos procesados: {processed_path}")
            
        df = pd.read_csv(processed_path)
        logger.info(f"Datos cargados correctamente: {len(df)} registros.")
        
        # 2. Preprocesamiento para Series Temporales
        date_col = config['data']['date_col']
        value_col = config['data']['value_col']
        group_col = config['data']['group_col']
        
        # Validación y conversión de fechas
        df[date_col] = pd.to_datetime(df[date_col])
        df['Año'] = df[date_col].dt.year
        
        # Agrupación anual por país
        df_grouped = df.groupby([group_col, 'Año'])[value_col].sum().reset_index()
        
        # Identificación de series únicas
        countries = df_grouped[group_col].unique()
        logger.info(f"Se generarán proyecciones para {len(countries)} países.")

        # 3. Inicialización del Modelo TimesFM
        repo_id = "google/timesfm-2.0-500m-pytorch"
        horizon_years = config['model'].get('horizon_years', 5)
        
        logger.info(f"Cargando arquitectura del modelo: {repo_id}...")
        
        # Configuración de hardware (GPU/CPU)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Dispositivo de procesamiento seleccionado: {device}")

        # Importación dinámica del modelo
        try:
            from transformers.models.timesfm.modeling_timesfm import TimesFmModelForPrediction
        except ImportError:
            logger.warning("Importación específica fallida, intentando carga genérica con AutoModel...")
            from transformers import AutoModelForTimeSeriesForecasting as TimesFmModelForPrediction
            
        model = TimesFmModelForPrediction.from_pretrained(
            repo_id, 
            trust_remote_code=True,
            device_map=device
        )
        
        # 4. Generación de Pronósticos
        logger.info("Ejecutando inferencia por país...")
        
        all_forecasts = []
        
        for country in countries:
            try:
                # Filtrar y ordenar datos históricos del país
                country_data = df_grouped[df_grouped[group_col] == country].sort_values('Año')
                
                history_values = country_data[value_col].values
                
                # Preparación del tensor de entrada
                input_tensor = torch.tensor(history_values, dtype=torch.float32).unsqueeze(0).to(device)
                freq_tensor = torch.tensor([0]).to(device) 

                with torch.no_grad():
                    outputs = model(
                        past_values=input_tensor, 
                        freq=freq_tensor
                    )
                    forecast = outputs.mean_predictions
                    
                # Procesamiento de la salida
                forecast_values = forecast.cpu().numpy().squeeze()
                
                # Ajuste de longitud del horizonte
                if len(forecast_values) > horizon_years:
                     forecast_values = forecast_values[-horizon_years:]
                
                # Generación de fechas futuras
                last_year = country_data['Año'].max()
                future_years = [last_year + i + 1 for i in range(len(forecast_values))]
                
                # Cálculo de intervalos de confianza
                lower_bounds, upper_bounds = calculate_confidence_intervals(
                    forecast_values, 
                    country, 
                    residual_stats,
                    confidence_level=0.95
                )
                
                # Estructuración de resultados
                temp_df = pd.DataFrame({
                    'unique_id': country, 
                    'ds': [datetime(y, 1, 1) for y in future_years],
                    'yhat': forecast_values,
                    'yhat_lower': lower_bounds,
                    'yhat_upper': upper_bounds
                })
                
                all_forecasts.append(temp_df)
                
            except Exception as e_country:
                logger.warning(f"No se pudo completar la proyección para {country}. Error: {e_country}")
                continue
                
        if not all_forecasts:
            raise ValueError("El proceso finalizó sin generar pronósticos válidos para ningún país.")
            
        forecast_df = pd.concat(all_forecasts, ignore_index=True)
        
        # 5. Exportación de Resultados
        forecast_df = forecast_df.rename(columns={'unique_id': 'País'})
        
        output_dir = config.get('paths', {}).get('predictions_path', "data/04-predictions")
        output_path = os.path.join(output_dir, "predicciones_bcie.csv") 
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        forecast_df.to_csv(output_path, index=False)
        logger.info(f"Proyecciones guardadas exitosamente en: {output_path}")
        
        # Resumen final sobre la metodología de intervalos
        if residual_stats:
            logger.info("Nota: Los intervalos de confianza se calcularon utilizando la variabilidad histórica real.")
        else:
            logger.info("Nota: Los intervalos de confianza se estimaron utilizando un método proporcional estándar.")
        
    except Exception as e:
        logger.error(f"Error crítico en el pipeline de inferencia: {str(e)}")
        logger.error(traceback.format_exc())
        raise e

if __name__ == "__main__":
    run_forecasting("config/local.yaml")


