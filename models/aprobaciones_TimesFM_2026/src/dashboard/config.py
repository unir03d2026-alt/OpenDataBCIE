"""
Módulo de Configuración

Este archivo almacena constantes, diccionarios de mapeo y textos estáticos
utilizados en AMBOS tableros (Predicciones y Ejecutivo).
"""

# Orden jerárquico estricto para visualización de países
COUNTRY_ORDER = [
    "Guatemala", "El Salvador", "Honduras", "Nicaragua", "Costa Rica",
    "Panamá", "República Dominicana", "Belice",
    "México", "Taiwán", "Argentina", "Colombia", "España", "Corea", "Cuba"
]

# Mapeo de países a tipos de socios
SOCIO_MAP = {
    'GUATEMALA': 'Fundador', 'EL SALVADOR': 'Fundador', 'HONDURAS': 'Fundador', 
    'NICARAGUA': 'Fundador', 'COSTA RICA': 'Fundador',
    'PANAMA': 'Regional No Fundador', 'PANAMÁ': 'Regional No Fundador',
    'REPUBLICA DOMINICANA': 'Regional No Fundador', 'REPÚBLICA DOMINICANA': 'Regional No Fundador',
    'BELICE': 'Regional No Fundador', 'BELIZE': 'Regional No Fundador',
    'MEXICO': 'Extrarregional', 'MÉXICO': 'Extrarregional',
    'TAIWAN': 'Extrarregional', 'TAIWÁN': 'Extrarregional', 'REPUBLICA DE CHINA (TAIWAN)': 'Extrarregional',
    'ARGENTINA': 'Extrarregional', 'COLOMBIA': 'Extrarregional', 
    'ESPAÑA': 'Extrarregional', 'ESPANA': 'Extrarregional',
    'COREA': 'Extrarregional', 'REPUBLICA DE COREA': 'Extrarregional',
    'CUBA': 'Extrarregional'
}

# Diccionario de traducciones de datos (Contenido de tablas)
DATA_DICT = {
    "República Dominicana": "Dominican Republic", "España": "Spain", "Corea": "Korea", "República De Corea": "Korea",
    "México": "Mexico", "Panamá": "Panama", "Belice": "Belize", "Taiwán": "Taiwan", "Argentina": "Argentina",
    "Colombia": "Colombia", "Guatemala": "Guatemala", "Honduras": "Honduras", "El Salvador": "El Salvador",
    "Nicaragua": "Nicaragua", "Costa Rica": "Costa Rica", "Cuba": "Cuba",
    "Fundador": "Founder", "Regional No Fundador": "Regional Non-Founder", "Extrarregional": "Non-Regional", "Otro": "Other",
    "Público": "Public", "Sector Público": "Public Sector", "Privado": "Private", "Sector Privado": "Private Sector",
    "Financiero": "Financial", "No Definido": "Undefined", "Proyección Global": "Global Forecast"
}

