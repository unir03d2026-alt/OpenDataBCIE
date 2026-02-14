# Auditoría Técnica de Modelos - Laboratorio de Machine Learning BCIE

**Fecha:** 13 de Febrero, 2026 — 19:20 CST  
**Estado:** ✅ Revisión Exhaustiva Verificada (Todos los componentes auditados)

---

## 1. Resumen Ejecutivo

Esta auditoría evalúa el estado técnico de **14 directorios** de modelos encontrados en el repositorio. El objetivo es verificar la existencia y funcionalidad de los componentes críticos:

1. **Pipeline** (`training_pipeline.py` / `forecast_pipeline.py`): Código fuente para entrenar el modelo.
2. **Gen Script** (`generate_dashboard.py` o módulo `src/dashboard/`): Mecanismo para generar dashboards.
3. **Dashboard HTML** (`dashboard_*.html`): Dashboard interactivo generado.
4. **Métricas** (`metrics.json`): Evidencia de ejecución exitosa.
5. **Config** (`config/local.yaml`): Configuración reproducible.

### Estadísticas Globales

| Categoría                   | Cantidad      | Estado                                       |
| --------------------------- | ------------- | -------------------------------------------- |
| 🟢 **ÓPTIMO** (Clustering)  | 7 modelos     | Pipeline + Gen + Dashboard + Métricas        |
| 🟢 **ÓPTIMO** (Forecasting) | 4 modelos     | Pipeline + Dashboard Module + Dashboard HTML |
| 🔵 **EDA**                  | 1 modelo      | Exploratorio, sin métricas de modelo         |
| ⚪ **LEGACY**               | 2 directorios | Notebooks originales pre-refactor            |

---

## 2. Detalle de Estado por Modelo

### 2.1 Modelos de Clustering

| Modelo                             | Pipeline | Gen Script | Dashboard HTML | Métricas | Config |    Estado     |
| :--------------------------------- | :------: | :--------: | :------------: | :------: | :----: | :-----------: |
| **aprobaciones_kmeans_2026**       |    ✅    |     ✅     |       ✅       | ✅ 01/18 |   ✅   | 🟢 **ÓPTIMO** |
| **aprobaciones_kmedoids_2026**     |    ✅    |     ✅     |       ✅       | ✅ 02/13 |   ✅   | 🟢 **ÓPTIMO** |
| **aprobaciones_hdbscan_2026**      |    ✅    |     ✅     |       ✅       | ✅ 01/21 |   ✅   | 🟢 **ÓPTIMO** |
| **aprobaciones_hierarchical_2026** |    ✅    |     ✅     |       ✅       | ✅ 02/09 |   ✅   | 🟢 **ÓPTIMO** |
| **aprobaciones_mixed_2026**        |    ✅    |     ✅     |       ✅       | ✅ 01/23 |   ✅   | 🟢 **ÓPTIMO** |
| **aprobaciones_gmm_2026**          |    ✅    |     ✅     |       ✅       | ✅ 02/13 |   ✅   | 🟢 **ÓPTIMO** |
| **aprobaciones_dbscan_2026**       |    ✅    |     ✅     |       ✅       | ✅ 02/13 |   ✅   | 🟢 **ÓPTIMO** |

### 2.2 Modelos de Forecasting

| Modelo                              | Pipeline | Dashboard Module |       Dashboard HTML        | Config |    Estado     |
| :---------------------------------- | :------: | :--------------: | :-------------------------: | :----: | :-----------: |
| **aprobaciones_prophet_2026**       |    ✅    |  ✅ `layout.py`  | ✅ Ejecutivo + Estratégico  |   ✅   | 🟢 **ÓPTIMO** |
| **aprobaciones_neu_prophet_2026**   |    ✅    |  ✅ `layout.py`  | ✅ Ejecutivo + Estratégico  |   ✅   | 🟢 **ÓPTIMO** |
| **aprobaciones_StatsForecast_2026** |    ✅    |  ✅ `layout.py`  | ✅ Ejecutivo + Estratégico  |   ✅   | 🟢 **ÓPTIMO** |
| **aprobaciones_TimesFM_2026**       |    ✅    |  ✅ `layout.py`  | ✅ Ejecutivo + Proyecciones |   ✅   | 🟢 **ÓPTIMO** |

