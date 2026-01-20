# Propuesta Técnica: BCIE Data Lab (Fase 1)

**Proyecto:** Predicción y Segmentación de Créditos mediante Machine Learning  
**Contexto:** Seminario de Innovación - Maestría en Visualización de Datos Masivos (UNIR)  
**Equipo 03 D:** Willson Aguilar, Edgar García, Norman Sabillón

---

## 1. Visión y Oportunidad

El objetivo es establecer los cimientos de la primera infraestructura de Inteligencia Artificial institucional del BCIE.

- **Brecha Actual:** Transicionar del análisis puramente descriptivo/retrospectivo a una **visión prospectiva**.
- **El Desafío:** La heterogeneidad histórica entre socios fundadores y recientes impide el uso de modelos lineales tradicionales.
- **Solución:** Un laboratorio de datos centralizado ("BCIE Data Lab") que explote los activos de información para la planificación estratégica.

---

## 2. Objetivos Estratégicos

Desarrollar un ecosistema analítico automatizado bajo la metodología **CRISP-DM**:

1.  **Automatización:** Pipeline de extracción directa (API CKAN) y limpieza de datos.
2.  **Predicción:** Modelos de series temporales (**Prophet**) para proyecciones 2026-2030, validados contra una línea base (**ARIMA**).
3.  **Segmentación:** Algoritmos de Clustering (**K-Means**) para agrupar países según patrones de crédito únicos.
4.  **Visualización:** Dashboards interactivos para perfiles Ejecutivos (histórico) y Estratégicos (predictivo).

---

## 3. Arquitectura y Tecnología

Diseño robusto basado en estándares de **MLOps** y Arquitectura por Capas:

- **Flujo del Dato:**
  - 🥉 **Capa Bronce:** Ingesta cruda inmutable (Raw).
  - 🥈 **Capa Plata:** Datos procesados y normalizados.
  - 🥇 **Capa Oro:** Datos agregados listos para consumo.
- **Tecnologías:** Python 3.10, Scikit-learn, Prophet, Plotly.
- **Infraestructura:** Código modular, mantenible y escalable, "tropicalizado" a las necesidades del BCIE.

---

## 4. Impacto para el BCIE

- **Toma de Decisiones 2.0:** Capacidad de anticipar tendencias de demanda crediticia a 5 años.
- **Eficiencia:** Reducción de tiempos en la generación de escenarios base.
- **Transparencia y Modernización:** Uso auditable de datos abiertos alineado con calificaciones de riesgo AA+.

---

_Propuesta de "Primer Paso" lista para defensa académica e implementación piloto._
