# Modelo de Proyección de Aprobaciones (TimesFM)

Este proyecto implementa el modelo **TimesFM** de Google (vía Hugging Face Transformers) para realizar proyecciones financieras sobre las aprobaciones del BCIE.

## Requisitos del Sistema

Para ejecutar este modelo correctamente, necesitarás:
- **Python 3.9** o una versión superior.
- **Acceso a Internet**: Necesario para conectar con el API de Datos Abiertos del BCIE y para descargar los pesos del modelo desde Hugging Face la primera vez.
- **Hardware Recomendado**: Aunque el modelo puede correr en CPU, se recomienda disponer de una tarjeta gráfica NVIDIA con soporte CUDA para reducir significativamente los tiempos de procesamiento.

## Instrucciones de Instalación

1.  **Ubicación**: Abre tu terminal y navega hasta el directorio principal del modelo:
    ```bash
    cd models/aprobaciones_TimesFM_2026
    ```

2.  **Dependencias**: Instala todas las librerías necesarias ejecutando el siguiente comando:
    ```bash
    pip install -r requirements.txt
    ```
    *Nota: Si dispones de una GPU compatible, asegúrate de instalar la versión de `torch` habilitada para CUDA.*

## Guía de Ejecución

El proyecto cuenta con un script maestro que automatiza todo el flujo de trabajo, desde la obtención de datos hasta la generación de reportes. Para iniciarlo, ejecuta:

```bash
python run.py
```

### ¿Qué hace este script?
Al ejecutar el comando, se sucederán las siguientes etapas de forma automática:
1.  **ETL (Extracción, Transformación y Carga)**: Se conecta al portal de Datos Abiertos del BCIE y descarga la información histórica más reciente.
2.  **Evaluación de Robustez**: Realiza un "Backtesting", probando el modelo con datos pasados para evaluar su precisión y fiabilidad antes de proyectar a futuro.
3.  **Proyección**: Utiliza TimesFM para generar pronósticos a un horizonte de 5 años.
4.  **Reportes**: Genera gráficos y archivos HTML interactivos para analizar los resultados.

## Resultados y Salidas

Toda la información generada se organiza automáticamente en la carpeta `data/`:
- `data/04-predictions/predicciones_bcie.csv`: Contiene el archivo CSV con las proyecciones finales detalladas.
- `data/05-evaluation/`: Alberga los reportes técnicos sobre las métricas de precisión y desempeño del modelo.
- `data/05-reporting/`: Aquí encontrarás los dashboards interactivos en formato HTML.

## Personalización

Si necesitas ajustar parámetros como la cantidad de años a proyectar (horizonte) o las rutas de los archivos, puedes editar directamente el archivo de configuración ubicado en `config/local.yaml`.