# --- TEXTOS PARA EL DASHBOARD DE PREDICCIONES (PROPHET) ---
UI_TEXTS = {
    "es": {
        "title": "Análisis de Proyección de Aprobaciones de Datos Abiertos del BCIE",
        "subtitle": "Modelo de Inteligencia Artificial (Prophet) • Escenarios 2026-2030",
        "sidebar": "Filtros de Control",
        "type": "Tipo de Socio",
        "sector": "Sector Institucional",
        "country": "País",
        "restore": "↺ RESTAURAR",
        "context": "Alcance",
        "last_real": "Cierre Real",
        "proj": "Proyección Total",
        "growth": "Crecimiento Est.",
        "yoy_title": "Trayectoria Anual Estimada",
        "chart_title": "Tendencia Histórica y Proyección",
        "table_title": "Matriz Detallada de Pronósticos",
        "footer": "Este tablero presenta proyecciones financieras basadas en datos históricos auditados y modelos de machine learning. Los resultados reflejan un análisis estadístico basado en patrones históricos y no constituyen un compromiso financiero vinculante por parte del BCIE.",
        "rights": "© {year} | UNIR–BCIE | Trabajo de Colaboración Académica | Proyecto Final de Máster | Equipo 03-D | Desarrollado por Edgar García, Norman Sabillón y Wilson Aguilar | Todos los derechos reservados.",
        "total": "Total General",
        "subtotal": "Subtotal", 
        "chart_hist": "Histórico",
        "chart_pred": "Pronóstico",
        "update": "Datos Actualizados:",
        "all": "Todos",
        "scenario_on": "Ocultar Intervalos",
        "scenario_off": "Ver Intervalos",
        "export": "Exportar CSV",
        "tip_theme": "Cambiar Tema",
        "tip_lang": "Cambiar Idioma",
        "txt_theme_light": "Claro", "txt_theme_dark": "Oscuro",
        "txt_lang_es": "Esp", "txt_lang_en": "Ing",
        "txt_snap": "Captura", "txt_pdf": "PDF"
    },
    "en": {
        "title": "Open Data Approvals Projection Analysis",
        "subtitle": "Artificial Intelligence Model (Prophet) • Scenarios 2026-2030",
        "sidebar": "Control Filters",
        "type": "Partner Type",
        "sector": "Institutional Sector",
        "country": "Country",
        "restore": "↺ Reset",
        "context": "Context",
        "last_real": "Last Actual",
        "proj": "Total Forecast",
        "growth": "Est. Growth",
        "yoy_title": "Estimated Annual Trajectory",
        "chart_title": "Historical Trend & Forecast",
        "table_title": "Detailed Forecast Matrix",
        "footer": "This dashboard presents financial projections based on audited historical data and machine learning models. The results reflect statistical analysis based on historical patterns and do not constitute a binding financial commitment by CABEI.",
        "rights": "© {year} | UNIR–CABEI | Academic Collaboration Work | Master's Final Project | Team 03-D | Developed by Edgar García, Norman Sabillón and Wilson Aguilar | All rights reserved.",
        "total": "Grand Total",
        "subtotal": "Subtotal",
        "chart_hist": "Historical",
        "chart_pred": "Forecast",
        "update": "Data Updated:",
        "all": "All",
        "scenario_on": "Hide Intervals",
        "scenario_off": "Show Intervals",
        "export": "Export CSV",
        "tip_theme": "Toggle Theme",
        "tip_lang": "Switch Language",
        "txt_theme_light": "Light", "txt_theme_dark": "Dark",
        "txt_lang_es": "Spa", "txt_lang_en": "Eng",
        "txt_snap": "Snapshot", "txt_pdf": "PDF"
    }
}

