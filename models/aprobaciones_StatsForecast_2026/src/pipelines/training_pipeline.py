import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA, DynamicOptimizedTheta
from joblib import Parallel, delayed
import yaml
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def train_country_model(group_name, df_group, periods, freq):
    try:
        # 1. Preparar datos y Agrupar ANUALMENTE ('YS')
        # StatsForecast requiere columas: unique_id, ds, y
        df_sf = df_group.rename(columns={'Fecha_Aprobacion': 'ds', 'Monto_Aprobado': 'y'})
        df_sf = df_sf.groupby(pd.Grouper(key='ds', freq='YS'))['y'].sum().reset_index()
        
        # Agregar unique_id
        df_sf['unique_id'] = group_name

        if len(df_sf) < 2: return pd.DataFrame()

        # 2. Detectar la ULTIMA FECHA REAL
        last_real_date = df_sf['ds'].max()

        # 3. Definir e Instanciar StatsForecast con Multiples Modelos (Competencia/Ensemble)
        # 3. Definir e Instanciar StatsForecast con Multiples Modelos (Competencia/Ensemble)
        # AutoARIMA: Inercia / Corto Plazo
        # Theta: Excelente para capturar tendencias globales suavizadas (Comportamiento "Prophet-like")
        models = [
            AutoARIMA(season_length=1),
            DynamicOptimizedTheta(season_length=1) 
        ]
        
        sf = StatsForecast(
            models=models,
            freq='YS'
        )
        
        # 4. Ajustar y Predecir
        sf.fit(df_sf)
        # Nivel de confianza 80%
        forecast = sf.predict(h=periods, level=[80])
        forecast = forecast.reset_index()
        
        # LOGICA ENSEMBLE (PROMEDIO):
        
        # Prediccion Central (Promedio)
        forecast['yhat'] = (forecast['AutoARIMA'] + forecast['DynamicOptimizedTheta']) / 2
        
        # Intervalos de Confianza (Conservadores: Tomamos el rango mas amplio)
        forecast['yhat_lower'] = forecast[['AutoARIMA-lo-80', 'DynamicOptimizedTheta-lo-80']].min(axis=1)
        forecast['yhat_upper'] = forecast[['AutoARIMA-hi-80', 'DynamicOptimizedTheta-hi-80']].max(axis=1)
        
        # 5. FILTRO CRITICO: Solo guardar fechas ESTRICTAMENTE MAYORES a la ultima real
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
    # Ajuste de ruta si estamos ejecutando desde root del proyecto
    if not Path(data_path).exists(): return

    df = pd.read_csv(data_path)
    df['Fecha_Aprobacion'] = pd.to_datetime(df['Fecha_Aprobacion'])

    # Parametros
    horizonte = config['model']['horizon_years']
    paises = df['Pais'].unique()
    
    logging.info(f"Entrenando modelos para {len(paises)} paises (Ensemble AutoARIMA + Theta)...")

    # Paralelizacion
    # Nota: StatsForecast ya es eficiente, pero mantenemos paralelismo por paises si se desea
    # O podríamos pasar todo el DF a StatsForecast, pero para mantener logica existente:
    
    resultados = Parallel(n_jobs=-1, backend="threading")(
        delayed(train_country_model)(pais, df[df['Pais'] == pais], horizonte, 'YS') for pais in paises
    )
    
    if resultados:
        final_df = pd.concat(resultados, ignore_index=True)
        output_path = "data/04-predictions/predicciones_bcie.csv"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        final_df.to_csv(output_path, index=False)
        logging.info("Predicciones futuras guardadas correctamente (AutoARIMA).")

if __name__ == "__main__":
    run_training("config/local.yaml")