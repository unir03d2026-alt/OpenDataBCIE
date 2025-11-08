# Modelado y Pronóstico de Aprobaciones del BCIE con Prophet y Datos Abiertos

Este notebook implementa un flujo completo de análisis y modelado de las aprobaciones del
Banco Centroamericano de Integración Económica (BCIE) utilizando datos abiertos oficiales
y el modelo de series temporales **Prophet**.

Forma parte del módulo:

`models/aprobaciones_prophet/`

dentro del repositorio de prácticas de Machine Learning con datos abiertos del BCIE.

---

## Objetivo

Construir un modelo reproducible que permita:

1. Integrar el histórico de aprobaciones del BCIE a partir de datos abiertos.
2. Preparar un dataset consolidado para series temporales por país, tipo de socio y sector.
3. Entrenar modelos Prophet por grupo (segmentos relevantes).
4. Generar pronósticos multi-anuales (por ejemplo 2026–2030) con intervalos de confianza.
5. Presentar visualizaciones interactivas y componentes ejecutivos listos para análisis.

El enfoque está orientado a transparencia, replicabilidad y uso práctico en análisis financiero
y de desarrollo.

---

## ¿Qué es Prophet?

**Prophet** es una librería de pronóstico de series temporales desarrollada inicialmente por Meta (Facebook),
diseñada para:

- Modelar series con tendencias no lineales.
- Incorporar estacionalidades (anuales, mensuales, semanales) de forma flexible.
- Manejar valores faltantes y cambios estructurales en la tendencia.
- Entregar resultados interpretables y robustos con poca configuración.

La formulación base es un modelo aditivo:

> y(t) = g(t) + s(t) + h(t) + ε(t)

donde:

- `g(t)` = componente de tendencia (lineal, logística u otras variantes suavizadas).
- `s(t)` = estacionalidades periódicas (por ejemplo, anual).
- `h(t)` = efectos especiales (festivos, eventos, shocks definidos por el usuario).
- `ε(t)` = término de error.

Prophet está orientado a escenarios reales de negocio: múltiples series, datos con ruido, ventanas
relativamente cortas y necesidad de automatización.

---

## ¿Por qué Prophet es adecuado para las aprobaciones del BCIE con datos abiertos?

Las aprobaciones históricas del BCIE (por país, tipo de socio, sector) presentan características donde Prophet
resulta especialmente apropiado:

1. **Frecuencia anual o baja granularidad**
   - Muchas series agregadas (por ejemplo, aprobaciones anuales por país) tienen pocas observaciones.
   - Prophet funciona correctamente con series cortas, siempre que exista una tendencia identificable.

2. **Cambios de tendencia y niveles**
   - El portafolio del BCIE puede experimentar cambios estructurales:
     ampliación de mandato, crisis financieras, shocks externos.
   - Prophet permite modelar cambios de tendencia (“changepoints”) de forma explícita y controlada.

3. **Robustez ante valores atípicos**
   - Montos extraordinarios en años específicos pueden distorsionar modelos clásicos.
   - Prophet incorpora mecanismos robustos para reducir el impacto de outliers en la tendencia.

4. **Escalabilidad por grupos**
   - El enfoque del notebook entrena Prophet por combinaciones como:
     país × tipo de socio × sector institucional.
   - Prophet es adecuado para automatizar múltiples modelos con una misma lógica,
     manteniendo consistencia metodológica y facilitando reproducción.

5. **Interpretabilidad**
   - En el contexto de banca de desarrollo y transparencia con datos abiertos,
     la capacidad de explicar la tendencia y los intervalos de confianza es clave.
   - Prophet ofrece componentes claros (tendencia, estacionalidad, intervalos) que pueden ser comunicados
     a decisiones técnicas y no técnicas.

En conjunto, Prophet ofrece un equilibrio adecuado entre rigor estadístico, facilidad de implementación,
capacidad de automatización y claridad para auditoría y comunicación pública.

---

## Comparación con otros enfoques de pronóstico

Este notebook utiliza Prophet como modelo principal, pero se alinea con una estrategia más amplia donde
pueden evaluarse otros métodos.

### Comparado con modelos clásicos (ARIMA, ETS)

