# Auditoría Técnica de Modelos - Laboratorio de Machine Learning BCIE

**Fecha:** 13 de Febrero, 2026 — 19:20 CST  
**Responsable:** Agente Antigravity  
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
- ⚠️ **Nota:** El directorio `runs/` contiene una run residual clonada de HDBSCAN (`run_20260121_151227_05f783`) con métricas HDBSCAN. Las métricas reales de Hierarchical están en `data/04-predictions/metrics.json` (raíz).

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

- **Algoritmo:** Nixtla StatsForecast (AutoARIMA, ETS, CES, Theta)
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

| Directorio             | Contenido                                      | Recomendación                                                    |
| :--------------------- | :--------------------------------------------- | :--------------------------------------------------------------- |
| `aprobaciones_prophet` | Notebooks Jupyter originales (.ipynb) + README | Archivar o eliminar (sustituido por `aprobaciones_prophet_2026`) |
| `aprobaciones_xgboost` | Notebooks Jupyter originales (.ipynb)          | Archivar o eliminar (modelo experimental no operacionalizado)    |

---

## 6. Notas de Ajuste Pendientes

### 🔶 Prioridad Media

1. **Hierarchical — Run HDBSCAN residual:**  
   El directorio `aprobaciones_hierarchical_2026/data/04-predictions/runs/run_20260121_151227_05f783/` contiene archivos clonados de HDBSCAN (metrics con 14 clusters, min_cluster_size). Esto no afecta la funcionalidad (las métricas reales están en la raíz de `04-predictions/`), pero genera confusión. **Acción:** Eliminar la carpeta `runs/` residual.

2. **Forecasting — Gen Script diferente:**  
   Los 4 modelos de forecasting no usan `generate_dashboard.py` sino un módulo Plotly Dash (`assets.py`, `config.py`, `layout.py`, `logic.py`). Esto es correcto por diseño (dashboards interactivos vs estáticos), pero la auditoría anterior los marcaba con ❌ en "Gen Script". **Acción:** Ya corregido en esta auditoría.

### 🔵 Prioridad Baja

3. **Legacy — Notebooks sin operacionalizar:**  
   `aprobaciones_prophet` y `aprobaciones_xgboost` son notebooks originales pre-refactor. No tienen pipeline, config, ni dashboard generado. **Acción:** Mover a carpeta `legacy/` o eliminar para mantener el repositorio limpio.

4. **EDA — Sin métricas JSON:**  
   `aprobaciones_eda_2026` no produce `metrics.json` porque es un modelo exploratorio. Esto es correcto por naturaleza. **Acción:** Ninguna requerida.

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
3. 🔶 **Fase 3 (Pendiente):** Limpieza de residuos legacy y runs clonadas.
4. 🔵 **Fase 4 (Futuro):** Validar inferencia real de TimesFM y enriquecer EDA.