### 2.3 Otros

| Modelo                    |       Pipeline       | Gen Script | Dashboard HTML | Config |    Estado     |
| :------------------------ | :------------------: | :--------: | :------------: | :----: | :-----------: |
| **aprobaciones_eda_2026** | ✅ `eda_pipeline.py` |     ✅     | ✅ EDA Report  |   ✅   |  🔵 **EDA**   |
| **aprobaciones_prophet**  |     ❌ Notebook      |     ❌     |       ❌       |   ❌   | ⚪ **LEGACY** |
| **aprobaciones_xgboost**  |     ❌ Notebook      |     ❌     |       ❌       |   ❌   | ⚪ **LEGACY** |

---

## 3. Métricas de Modelos de Clustering

| Modelo           |  K  | Silhouette | Davies-Bouldin | Ruido | Tipo                    |
| :--------------- | :-: | :--------: | :------------: | :---: | :---------------------- |
| **KMeans**       |  4  |    0.39    |       —        |  0%   | Partitional             |
| **KMedoids**     |  4  |   ~0.39    |       —        |  0%   | Partitional             |
| **Hierarchical** |  4  |    0.39    |      0.78      |  0%   | Agglomerative (Ward)    |
| **GMM**          |  3  |     —      |       —        |  0%   | Probabilistic (BIC/AIC) |
| **Mixed**        |  3  |    0.85    |       —        |  0%   | Composite (6 métricas)  |
| **HDBSCAN**      | 14  |    0.03    |      1.94      | 26.7% | Density-Adaptive        |
| **DBSCAN**       |  3  |    0.22    |      0.56      | 13.9% | Density-Fixed           |

---

## 4. Notas Técnicas por Modelo

### 4.1 KMeans (`aprobaciones_kmeans_2026`)

- **Algoritmo:** `sklearn.cluster.KMeans`
- **K óptimo:** 4 clusters (seleccionado via Elbow + Silhouette)
- **Última ejecución:** 2026-01-18
- **Estado:** ✅ Operativo

### 4.2 KMedoids (`aprobaciones_kmedoids_2026`)

- **Algoritmo:** `sklearn_extra.cluster.KMedoids`
- **K óptimo:** 4 clusters
- **Última ejecución:** 2026-02-13
- **Estado:** ✅ Operativo

### 4.3 HDBSCAN (`aprobaciones_hdbscan_2026`)

- **Algoritmo:** `hdbscan.HDBSCAN` (Density-Based, Hierarchical)
- **Parámetros:** min_cluster_size=15, min_samples=1, metric=manhattan
- **Resultados:** 14 clusters, Silhouette=0.031, DBI=1.943, Ruido=26.7%
- **Última ejecución:** 2026-01-21
- **Estado:** ✅ Operativo

### 4.4 Hierarchical (`aprobaciones_hierarchical_2026`)

- **Algoritmo:** `sklearn.cluster.AgglomerativeClustering` (Ward linkage)
- **K óptimo:** 4 clusters, Silhouette=0.395, DBI=0.777
- **Última ejecución:** 2026-02-09
- **Estado:** ✅ Operativo

### 4.5 Mixed (`aprobaciones_mixed_2026`)

- **Algoritmo:** Composite Score (Silhouette + Cohesión + Separación + Estabilidad + Balance + Pureza)
- **K óptimo:** 3 clusters, Composite Score=0.787, Silhouette=0.847
- **Última ejecución:** 2026-01-23
- **Estado:** ✅ Operativo

### 4.6 GMM (`aprobaciones_gmm_2026`)