- **Ventajas de Prophet:**
  - Menos sensibilidad a la especificación manual (órdenes p, d, q).
  - Manejo más directo de múltiples estacionalidades y cambios de tendencia.
  - Configuración coherente al aplicar un mismo pipeline a muchas series.

- **Cuándo preferir ARIMA/ETS:**
  - Series largas, con estructura claramente estacionaria.
  - Necesidad de modelos estadísticos clásicos con fuerte tradición regulatoria.

### Comparado con modelos basados en árboles (XGBoost, Random Forest)

- Propios de problemas de regresión supervisada con muchas variables explicativas.
- Útiles para explicar montos aprobados en función de covariables (PIB, riesgo, inflación, etc.).
- Menos directos para pronóstico puramente temporal cuando el objetivo es la proyección de la serie agregada.

En este contexto, Prophet se utiliza como modelo especializado para pronosticar la trayectoria temporal
de aprobaciones, mientras que modelos de árboles pueden integrarse en módulos complementarios.

### Comparado con redes neuronales (LSTM, Transformers para series temporales)

- **Ventajas de Prophet frente a deep learning en este caso:**
  - Menor requerimiento de datos (especialmente relevante con series anuales o pocos años por segmento).
  - Entrenamiento más simple y rápido.
  - Mayor interpretabilidad para entornos institucionales y de datos abiertos.

- **Cuándo evaluar deep learning:**
  - Gran volumen de series de alta frecuencia.
  - Integración compleja de múltiples señales externas.
  - Casos donde se justifica la complejidad adicional.

Para el caso de uso específico (aprobaciones históricas del BCIE con datos abiertos),
Prophet ofrece una relación adecuada entre calidad del pronóstico, simplicidad y transparencia,
por lo que es una elección razonable como modelo base.

---

## Datos utilizados

Los datos provienen del portal oficial de datos abiertos del BCIE:

[Portal de Datos Abiertos del BCIE](https://datosabiertos.bcie.org/)

El notebook asume como insumo principal un dataset consolidado ubicado en:

- `data/aprobaciones_desembolsos/processed/tabla_final.parquet`

Este dataset incluye, entre otros campos:

- Año / Fecha
- País
- Tipo de socio
- Sector institucional
- Monto aprobado

Cualquier transformación adicional se documenta dentro del propio notebook.

---

## Contenido del notebook

El notebook está organizado en secciones:

1. **Configuración inicial**  
   Importación de librerías, configuración de rutas y parámetros.

2. **Carga y exploración de datos**  
   Validación de estructura, rangos de fechas, consistencia y cobertura.

3. **Preparación para Prophet**  
   Construcción de las series por grupo en formato compatible (`ds`, `y`).

4. **Entrenamiento del modelo**  
   Definición del pipeline Prophet por grupo y ejecución controlada sobre múltiples combinaciones.

5. **Generación de pronósticos**  
   Cálculo de pronósticos multi-anuales con intervalos de confianza.

6. **Consolidación histórico + pronóstico**  
   Unión de datos reales y proyectados en un único dataframe (`df_unico`) para análisis.

7. **Visualizaciones interactivas**  
   Gráficos con series históricas, predicciones, bandas de confianza y filtros interactivos
   por país, tipo de socio y sector.

8. **Resultados y extensiones**  
   Exportación de salidas en formatos estándar y sugerencias para integración
   con herramientas de visualización y otros modelos.

---

## Requisitos

- Python 3.9+
- `pandas`, `numpy`
- `prophet`
- `plotly`, `ipywidgets`
- `openpyxl` (si se exportan archivos Excel)
- `scikit-learn` (para funciones auxiliares en algunos flujos)

La instalación detallada se documenta en las celdas iniciales del notebook.

---

## Uso recomendado

1. Clonar el repositorio que contiene este módulo.
2. Descargar y ubicar los datasets del portal de datos abiertos del BCIE en `data/aprobaciones_desembolsos/raw/`.
3. Generar el dataset consolidado en `data/aprobaciones_desembolsos/processed/`.
4. Ejecutar el notebook:

   `models/aprobaciones_prophet/notebooks/Modelado_y_Pronóstico_de_Aprobaciones_del_BCIE_con_Prophet_y_Datos_Abiertos.ipynb`

5. Revisar las salidas generadas y las visualizaciones interactivas.

Este notebook puede servir como plantilla para otros modelos de series temporales aplicados
a los datos abiertos del BCIE.
