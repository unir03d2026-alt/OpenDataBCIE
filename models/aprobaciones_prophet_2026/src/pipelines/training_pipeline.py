import pandas as pd
from prophet import Prophet
from joblib import Parallel, delayed
import yaml
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def train_country_model(group_name, df_group, periods, freq):
    try:
        # 1. Preparar datos y Agrupar ANUALMENTE ('YS')
        df_prophet = df_group.rename(columns={'Fecha_Aprobacion': 'ds', 'Monto_Aprobado': 'y'})
        df_prophet = df_prophet.groupby(pd.Grouper(key='ds', freq='YS'))['y'].sum().reset_index()

        if len(df_prophet) < 2: return pd.DataFrame()

        # 2. Detectar la ULTIMA FECHA REAL (Ej: 2025-01-01)
        last_real_date = df_prophet['ds'].max()

        # 3. Entrenar
        m = Prophet(seasonality_mode='multiplicative', yearly_seasonality=False)
        m.fit(df_prophet)
        
        # 4. Predecir Futuro
        future = m.make_future_dataframe(periods=periods, freq='YS')
        forecast = m.predict(future)
        
        # 5. FILTRO CRITICO: Solo guardar fechas ESTRICTAMENTE MAYORES a la ultima real
        # Esto elimina 2025 si ya existia en real. Empieza en 2026.
        forecast_future = forecast[forecast['ds'] > last_real_date].copy()
        
        res = forecast_future[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        res['Pais'] = group_name
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
    
    logging.info(f"Entrenando modelos para {len(paises)} paises (Frecuencia Anual)...")

    resultados = Parallel(n_jobs=-1, backend="threading")(
        delayed(train_country_model)(pais, df[df['Pais'] == pais], horizonte, 'YS') for pais in paises
    )
    
    if resultados:
        final_df = pd.concat(resultados, ignore_index=True)
        output_path = "data/04-predictions/predicciones_bcie.csv"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        final_df.to_csv(output_path, index=False)
        logging.info("Predicciones futuras guardadas correctamente.")

if __name__ == "__main__":
    run_training("config/local.yaml")