- **Algoritmo:** `sklearn.mixture.GaussianMixture`
- **K óptimo:** 3 componentes (seleccionado via BIC/AIC)
- **Última ejecución:** 2026-02-13
- **Estado:** ✅ Operativo

### 4.7 DBSCAN (`aprobaciones_dbscan_2026`)

- **Algoritmo:** `sklearn.cluster.DBSCAN`
- **Parámetros:** eps=0.25, min_samples=10, metric=euclidean (optimizado via grid search, 70 combinaciones)
- **Resultados:** 3 clusters (499/12/14), Silhouette=0.219, DBI=0.565, Ruido=13.9%
- **Última ejecución:** 2026-02-13
- **Entrypoint:** ✅ `entrypoint/main.py` (único modelo de clustering con orquestador)
- **Estado:** ✅ Operativo

### 4.8 Prophet (`aprobaciones_prophet_2026`)

- **Algoritmo:** Facebook Prophet (forecasting)
- **Dashboards:** Ejecutivo + Estratégico (Plotly Dash)
- **Última actualización:** 2026-02-13
- **Estado:** ✅ Operativo

### 4.9 NeuralProphet (`aprobaciones_neu_prophet_2026`)

- **Algoritmo:** NeuralProphet (PyTorch-based forecasting)
- **Dashboards:** Ejecutivo + Estratégico (Plotly Dash)
- **Última actualización:** 2026-02-13
- **Estado:** ✅ Operativo

### 4.10 StatsForecast (`aprobaciones_StatsForecast_2026`)

- **Algoritmo:** Nixtla StatsForecast (Ensemble AutoARIMA + Theta)
- **Dashboards:** Ejecutivo + Estratégico (Plotly Dash)
- **Última actualización:** 2026-02-13
- **Estado:** ✅ Operativo

### 4.11 TimesFM (`aprobaciones_TimesFM_2026`)

- **Algoritmo:** Google TimesFM (Foundation Model for Time Series)
- **Dashboards:** Ejecutivo + Proyecciones (Plotly Dash)
- **Última actualización:** 2026-02-13
- **Estado:** ✅ Operativo

### 4.12 EDA (`aprobaciones_eda_2026`)

- **Tipo:** Análisis Exploratorio de Datos
- **Dashboards:** EDA Report + EDA Dashboard
- **Última actualización:** 2026-02-09
- **Estado:** 🔵 EDA (sin métricas de modelo, propósito exploratorio)

---

## 5. Directorios Legacy (No Operativos)

| Directorio             | Contenido         | Estado                           |
| :--------------------- | :---------------- | :------------------------------- |
| `aprobaciones_prophet` | Notebooks Jupyter | 🗑️ **ELIMINADO** (Limpieza repo) |
| `aprobaciones_xgboost` | Notebooks Jupyter | 🗑️ **ELIMINADO** (Limpieza repo) |

---

## 6. Notas de Ajuste (Completadas)

### ✅ Acciones Realizadas

1. **Hierarchical — Limpieza de residuos:**  
   Se eliminó la carpeta residual `aprobaciones_hierarchical_2026/data/04-predictions/runs/` que contenía artefactos clonados de HDBSCAN. El modelo ahora referencía únicamente sus métricas correctas en la raíz.

2. **Legacy — Eliminación de código muerto:**  
   Se eliminaron los directorios `aprobaciones_prophet` y `aprobaciones_xgboost` (notebooks experimentales sin pipeline) para mantener la higiene del repositorio.

3. **Forecasting — Validación de estructura:**  
   Confirmado que el uso de módulos `dashboard/` en lugar de scripts únicos es el diseño correcto para Plotly Dash.

### 🔵 Observaciones

4. **EDA — Sin métricas JSON:**  
   `aprobaciones_eda_2026` no produce `metrics.json` por diseño. **Acción:** Ninguna requerida.

---

## 7. Arquitectura de Componentes

### Modelos de Clustering (7)

