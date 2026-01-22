import sys
import os
import traceback

# Mensaje inicial de ejecución
print("Iniciando ejecución del script principal (Modelo TimesFM)...")

# Ajuste de rutas para encontrar la carpeta src independientemente de donde se ejecute
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

try:
    from src.pipelines.etl_pipeline import run_etl
    from src.pipelines.inference_pipeline import run_forecasting
    from src.pipelines.evaluation_pipeline import run_evaluation
    from src.pipelines.visualization_pipeline import generate_plots
    
    print("Las librerías y módulos necesarios se han importado correctamente.")
except ImportError as e:
    print(f"Error crítico: No fue posible importar los módulos requeridos. Detalles: {e}")
    sys.exit(1)

def main():
    """
    Función principal que orquesta la ejecución secuencial de los pipelines:
    1. ETL: Extracción y transformación de datos.
    2. Evaluación: Validación histórica del modelo.
    3. Inferencia: Generación de proyecciones futuras.
    4. Visualización: Creación de reportes y gráficos.
    """
    config_path = os.path.join(BASE_DIR, "config", "local.yaml")

    if not os.path.exists(config_path):
        print(f"Error: El archivo de configuración no se encuentra en la ruta esperada: {config_path}")
        return

    # Etapa 1: Extracción y Transformación (ETL)
    print("\n--- Etapa 1: Proceso ETL (Extracción, Transformación y Carga) ---")
    try:
        run_etl(config_path)
    except Exception as e:
        print(f"La etapa de ETL ha fallado: {e}")
        return

    # Etapa 2: Evaluación y Backtesting
    print("\n--- Etapa 2: Evaluación del Modelo (Backtesting y Validación) ---")
    try:
        run_evaluation(config_path)
    except Exception as e:
        print(f"Advertencia: Se produjo un error durante la evaluación: {e}")
        # El proceso continúa, ya que la evaluación no bloquea la generación de pronósticos,
        # aunque es recomendable revisar los logs.
        traceback.print_exc()

    # Etapa 3: Generación de Pronósticos
    print("\n--- Etapa 3: Ejecución de Pronósticos con TimesFM ---")
    try:
        run_forecasting(config_path)
    except Exception as e:
        print(f"Error: No se pudieron generar los pronósticos: {e}")
        traceback.print_exc()
        return

    # Etapa 4: Visualización y Reportes
    print("\n--- Etapa 4: Generación de Reportes y Visualizaciones ---")
    try:
        generate_plots(config_path)
    except Exception as e:
        print(f"Error: Falló la generación de los gráficos finales: {e}")
        traceback.print_exc()

    print("\nEl proceso ha finalizado exitosamente.")

if __name__ == "__main__":
    main()
