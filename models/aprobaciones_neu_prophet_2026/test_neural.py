import pandas as pd
from neuralprophet import NeuralProphet, set_log_level
import logging
import time

# Configuracion basica logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
set_log_level("ERROR")

def test_single_country():
    data_path = "models/aprobaciones_neu_prophet_2026/data/02-preprocessed/aprobaciones_limpias.csv"
    
    logging.info(f"Cargando datos de: {data_path}")
    try:
        df = pd.read_csv(data_path)
        df['Fecha_Aprobacion'] = pd.to_datetime(df['Fecha_Aprobacion'])
    except Exception as e:
        logging.error(f"Error cargando datos: {e}")
        return

    # Filtrar solo un pais para prueba (Costa Rica suele tener mas datos)
    pais = "COSTA RICA"
    df_pais = df[df['Pais'] == pais].copy()
    
    if df_pais.empty:
        logging.error(f"No hay datos para {pais}")
        return
        
    logging.info(f"Datos cargados para {pais}: {len(df_pais)} registros.")

    # 1. Preparar datos
    df_prophet = df_pais.rename(columns={'Fecha_Aprobacion': 'ds', 'Monto_Aprobado': 'y'})
    df_prophet = df_prophet.groupby(pd.Grouper(key='ds', freq='YS'))['y'].sum().reset_index()
    
    logging.info(f"Datos agrupados (anual): {len(df_prophet)} registros.")
    print(df_prophet.tail())

    # 2. Configurar Modelo (Version Ligera)
    logging.info("Inicializando NeuralProphet...")
    # Reducimos epochs y learning rate para prueba
    m = NeuralProphet(
        quantiles=[0.1, 0.9],
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        epochs=100, # Limitamos epochs para velocidad
        learning_rate=0.01
    )
    
    # 3. Entrenar
    start_time = time.time()
    logging.info("Iniciando entrenamiento...")
    print("DEBUG: Calling m.fit()", flush=True)
    try:
        metrics = m.fit(df_prophet, freq='YS') 
        print("DEBUG: m.fit() returned", flush=True)
        duration = time.time() - start_time
        logging.info(f"Entrenamiento completado en {duration:.2f} segundos.")
    except Exception as e:
        logging.error(f"FALLO EN ENTRENAMIENTO: {e}")
        return

    # 4. Predecir
    try:
        logging.info("Generando predicciones futuras...")
        print("DEBUG: Calling make_future_dataframe", flush=True)
        future = m.make_future_dataframe(df_prophet, periods=5)
        print("DEBUG: Calling predict", flush=True)
        forecast = m.predict(future)
        logging.info("Prediccion exitosa.")
        print("DEBUG: Prediction DONE", flush=True)
        print(forecast[['ds', 'yhat1', 'yhat1 10.0%', 'yhat1 90.0%']].tail())
    except Exception as e:
        logging.error(f"FALLO EN PREDICCION: {e}")

if __name__ == "__main__":
    test_single_country()
