import sys
import os

# Mensaje de prueba inmediato
print("INICIANDO EJECUCION DEL SCRIPT...")

# Ajuste de rutas para encontrar la carpeta src
sys.path.append(os.getcwd())

try:
    from src.pipelines.etl_pipeline import run_etl
    from src.pipelines.training_pipeline import run_training
    # Dashboard de Predicciones (Prophet)
    from src.pipelines.visualization_pipeline import generate_plots
    # Dashboard Ejecutivo (Histórico) - NUEVO
    from src.pipelines.historical_pipeline import generate_historical_report
    
    print("Modulos importados correctamente.")
except ImportError as e:
    print(f"ERROR CRITICO: No se pudieron importar los modulos. {e}")
    sys.exit(1)

def main():
    config_path = "config/local.yaml"

    if not os.path.exists(config_path):
        print(f"ERROR: No se encuentra el archivo de configuracion en: {config_path}")
        return

    # Paso 1: ETL
    print("--- PASO 1: Extraccion y Transformacion (ETL) ---")
    try:
        run_etl(config_path)
    except Exception as e:
        print(f"FALLO EN ETL: {e}")
        return

    # Paso 2: Entrenamiento
    print("\n--- PASO 2: Entrenamiento del Modelo ---")
    try:
        run_training(config_path)
    except Exception as e:
        print(f"FALLO EN ENTRENAMIENTO: {e}")
        return

    # Paso 3: Visualizacion (Predicciones)
    print("\n--- PASO 3: Generacion Dashboard Predicciones (Prophet) ---")
    try:
        generate_plots(config_path)
    except Exception as e:
        print(f"FALLO EN GRAFICOS PREDICCION: {e}")
        # No detenemos el script para intentar generar el histórico

    # Paso 4: Visualizacion (Histórico)
    print("\n--- PASO 4: Generacion Dashboard Ejecutivo (Historico) ---")
    try:
        generate_historical_report(config_path)
    except Exception as e:
        print(f"FALLO EN GRAFICOS HISTORICOS: {e}")

    print("\nPROCESO COMPLETADO EXITOSAMENTE")

if __name__ == "__main__":
    main()