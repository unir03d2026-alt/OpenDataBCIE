# Laboratorio de Machine Learning: Datos Abiertos del BCIE

[![Portal de Datos Abiertos del BCIE](https://img.shields.io/badge/Portal%20BCIE-Datos%20Abiertos-105682)](https://datosabiertos.bcie.org/)

Repositorio dedicado a experimentos, notebooks y pipelines de Machine Learning
basados en datos abiertos del Banco Centroamericano de Integración Económica (BCIE).

El objetivo es mostrar, de forma reproducible, cómo transformar los conjuntos de datos
publicados por el BCIE en casos de uso analíticos y modelos predictivos aplicables a
aprobaciones, impacto, adquisiciones y transparencia.

## 1. Áreas de datos abiertos utilizadas

Los ejemplos y notebooks de este repositorio se apoyan en las áreas de conocimiento
habilitadas en el portal de datos abiertos del BCIE:

### 1.1 Aprobaciones y desembolsos

Incluye información histórica sobre aprobaciones y desembolsos de operaciones
financiadas por el BCIE (por ejemplo, préstamos y productos de cooperación),
segmentados por país, sector, tipo de socio y otros atributos clave.

**Ideas de modelos:**

- Pronóstico multi-paso de aprobaciones y desembolsos.
- Modelos de regresión para estimar montos esperados por país, sector y tipo de socio.
- Segmentación de países o proyectos según comportamiento financiero.
- Detección de anomalías en montos, plazos o patrones de aprobación.
- Modelos de riesgo agregado: concentración por país, sector o instrumento.

### 1.2 Evaluación y medición de impacto

Contiene resultados de evaluaciones de impacto de proyectos y operaciones,
incluyendo indicadores de desarrollo, cobertura geográfica y temporal.

**Ideas de modelos:**

- Modelos de clasificación/regresión para explicar factores asociados a mayor impacto.
- Clustering de proyectos según desempeño social, económico o ambiental.
- Recomendadores de diseño de proyecto basados en experiencias exitosas.
- Modelos explicables para identificar palancas clave de impacto.

### 1.3 Adquisiciones en operaciones

Información sobre procesos de adquisición vinculados a proyectos financiados
(licitaciones, adjudicaciones, proveedores, montos, tiempos, etc.).

**Ideas de modelos:**

- Detección de anomalías en procesos de compra.
- Predicción de retrasos o riesgos en licitaciones.
- Análisis de tiempos de ciclo y modelos de duración esperada.
- Segmentación de proveedores según desempeño y especialización.

### 1.4 Adquisiciones institucionales

Datos sobre adquisiciones corporativas internas del BCIE.

**Ideas de modelos:**

- Análisis y optimización del gasto institucional.
- Clustering de proveedores institucionales.
- Detección de inconsistencias o patrones atípicos en compras internas.
- Pronósticos de demanda por categoría de bienes y servicios.

### 1.5 Cumplimiento de la Política de Acceso a la Información (PAI)

Indicadores sobre la implementación de la Política de Acceso a la Información:
tiempos de respuesta, volúmenes, niveles de cumplimiento, entre otros.

**Ideas de modelos:**

- Predicción de tiempos de respuesta a solicitudes.
- Clasificación de solicitudes por prioridad o complejidad.
- Series temporales para indicadores de transparencia.
- Alertas tempranas ante deterioro de métricas de acceso a la información.

---

## 2. Tipos de modelos de Machine Learning considerados

Según el caso de uso y el conjunto de datos, este laboratorio explora distintas familias de modelos:

- **Series temporales**  
  Prophet, ARIMA y variantes con regresores externos, modelos LSTM/GRU,
  arquitecturas tipo Transformer para series de tiempo, N-BEATS.

- **Regresión y clasificación**  
  XGBoost, LightGBM, CatBoost, Random Forest, modelos lineales regularizados
  (Ridge/Lasso/ElasticNet), entre otros.

- **Aprendizaje no supervisado**  
  K-means, HDBSCAN, UMAP, autoencoders para segmentación, reducción de dimensionalidad
  y descubrimiento de patrones.

- **Detección de anomalías**  
  Isolation Forest, Local Outlier Factor, One-Class SVM, autoencoders de reconstrucción.

- **Explicabilidad**  
  SHAP, LIME, gráficos de dependencia parcial, análisis de importancia de variables.

- **Optimización y tuning**  
  Búsqueda bayesiana (Optuna) y algoritmos evolutivos para ajuste de hiperparámetros
  y selección de modelos.

---

## 3. Estructura sugerida del repositorio

- `data/`  
  Datasets derivados de los datos abiertos del BCIE (limpios, documentados).

- `notebooks/`  
  Laboratorios por área temática:
  - `aprobaciones_desembolsos/`
  - `impacto/`
  - `adquisiciones_operaciones/`
  - `adquisiciones_institucionales/`
  - `transparencia_pai/`

- `models/`  
  Implementaciones por tipo de modelo (por ejemplo, `prophet/`, `arima/`, `xgboost/`, `anomalies/`).

- `visualizations/`  
  Gráficos interactivos y dashboards (Plotly, etc.).

- `docs/`  
  Documentación técnica, descripciones de variables, decisiones metodológicas.

---

## 4. Propósito

Demostrar, con ejemplos reproducibles, cómo los datos abiertos del BCIE pueden
aprovecharse para desarrollar modelos de Machine Learning que fortalezcan:

- la comprensión del portafolio de operaciones,
- la transparencia y rendición de cuentas,
- la gestión de riesgos,
- y la toma de decisiones basada en evidencia en instituciones de desarrollo.
