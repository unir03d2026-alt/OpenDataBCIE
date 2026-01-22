import pandas as pd
from neuralprophet import NeuralProphet, set_log_level
import yaml
import logging
from pathlib import Path
import time
import warnings

# Suprimir logs y warnings
set_log_level("ERROR")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
warnings.filterwarnings("ignore", category=FutureWarning)

def train_country_model(group_name, df_group, periods, freq):
    try:
        # 1. Preparar datos y Agrupar ANUALMENTE ('YS')
        df_prophet = df_group.rename(columns={'Fecha_Aprobacion': 'ds', 'Monto_Aprobado': 'y'})
        df_prophet = df_prophet.groupby(pd.Grouper(key='ds', freq='YS'))['y'].sum().reset_index()

        if len(df_prophet) < 2: return pd.DataFrame()

        # 2. Detectar la ULTIMA FECHA REAL
        last_real_date = df_prophet['ds'].max()

        # 3. Entrenar NeuralProphet
        # Configuración optimizada basada en pruebas
        m = NeuralProphet(
            quantiles=[0.1, 0.9],
            yearly_seasonality=False,
            weekly_seasonality=False,
            daily_seasonality=False,
            epochs=100, # Optimizado para velocidad/rendimiento
            learning_rate=0.01
        )
        
        # Fit con barra de progreso desactivada para logs limpios
        metrics = m.fit(df_prophet, freq='YS', progress=None) # 'YS' es critico
        
        # 4. Predecir Futuro
        future = m.make_future_dataframe(df_prophet, periods=periods)
        forecast = m.predict(future)
        
        # 5. Mapeo de columnas NeuralProphet -> Formato Dashboard
        col_lower = 'yhat1 10.0%'
        col_upper = 'yhat1 90.0%'
        
        rename_map = {
            'yhat1': 'yhat',
            col_lower: 'yhat_lower',
            col_upper: 'yhat_upper'
        }
        
        forecast.rename(columns=rename_map, inplace=True)
        
        # 6. FILTRO CRITICO: Solo guardar fechas ESTRICTAMENTE MAYORES a la ultima real
        forecast_future = forecast[forecast['ds'] > last_real_date].copy()
        
        res = forecast_future[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        res['Pais'] = group_name
        
        logging.info(f"Modelo {group_name} completado.")
        return res

    except Exception as e:
        logging.error(f"Fallo en {group_name}: {e}")
        return pd.DataFrame()

def run_training(config_path):
    with open(config_path, 'r') as f: config = yaml.safe_load(f)
    data_path = config['data']['processed_path']
    if not Path(data_path).exists(): return

    df = pd.read_csv(data_path)
    df['Fecha_Aprobacion'] = pd.to_datetime(df['Fecha_Aprobacion'])

    # Parametros
    horizonte = config['model']['horizon_years']
    paises = df['Pais'].unique()
    
    logging.info(f"Entrenando modelos para {len(paises)} paises (NeuralProphet)...")

    # Ejecucion Secuencial
    resultados = []
    start_total = time.time()
    for pais in paises:
        res = train_country_model(pais, df[df['Pais'] == pais], horizonte, 'YS')
        resultados.append(res)
    
    duration_total = time.time() - start_total
    logging.info(f"Entrenamiento total completado en {duration_total:.2f} segundos.")

    if resultados:
        final_df = pd.concat(resultados, ignore_index=True)
        output_path = "data/04-predictions/predicciones_bcie.csv"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        final_df.to_csv(output_path, index=False)
        logging.info("Predicciones futuras guardadas correctamente (NeuralProphet).")

if __name__ == "__main__":
    run_training("config/local.yaml")