# --- TEXTOS PARA EL DASHBOARD EJECUTIVO (HISTÓRICO) ---
UI_HIST_TEXTS = {
    "es": {
        "main_title": "Dashboard Ejecutivo BCIE",
        "sub_title": "Análisis Integral de Aprobaciones Históricas (Datos Reales)",
        "sidebar": "Filtros Históricos",
        "type": "Tipo de Socio",
        "country": "País",
        "restore": "↺ RESTAURAR",
        "kpi_total": "Monto Total Aprobado",
        "kpi_count": "Cantidad de Aprobaciones",
        "kpi_avg": "Promedio por Aprobación",
        "card_evolution": "Evolución Temporal de Aprobaciones",
        "card_sector": "Distribución por Sector Institucional",
        "card_partner": "Por Tipo de Socio",
        "card_country": "Participación por País",
        "card_table": "Detalle Anual",
        "col_year": "Año",
        "col_amount": "Monto",
        "col_count": "Cantidad",
        "col_avg": "Promedio por<br>Aprobación",
        "col_var": "Variación YoY<br>(Monto / Cantidad)",
        "footer": "Este tablero presenta datos reales obtenidos del portal de datos abiertos del BCIE. A partir de 2010, se observa una disminución en la cantidad de aprobaciones pero un aumento en los montos, reflejando el inicio de proyectos más grandes.",
        "rights": "© {year} | UNIR–BCIE | Trabajo de Colaboración Académica | Proyecto Final de Máster | Equipo 03-D | Desarrollado por Edgar García, Norman Sabillón y Wilson Aguilar | Todos los derechos reservados.",
        "update": "Datos Actualizados:",
        "all": "Todos",
        "export": "Exportar",
        "tip_theme": "Cambiar Tema",
        "tip_lang": "Cambiar Idioma",
        "txt_theme_light": "Claro", "txt_theme_dark": "Oscuro",
        "txt_lang_es": "Esp", "txt_lang_en": "Ing",
        "axis_amount": "Monto (USD)", "axis_count": "Cantidad",
        "lbl_sector_public": "Sector Público", "lbl_sector_private": "Sector Privado",
        "lbl_sector_financial": "Sector Financiero", "lbl_other": "Otro",
        "lbl_amount": "Monto", "lbl_quantity": "Cantidad",
        "txt_snap": "Captura", "txt_pdf": "PDF",
        "countries": {
            "Guatemala": "Guatemala",
            "El Salvador": "El Salvador",
            "Honduras": "Honduras",
            "Nicaragua": "Nicaragua",
            "Costa Rica": "Costa Rica",
            "Panamá": "Panamá",
            "República Dominicana": "República\nDominicana",
            "Belice": "Belice",
            "Argentina": "Argentina",
            "Colombia": "Colombia",
            "México": "México",
            "Cuba": "Cuba",
            "Regional": "Regional",
             "Republica Dominicana": "República\nDominicana"
        }
    },
    "en": {
        "main_title": "BCIE Executive Dashboard",
        "sub_title": "Comprehensive Analysis of Historical Approvals (Real Data)",
        "sidebar": "Historical Filters",
        "type": "Partner Type",
        "country": "Country",
        "restore": "↺ RESET",
        "kpi_total": "Total Approved Amount",
        "kpi_count": "Number of Approvals",
        "kpi_avg": "Average per Approval",
        "card_evolution": "Temporal Evolution of Approvals",
        "card_sector": "Distribution by Institutional Sector",
        "card_partner": "By Partner Type",
        "card_country": "Participation by Country",
        "card_table": "Yearly Detail",
        "col_year": "Year",
        "col_amount": "Amount",
        "col_count": "Quantity",
        "col_avg": "Average per<br>Approval",
        "col_var": "YoY Variation<br>(Amount / Quantity)",
        "footer": "This dashboard presents real data obtained from the BCIE open data portal. From 2010 onwards, a decrease in the number of approvals is observed but an increase in amounts, reflecting the start of larger projects.",
        "rights": "© {year} | UNIR–CABEI | Academic Collaboration Work | Master's Final Project | Team 03-D | Developed by Edgar García, Norman Sabillón and Wilson Aguilar | All rights reserved.",
        "update": "Data Updated:",
        "all": "All",
        "export": "Export",
        "tip_theme": "Toggle Theme",
        "tip_lang": "Switch Language",
        "txt_theme_light": "Light", "txt_theme_dark": "Dark",
        "txt_lang_es": "Esp", "txt_lang_en": "Ing",
        "axis_amount": "Amount (USD)", "axis_count": "Quantity",
        "lbl_sector_public": "Public Sector", "lbl_sector_private": "Private Sector",
        "lbl_sector_financial": "Financial Sector", "lbl_other": "Other",
        "lbl_amount": "Amount", "lbl_quantity": "Quantity",
        "txt_snap": "Snapshot", "txt_pdf": "PDF",

        "countries": {
            "Guatemala": "Guatemala",
            "El Salvador": "El Salvador",
            "Honduras": "Honduras",
            "Nicaragua": "Nicaragua",
            "Costa Rica": "Costa Rica",
            "Panamá": "Panama",
            "República Dominicana": "Dominican\nRepublic",
            "Belice": "Belize",
            "Argentina": "Argentina",
            "Colombia": "Colombia",
            "México": "Mexico",
            "Cuba": "Cuba",
            "Regional": "Regional",
            "Republica Dominicana": "Dominican\nRepublic"
        }
    }
}