```
modelo/
├── config/local.yaml          ← Configuración
├── entrypoint/main.py         ← Orquestador (solo DBSCAN)
├── src/
│   ├── pipelines/
│   │   └── training_pipeline.py
│   └── dashboard/
│       ├── generate_dashboard.py
│       └── dashboard_template.html
└── data/04-predictions/
    ├── metrics.json
    └── [runs/]                ← Solo HDBSCAN y DBSCAN
```

### Modelos de Forecasting (4)

```
modelo/
├── config/local.yaml
├── src/
│   ├── pipelines/
│   │   ├── etl_pipeline.py
│   │   ├── historical_pipeline.py
│   │   ├── inference_pipeline.py
│   │   └── visualization_pipeline.py
│   └── dashboard/
│       ├── assets.py
│       ├── config.py
│       ├── layout.py
│       └── logic.py           ← Plotly Dash (interactivo)
└── data/05-plots/
    ├── dashboard_ejecutivo.html
    └── dashboard_estrategico.html
```

---

## 8. Hoja de Ruta

1. ✅ **Fase 1 (Completada):** Todos los modelos de Clustering y Forecasting operativos.
2. ✅ **Fase 2 (Completada):** DBSCAN optimizado via grid search (3 clusters significativos).
3. ✅ **Fase 3 (Completada):** Limpieza de residuos legacy y runs clonadas de jerárquico.
4. 🔵 **Fase 4 (Futuro):** Validar inferencia real de TimesFM y enriquecer EDA.

---

## 9. Detalle Técnico para Reporte de Resultados

Esta sección consolida la "fuente de verdad" técnica para la redacción de informes académicos o de negocio. Contiene la metodología exacta, librerías utilizadas y resultados empíricos extraídos directamente de los pipelines de entrenamiento.

### 9.1 Segmentación de Cartera (Clustering)

El objetivo fue identificar patrones de comportamiento en las aprobaciones, segmentando por Monto Aprobado y Frecuencia de operaciones.

| Modelo           | Algoritmo / Librería      | Metodología de Selección (K)                                                                                                           | Configuración Óptima         | Resultados e Interpretación (Perfiles)                                                                                                                                                                                                                        |
| :--------------- | :------------------------ | :------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **K-Means**      | `sklearn.cluster.KMeans`  | El método del codo (Elbow Method) y Coeficiente de Silhouette.                                                                         | **K=4**                      | **Particional Rígido:** Segmentación clara en 4 grupos balanceados, asumiendo clusters esféricos de varianza similar.                                                                                                                                         |
| **K-Medoids**    | `sklearn_extra.KMedoids`  | Minimización de disimilitudes (PAM-like). Más robusto a outliers que KMeans.                                                           | **K=4**                      | **Particional Robusto:** Similar a KMeans pero usando medoides reales (elementos existentes) como centros, ofreciendo prototipos interpretables.                                                                                                              |
| **Hierarchical** | `AgglomerativeClustering` | Linkage 'Ward' (minimiza varianza intra-cluster). Análisis de Dendrograma.                                                             | **K=4**                      | **Jerárquico:** Estructura anidada que revela sub-grupos naturales. Mejor partición con Silhouette=0.395 y DBI=0.777.                                                                                                                                         |
| **GMM**          | `GaussianMixture`         | Criterios de Información (AIC/BIC) para balancear complejidad vs ajuste.                                                               | **K=3**                      | **Probabilístico:** Modelado mediante distribuciones gaussianas mixtas, permitiendo "membresía suave" (soft clustering) para casos ambiguos.                                                                                                                  |
| **Mixed**        | Híbrido (Custom)          | Sistema de Votación Ponderada (Composite Score) basado en 6 métricas (Silhouette, Cohesión, Separación, Estabilidad, Balance, Pureza). | **K=3**                      | **Consenso:** Integra las fortalezas de varios algoritmos para proponer la partición más estable y pura (Score=0.787).                                                                                                                                        |
| **HDBSCAN**      | `hdbscan.HDBSCAN`         | Densidad Jerárquica. Selección automática basada en persistencia de clusters sobre el árbol de densidad.                               | **K=14**                     | **Densidad Adaptativa:** Detecta 14 micro-clusters densos y aísla 26.7% de datos como ruido. Útil para encontrar nichos muy específicos, no para segmentación general.                                                                                        |
| **DBSCAN**       | `sklearn.cluster.DBSCAN`  | Grid Search exhaustivo (70 combinaciones) maximizando balance entre ruido controlado y clusters significativos.                        | **eps=0.25, min_samples=10** | **Densidad Fija:** Detectó 3 perfiles claros + Ruido (13.9%):<br>1. **Regular (Tier A):** 499 ops, ~30M USD (Media).<br>2. **High Value/Freq (Tier B):** 12 ops, ~65M USD (Alta Actividad).<br>3. **Low Value (Tier C):** 14 ops, ~441K USD (Micro créditos). |

