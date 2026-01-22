"""
Pipeline de Evaluación y Validación (Backtesting + Cross-Validation)

Este módulo se encarga de analizar la robustez y precisión del modelo TimesFM mediante dos estrategias:
1. Backtesting Histórico: Simula proyecciones en el pasado reciente para comparar con datos reales.
2. Validación Cruzada en Series Temporales (Time Series Cross-Validation): Evalúa el desempeño en múltiples ventanas de tiempo móviles.
"""

import pandas as pd
import numpy as np
import yaml
import torch
import os
from datetime import datetime
import logging
import traceback
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error, mean_absolute_error

# Configuración del registro de eventos (logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def time_series_cross_validation(country_data, model, device, value_col, n_splits=3, horizon=2):
    """
    Realiza una validación cruzada temporal (Rolling Window).
    
    Estrategia para n_splits=3 y horizon=2:
    - Iteración 1: Entrenar hasta 2018, Validar 2019-2020
    - Iteración 2: Entrenar hasta 2020, Validar 2021-2022
    - Iteración 3: Entrenar hasta 2022, Validar 2023-2024
    
    Returns:
        Lista de diccionarios con las métricas de error (MAPE, RMSE, MAE) por cada iteración.
    """
    years = sorted(country_data['Año'].unique())
    n_years = len(years)
    
    # Requerimiento mínimo: Datos suficientes para entrenar y validar todas las divisiones
    min_train_size = 5
    required_years = min_train_size + (n_splits * horizon)
    
    if n_years < required_years:
        return None  # La serie temporal es demasiado corta para esta validación
    
    fold_metrics = []
    
    for fold in range(n_splits):
        # Definición de índices para dividir Train/Test en esta iteración
        # Se calcula de atrás hacia adelante para priorizar los datos más recientes
        test_end_idx = n_years - (fold * horizon)
        test_start_idx = test_end_idx - horizon
        train_end_idx = test_start_idx
        
        if train_end_idx < min_train_size:
            continue  # Datos de entrenamiento insuficientes para este pliegue
            
        test_years = years[test_start_idx:test_end_idx]
        train_years = years[:train_end_idx]
        
        if len(test_years) == 0 or len(train_years) < min_train_size:
            continue
        
        # Segmentación de datos
        train_data = country_data[country_data['Año'].isin(train_years)]
        test_data = country_data[country_data['Año'].isin(test_years)]
        
        # Preparación de Tensores
        history_values = train_data[value_col].values
        input_tensor = torch.tensor(history_values, dtype=torch.float32).unsqueeze(0).to(device)
        freq_tensor = torch.tensor([0]).to(device)
        
        try:
            with torch.no_grad():
                outputs = model(past_values=input_tensor, freq=freq_tensor)
                forecast = outputs.mean_predictions
                
            forecast_values = forecast.cpu().numpy().squeeze()
            
            # Ajuste de longitud y comparación
            pred_len = len(test_data)
            if len(forecast_values) < pred_len:
                continue
                
            y_pred = forecast_values[:pred_len]
            y_true = test_data[value_col].values
            
            # Cálculo de Métricas de Error
            mape = mean_absolute_percentage_error(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mae = mean_absolute_error(y_true, y_pred)
            
            fold_metrics.append({
                'fold': fold + 1,
                'train_years': f"{min(train_years)}-{max(train_years)}",
                'test_years': f"{min(test_years)}-{max(test_years)}",
                'MAPE': mape,
                'RMSE': rmse,
                'MAE': mae
            })
            
        except Exception as e:
            logger.warning(f"Excepción en Cross-Validation (Pliegue {fold+1}): {e}")
            continue
            
    return fold_metrics if fold_metrics else None


def run_evaluation(config_path):
    try:
        logger.info("=" * 60)
        logger.info("INICIO DE PROTOCOLO DE EVALUACIÓN (Backtesting + Cross-Validation)")
        logger.info("=" * 60)
        config = load_config(config_path)
        
        # 1. Carga de Datos Procesados
        processed_path = config['data']['processed_path']
        if not os.path.exists(processed_path):
            raise FileNotFoundError(f"No se encontró el archivo fuente: {processed_path}")
            
        df = pd.read_csv(processed_path)
        
        # Estandarización de Fechas
        date_col = config['data']['date_col']
        value_col = config['data']['value_col']
        group_col = config['data']['group_col']
        
        df[date_col] = pd.to_datetime(df[date_col])
        df['Año'] = df[date_col].dt.year
        
        # Agrupación por País y Año
        df_grouped = df.groupby([group_col, 'Año'])[value_col].sum().reset_index()
        
        # 2. Configuración de Parámetros de Evaluación
        horizon = config['model'].get('horizon_years', 5)
        max_year = df_grouped['Año'].max()
        cutoff_year = max_year - horizon
        
        logger.info(f"Último año registrado: {max_year}")
        logger.info(f"Horizonte de predicción definido: {horizon} años")
        
        # 3. Inicialización del Modelo
        repo_id = "google/timesfm-2.0-500m-pytorch"
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Cargando modelo {repo_id}. Dispositivo en uso: {device}")
        
        try:
            from transformers.models.timesfm.modeling_timesfm import TimesFmModelForPrediction
        except ImportError:
            from transformers import AutoModelForTimeSeriesForecasting as TimesFmModelForPrediction
            
        model = TimesFmModelForPrediction.from_pretrained(repo_id, trust_remote_code=True, device_map=device)
        
        countries = df_grouped[group_col].unique()
        
        # ========================================
        # FASE A: BACKTESTING SIMPLE
        # ========================================
        logger.info("\n" + "-" * 50)
        logger.info("FASE A: BACKTESTING HISTÓRICO")
        logger.info(f"Entrenamiento: Hasta {cutoff_year} | Prueba: {cutoff_year + 1} - {max_year}")
        logger.info("-" * 50)
        
        metrics = []
        all_results = []
        
        for country in countries:
            country_data = df_grouped[df_grouped[group_col] == country].sort_values('Año')
            
            # División de datos (Train/Test)
            train = country_data[country_data['Año'] <= cutoff_year]
            test = country_data[country_data['Año'] > cutoff_year]
            
            if len(test) == 0 or len(train) == 0:
                continue
                
            history_values = train[value_col].values
            input_tensor = torch.tensor(history_values, dtype=torch.float32).unsqueeze(0).to(device)
            freq_tensor = torch.tensor([0]).to(device)
            
            with torch.no_grad():
                outputs = model(past_values=input_tensor, freq=freq_tensor)
                forecast = outputs.mean_predictions
                
            forecast_values = forecast.cpu().numpy().squeeze()
            
            pred_len = len(test)
            if len(forecast_values) < pred_len:
                continue
                
            y_pred = forecast_values[:pred_len]
            y_true = test[value_col].values
            
            # Registro detallado de resultados (incluyendo análisis de residuales)
            for i in range(pred_len):
                residual = y_pred[i] - y_true[i]
                all_results.append({
                    'País': country,
                    'Año': test.iloc[i]['Año'],
                    'Real': y_true[i],
                    'Predicho': y_pred[i],
                    'Residual': residual,
                    'Residual_Abs': abs(residual)
                })

            try:
                mape = mean_absolute_percentage_error(y_true, y_pred)
                rmse = np.sqrt(mean_squared_error(y_true, y_pred))
                mae = mean_absolute_error(y_true, y_pred)
                metrics.append({
                    'País': country, 
                    'MAPE': mape, 
                    'RMSE': rmse, 
                    'MAE': mae
                })
            except Exception:
                pass
        
        # Exportación de resultados de Backtesting
        results_df = pd.DataFrame(all_results)
        
        evaluation_path = config.get('paths', {}).get('evaluation_path', "data/05-evaluation")
        output_path = os.path.join(evaluation_path, "backtesting_results.csv")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        results_df.to_csv(output_path, index=False)
        
        # Cálculo de estadísticas de residuales (esencial para intervalos de confianza)
        if len(results_df) > 0:
            residual_stats = results_df.groupby('País')['Residual'].agg(['mean', 'std']).reset_index()
            residual_stats.columns = ['País', 'Residual_Mean', 'Residual_Std']
            residual_stats.to_csv(os.path.join(evaluation_path, "residual_stats.csv"), index=False)
            logger.info("Estadísticas de residuales calculadas y almacenadas.")
        
        # Resumen de métricas de Backtesting
        if metrics:
            metrics_df = pd.DataFrame(metrics)
            avg_mape = metrics_df['MAPE'].mean()
            avg_rmse = metrics_df['RMSE'].mean()
            
            logger.info(f"MAPE Promedio Global: {avg_mape:.2%}")
            logger.info(f"RMSE Promedio Global: {avg_rmse:,.2f}")
        
        # ========================================
        # FASE B: VALIDACIÓN CRUZADA (CROSS-VALIDATION)
        # ========================================
        logger.info("\n" + "-" * 50)
        logger.info("FASE B: VALIDACIÓN CRUZADA DE SERIES TEMPORALES")
        logger.info("Configuración: 3 iteraciones de ventana móvil (Horizonte de 2 años)")
        logger.info("-" * 50)
        
        cv_results = []
        cv_summary = []
        
        for country in countries:
            country_data = df_grouped[df_grouped[group_col] == country].sort_values('Año')
            
            fold_metrics = time_series_cross_validation(
                country_data, model, device, value_col,
                n_splits=3, horizon=2
            )
            
            if fold_metrics:
                for fm in fold_metrics:
                    fm['País'] = country
                    cv_results.append(fm)
                
                # Agregación de resultados por país
                avg_mape_cv = np.mean([f['MAPE'] for f in fold_metrics])
                std_mape_cv = np.std([f['MAPE'] for f in fold_metrics])
                avg_rmse_cv = np.mean([f['RMSE'] for f in fold_metrics])
                
                cv_summary.append({
                    'País': country,
                    'MAPE_Mean': avg_mape_cv,
                    'MAPE_Std': std_mape_cv,
                    'RMSE_Mean': avg_rmse_cv,
                    'N_Folds': len(fold_metrics)
                })
        
        # Exportación de Resultados de Validacion Cruzada
        if cv_results:
            cv_results_df = pd.DataFrame(cv_results)
            cv_results_df.to_csv(os.path.join(evaluation_path, "cv_results_detail.csv"), index=False)
            
            cv_summary_df = pd.DataFrame(cv_summary)
            cv_summary_df.to_csv(os.path.join(evaluation_path, "cv_results_summary.csv"), index=False)
            
            # Reporte General de CV
            global_mape_cv = cv_summary_df['MAPE_Mean'].mean()
            global_mape_std = cv_summary_df['MAPE_Std'].mean()
            
            logger.info(f"MAPE Promedio en CV: {global_mape_cv:.2%} (Desviación: {global_mape_std:.2%})")
            logger.info(f"Países evaluados en CV: {len(cv_summary)}")
            
            # Ranking de desempeño
            cv_sorted = cv_summary_df.sort_values('MAPE_Mean')
            logger.info("\nTop 3 Países con Mejor Desempeño (Menor Error):")
            for _, row in cv_sorted.head(3).iterrows():
                logger.info(f"  {row['País']}: {row['MAPE_Mean']:.2%} (±{row['MAPE_Std']:.2%})")
        else:
            logger.warning("No fue posible realizar la validación cruzada (Insuficiencia de datos históricos).")
        
        # ========================================
        # CONCLUSIÓN FINAL
        # ========================================
        logger.info("\n" + "=" * 60)
        logger.info("CONCLUSIÓN DEL DIAGNÓSTICO DE ROBUSTEZ")
        logger.info("=" * 60)
        
        if metrics:
            # Ponderación de ambos métodos (Backtesting y CV)
            final_mape = avg_mape
            if cv_results:
                final_mape = (avg_mape + global_mape_cv) / 2
                
            robustness_status = "ROBUSTO" if final_mape < 0.3 else "REQUIERE REVISIÓN"
            logger.info(f"Error Porcentual Combinado (MAPE): {final_mape:.2%}")
            logger.info(f"DIAGNÓSTICO DEL MODELO: {robustness_status}")
            
            # Generación de informe ejecutivo
            summary_report = {
                'Fecha_Evaluacion': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'MAPE_Backtesting': avg_mape if metrics else None,
                'MAPE_CV': global_mape_cv if cv_results else None,
                'MAPE_Combinado': final_mape,
                'Estado': robustness_status
            }
            pd.DataFrame([summary_report]).to_csv(os.path.join(evaluation_path, "evaluation_summary.csv"), index=False)
            
        logger.info(f"Todos los resultados de la evaluación se han guardado en: {evaluation_path}")

    except Exception as e:
        logger.error(f"Se ha producido un error crítico durante la evaluación: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    run_evaluation("config/local.yaml")
