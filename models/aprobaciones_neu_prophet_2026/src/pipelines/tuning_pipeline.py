import pandas as pd
import yaml
import logging
import itertools
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from joblib import Parallel, delayed
from src.pipelines.feature_eng_pipeline import load_and_prep_data

# Configurar logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def evaluate_params(params, df, horizon_str):
    """
    Entrena un modelo con UN set de parámetros y calcula el error (RMSE).
    """
    try:
        model = Prophet(
            seasonality_mode=params['seasonality_mode'],
            changepoint_prior_scale=params['changepoint_prior_scale'],
            yearly_seasonality=params['yearly_seasonality'],
            weekly_seasonality=False,
            daily_seasonality=False
        )
        
        model.fit(df)
        
        # Cross Validation integrado de Prophet
        # initial: Con cuánto entrena antes de validar (ej. 730 days = 2 años)
        # period: Cada cuánto hace el corte (ej. 180 days = 6 meses)
        # horizon: Cuánto predice en la prueba (ej. 365 days = 1 año)
        df_cv = cross_validation(
            model, 
            initial='730 days', 
            period='180 days', 
            horizon=horizon_str, 
            parallel="processes",  # Prophet ya tiene paralelización interna para CV
            disable_tqdm=True
        )
        
        df_p = performance_metrics(df_cv, rolling_window=1)
        rmse = df_p['rmse'].values[0]
        
        return {'params': params, 'rmse': rmse, 'status': 'OK'}
        
    except Exception as e:
        return {'params': params, 'rmse': float('inf'), 'status': str(e)}

def run_tuning(config_path):
    # 1. Cargar Configuración y Datos
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    df_all = load_and_prep_data(config)
    
    # IMPORTANTE: Para optimizar, no usamos TODOS los grupos (países) porque tardaría días.
    # Estrategia: Agrupamos todo en un "Total Global" para encontrar los hiperparámetros generales.
    logging.info("Agrupando datos para encontrar hiperparámetros globales...")
    df_tuning = df_all.groupby('ds')['y'].sum().reset_index()
    
    # 2. Definir la Rejilla de Búsqueda (Grid Search)
    # Aquí pones las opciones que quieres probar.
    param_grid = {
        'changepoint_prior_scale': [0.01, 0.05, 0.1, 0.5], # Flexibilidad de la tendencia
        'seasonality_mode': ['additive', 'multiplicative'], # ¿El error crece con el monto?
        'yearly_seasonality': [True, False]
    }

    # Generar todas las combinaciones posibles
    all_params = [dict(zip(param_grid.keys(), v)) for v in itertools.product(*param_grid.values())]
    
    logging.info(f"--- Iniciando Optimización ---")
    logging.info(f"Total de combinaciones a probar: {len(all_params)}")
    
    horizon_days = f"{config['forecast']['horizon_years'] * 365} days"

    # 3. Ejecución Paralela de Combinaciones
    # Usamos joblib para probar varias configuraciones a la vez
    results = Parallel(n_jobs=config['system']['n_jobs'])(
        delayed(evaluate_params)(p, df_tuning, horizon_days) for p in all_params
    )
    
    # 4. Encontrar el mejor resultado
    results_df = pd.DataFrame(results)
    best_result = results_df.sort_values('rmse').iloc[0]
    
    logging.info("\n" + "="*30)
    logging.info(f"🏆 MEJORES PARÁMETROS ENCONTRADOS (RMSE: {best_result['rmse']:.2f})")
    logging.info(f"{best_result['params']}")
    logging.info("="*30)
    
    # 5. Guardar recomendación en un archivo
    with open("best_params_recommendation.txt", "w") as f:
        f.write(f"RMSE: {best_result['rmse']}\n")
        f.write(yaml.dump(best_result['params']))
        
    logging.info("✅ Recomendación guardada en 'best_params_recommendation.txt'. Copia estos valores a tu config/local.yaml")