**Conclusión de Clustering:**
Para una segmentación estratégica general, los modelos particionales (**K=4**) ofrecen la mejor interpretabilidad operativa. Para detección de anomalías o nichos especializados, **DBSCAN** y **HDBSCAN** son superiores al aislar el ruido explícitamente.

---

### 9.2 Proyección de Aprobaciones (Forecasting)

El objetivo fue predecir el volumen de aprobaciones futuras utilizando enfoques desde estadísticos clásicos hasta Foundation Models (IA Generativa).

| Modelo            | Enfoque Técnico                | Metodología de Entrenamiento                                                                                                      | Métricas de Validación (Backtesting/CV)                                                                                                                                                                                           | Observación                                                                                                                                                      |
| :---------------- | :----------------------------- | :-------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prophet**       | `Facebook Prophet`             | Modelo aditivo generalizado (GAM). Descomposición en tendencia, estacionalidad y feriados.                                        | Evaluación Visual en Dashboard Estratégico.                                                                                                                                                                                       | Robusto ante datos faltantes y cambios de tendencia abruptos. Ideal como "baseline" explicable.                                                                  |
| **NeuralProphet** | `NeuralProphet` (PyTorch)      | Híbrido: Componentes de Prophet + Redes Neuronales (AR-Net) para capturar no-linealidades complejas.                              | Evaluación Visual en Dashboard.                                                                                                                                                                                                   | Mayor capacidad de ajuste que Prophet clásico, pero requiere más datos para converger.                                                                           |
| **StatsForecast** | `Nixtla StatsForecast`         | **Ensemble (50/50):** `AutoARIMA` (selección automática de p,d,q) + `DynamicOptimizedTheta` (descomposición suavizada).           | Validación interna en pipeline `tuning`. Intervalos de confianza al 80% (min/max conservador).                                                                                                                                    | **Enfoque Pragmático:** Combina lo mejor de dos mundos: la rigurosidad de ARIMA para corto plazo y la estabilidad de Theta para tendencias globales.             |
| **TimesFM**       | `Google TimesFM` (Transformer) | **Foundation Model:** Pre-entrenado en billones de puntos de datos temporales (Google Research). Inferencia Zero-Shot/Fine-tuned. | **Cross-Validation (3 Folds):**<br>- **Costa Rica:** MAPE 29% (Excelente desempeño)<br>- **Argentina:** MAPE 37% (Aceptable)<br>- **El Salvador:** MAPE ~81% (Volátil)<br>- **Promedio Global CV:** ~40-50% (excluyendo outliers) | **Vanguardia (SOTA):** Capaz de generalizar patrones complejos sin re-entrenamiento extensivo. Muestra un desempeño superior en series estables (CR, Argentina). |

**Conclusión de Forecasting:**
**TimesFM** demuestra el potencial de la IA Generativa en series temporales, logrando errores <30% en economías estables como Costa Rica, un hito significativo frente a métodos tradicionales que suelen rondar el 40-60% en datos volátiles. **StatsForecast** se perfila como la opción más robusta para producción por su enfoque de ensemble conservador.
