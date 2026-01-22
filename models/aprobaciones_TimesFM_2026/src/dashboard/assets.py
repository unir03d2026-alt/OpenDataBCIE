"""
Módulo de Activos Visuales e Interactividad

Este módulo genera los bloques de código CSS y JavaScript que se inyectarán
en el HTML final. Define la apariencia visual (estilos, colores, estructura)
y la lógica del lado del cliente (gráficos Plotly, filtros, exportación).
"""

import json

def get_css():
    """
    Retorna el bloque de estilos CSS para el dashboard.
    Define variables de color, estructura de rejilla y componentes UI.
    
    Returns:
        str: Bloque HTML <style> completo.
    """
    return """
    <style>
        :root { 
            --font-main: 'Inter', sans-serif;
            --primary: #105682; --text-dark: #1e293b; --text-light: #64748b; --bg-body: #f8fafc; --bg-card: #ffffff; --border: #e2e8f0; --hover: #f1f5f9; --success: #10b981; --danger: #ef4444; --tooltip-bg: #1e293b; --tooltip-text: #ffffff; --bar-color: rgba(16, 86, 130, 0.12); 
        }
        [data-theme="dark"] { 
            --primary: #38bdf8; --text-dark: #f1f5f9; --text-light: #94a3b8; --bg-body: #0f172a; --bg-card: #1e293b; --border: #334155; --hover: #334155; --tooltip-bg: #ffffff; --tooltip-text: #0f172a; --bar-color: rgba(56, 189, 248, 0.20); 
        }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--text-light); }

        body { font-family: var(--font-main); background: var(--bg-body); margin: 0; padding: 0; color: var(--text-dark); transition: background 0.3s; overflow: hidden; }
        
        .top-nav { position: fixed; top: 0; left: 0; right: 0; height: 80px; background: var(--bg-card); border-bottom: 5px solid var(--primary); display: flex; align-items: center; justify-content: space-between; padding: 0 30px; z-index: 50; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .nav-controls { display: flex; align-items: center; gap: 15px; }
        
        .dashboard-wrapper { display: flex; height: calc(100vh - 80px); flex-direction: row; margin-top: 80px; overflow: hidden; }
        .sidebar { width: 240px; background: var(--bg-card); border-right: 1px solid var(--border); padding: 20px; flex-shrink: 0; display: flex; flex-direction: column; position: sticky; top: 80px; height: calc(100vh - 80px); overflow-y: auto; z-index: 10; transition: background 0.3s; }
        
        .sidebar-title { font-size: 13px; font-weight: 800; color: var(--primary); margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid var(--primary); }
        .filter-label { font-size: 11px; font-weight: 700; color: var(--text-light); margin-bottom: 8px; display: block; }
        .kpi-label { font-size: 10px; font-weight: 700; color: var(--text-light); margin-bottom: 5px; }
        .yoy-title { font-size: 12px; font-weight: 700; color: var(--primary); margin-bottom: 10px; }
        
        .filter-group { margin-bottom: 20px; }
        .btn-vertical { font-family: var(--font-main); display: block; width: 100%; text-align: left; padding: 9px 12px; margin-bottom: 5px; border: 1px solid var(--border); background: var(--bg-card); border-radius: 6px; cursor: pointer; font-size: 12px; color: var(--text-dark); font-weight: 500; transition: all 0.2s; }
        .btn-vertical:hover { background: var(--hover); }
        .btn-vertical.active { background: var(--primary); color: white; border-color: var(--primary); font-weight: 600; }
        
        .toggle-wrapper { display: flex; flex-direction: column; align-items: center; gap: 4px; }
        .toggle-switch { position: relative; width: 80px; height: 30px; background: var(--bg-body); border: 1px solid var(--border); border-radius: 15px; cursor: pointer; display: flex; align-items: center; justify-content: space-between; padding: 2px; transition: background 0.3s; }
        .toggle-switch.active { background: #94a3b8; border-color: #94a3b8; }
        .toggle-knob { width: 24px; height: 24px; background: white; border-radius: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.2); transition: transform 0.3s; position: absolute; left: 3px; z-index: 2; }
        .toggle-switch.active .toggle-knob { transform: translateX(50px); }
        .toggle-icon { font-size: 14px; z-index: 1; margin: 0 8px; user-select: none; }
        .toggle-labels { display: flex; justify-content: space-between; width: 100%; font-size: 9px; font-weight: 700; color: var(--text-light); padding: 0 6px; }
        .toggle-labels span { flex: 1; text-align: center; }
        
        .btn-reset { font-family: var(--font-main); width: 100%; padding: 10px; background: transparent; border: 1px solid var(--danger); color: var(--danger); border-radius: 6px; font-weight: 700; font-size: 11px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 5px; transition: background 0.2s; }
        .btn-reset:hover { background: var(--danger); color: white; }
        .btn-reset:hover { background: var(--danger); color: white; }
        
        /* TOGGLE COMPACTO PARA GRÁFICOS (Monto vs Cantidad) */
        .toggle-compact { position: relative; width: 60px; height: 24px; background: var(--bg-body); border: 1px solid var(--border); border-radius: 12px; cursor: pointer; display: flex; align-items: center; justify-content: space-between; padding: 2px; transition: all 0.3s; }
        .toggle-compact.monto { border-color: var(--success); background: rgba(34, 197, 94, 0.05); }
        .toggle-compact.cant { border-color: var(--primary); background: rgba(16, 86, 130, 0.05); }
        
        .toggle-compact .u-knob { width: 18px; height: 18px; background: white; border-radius: 50%; box-shadow: 0 1px 3px rgba(0,0,0,0.2); position: absolute; left: 2px; transition: transform 0.3s, background 0.3s; z-index: 2; }
        .toggle-compact.cant .u-knob { transform: translateX(36px); background: var(--primary); }
        .toggle-compact.monto .u-knob { background: var(--success); }
        
        .toggle-txt { font-size: 10px; font-weight:800; z-index:1; padding:0 6px; user-select: none; }

        .main-content { flex-grow: 1; padding: 20px; display: grid; grid-template-columns: 260px 1fr; grid-template-rows: 1fr auto; gap: 20px; overflow: hidden; height: 100%; background: var(--bg-body); }
        
        .kpi-section { display: flex; flex-direction: column; gap: 10px; padding-right: 2px; overflow-y: auto; height: 100%; }
        .kpi-card { background: var(--bg-card); padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08); border: 1px solid var(--border); display: flex; flex-direction: column; justify-content: center; text-align: center; flex-shrink: 0; min-height: 150px; }
        
        .charts-wrapper { display: flex; flex-direction: column; gap: 20px; min-width: 0; height: 100%; overflow: hidden; }
        
        .section-chart, .section-table { background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08); display: flex; flex-direction: column; overflow: hidden; padding: 25px; }
        .section-chart { flex: 1; min-height: 0; }
        .section-table { flex: 0 1 auto; min-height: 0; }
        
        .kpi-label { font-size: 11px; font-weight: 700; color: var(--text-light); margin-bottom: 4px; text-transform: uppercase; }
        .kpi-value { font-size: 24px; font-weight: 800; color: var(--text-dark); }
        .kpi-growth { font-size: 12px; font-weight: 600; margin-top: 4px; }
        
        .yoy-pct { font-size: 12px; font-weight: 700; background: transparent; padding: 2px 6px; border-radius: 4px; }
        
        .header-title h1 { margin: 0; font-size: 24px; font-weight: 800; color: var(--primary); }
        .header-title .subtitle { font-size: 14px; color: var(--text-light); margin-top: 4px; }
        .update-badge { font-size: 11px; background: var(--hover); color: var(--text-light); padding: 5px 10px; border-radius: 4px; }
        
        .yoy-list { display: flex; gap: 10px; flex: 1; width: 100%; overflow-x: auto; }
        
        /* ESTILOS ESPECÍFICOS PARA TRAYECTORIA ANUAL (YOY) */
        .card-yoy {
            background: var(--bg-card);
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
            padding: 20px 25px; /* Padding ajustado a la imagen */
            display: flex;
            flex-direction: column;
            height: 100%;
        }

        /* HEADER Y CONTENEDOR PRINCIPAL */
        
        .footer-compact { grid-column: 1 / -1; margin-top: auto; margin-left: -20px; margin-right: -20px; margin-bottom: -20px; width: calc(100% + 40px); padding: 5px 0; text-align: center; border-top: 1px solid var(--border); display: flex; flex-direction: column; align-items: center; justify-content: center; background: transparent; }
        .footer-disclaimer { font-size: 11px; color: var(--text-light); max-width: none; width: 95%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin: 0 auto 4px; font-style: italic; line-height: 1.2; }
        .footer-legal { font-size: 11px; font-weight: 700; color: var(--primary); margin-bottom: 5px; }
        .yoy-header {
            font-size: 13px;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 10px;
            text-align: left;
        }

        /* AREA DE SCROLL VERTICAL (SOLA COLUMNA) */
        .yoy-scroll-area {
            display: flex;
            flex-direction: column; /* Apilar verticalmente */
            gap: 10px;
            overflow-y: auto; /* Scroll vertical si excede el alto */
            padding-right: 5px; /* Espacio para scrollbar limpio */
            flex: 1; /* Ocupar todo el alto disponible */
        }
        
        /* MAIN CONTENT: GRID OPTIMIZED */
        .main-content-exec { flex-grow: 1; padding: 20px; display: flex; flex-direction: column; gap: 20px; overflow: hidden; height: 100%; background: var(--bg-body); }
        .exec-grid { display: grid; grid-template-columns: 320px 1fr 500px; grid-template-rows: 1fr; gap: 20px; height: 100%; overflow: hidden; }
        
        .kpi-title-exec { font-size: 11px; font-weight: 700; color: var(--text-light); text-transform: uppercase; margin-bottom: 2px; text-align: center; width: 100%; }
        .kpi-val-exec { font-size: 24px; font-weight: 800; color: var(--text-dark); text-align: center; width: 100%; line-height: 1.1; }
        .kpi-box { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 15px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08); flex: 1; }
        .chart-box { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08); }
        .table-box { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08); height: 100%; }
        .table-scroll { flex: 1; overflow-y: auto; width: 100%; padding-right: 5px; }

        /* TARJETA INDIVIDUAL POR AÑO (ESTILO CLARO) */
        .yoy-single-card {
            width: 100%; /* Ocupar ancho completo del contenedor */
            background: var(--bg-body);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            transition: all 0.2s;
            flex: 1; /* Estirarse para ocupar espacio vertical equitativamente */
            min-height: 0; /* Permitir encoger si es necesario, aunque flex:1 suele expandir */
        }
        
        .yoy-single-card:hover { transform: translateX(2px); border-color: var(--primary); }

        .yoy-year-text { font-size: 13px; font-weight: 700; color: var(--text-light); margin-bottom: 2px; }
        .yoy-val-text { font-size: 16px; font-weight: 800; color: var(--text-dark); margin-bottom: 2px; }
        .yoy-pct-text { font-size: 12px; font-weight: 700; }
        
        .pos { color: var(--success); } .neg { color: var(--danger); }
        
        .card-header-compact { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .card-title-compact { font-size: 14px; font-weight: 700; color: var(--primary); margin: 0; }
        
        .btn-action { font-family: var(--font-main); padding: 6px 16px; border-radius: 6px; font-size: 13px; font-weight: 700; cursor: pointer; border: 1px solid transparent; transition: 0.2s; min-width: 100px; text-align: center; }
        .btn-toggle { background: var(--bg-body); color: var(--text-light); border: 1px solid var(--border); }
        .btn-toggle.active { background: var(--primary); color: white; border-color: var(--primary); }
        .btn-export { background: var(--success); color: white; }
        .btn-export:hover { opacity: 0.9; }

        /* Estilos especificos para botones Captura/PDF estilo Estratégico */
        .btn-ghost-primary { 
            background: transparent; 
            border: 1px solid var(--primary); 
            color: var(--primary); 
        }
        .btn-ghost-primary:hover { 
            background: var(--hover); 
        }
        .btn-solid-primary { 
            background: var(--primary); 
            border: 1px solid var(--primary); 
            color: white; 
        }
        .btn-solid-primary:hover { 
            opacity: 0.9; 
        }
        /* Ajuste para Dark Mode si es necesario */
        [data-theme="dark"] .btn-ghost-primary { border-color: var(--primary); color: var(--primary); }
        [data-theme="dark"] .btn-solid-primary { background: var(--primary); color: var(--text-dark); } 
        /* En dark mode, primary es #38bdf8 (celeste). Texto negro sobre celeste es más legible o blanco? */
        /* Strategic image shows PDF button is Light Blue with White Text? verify image. */
        /* Image 4 (Dark Mode PDF): Solid Light Blue background. Text looks White or extremely light grey. */
        /* Let's stick to white text for solid button unless contrast fails. #38bdf8 is light, white text might be hard. */
        /* Reviewing assets.py: --primary in dark is #38bdf8. White on #38bdf8 is fail. */
        /* Wait, in Image 3/4 the text on PDF button looks white. */
        /* I will set color: #1e293b (Dark Blue) for solid button in dark mode if needed, or white. */
        /* Let's trust the primary color definition. */
        [data-theme="dark"] .btn-solid-primary { color: #0f172a; } /* Dark text on light blue button for contrast */
        
        #chart { width: 100%; height: 100%; min-height: 0; }
        .table-container { overflow-x: visible; overflow-y: visible; }
        table { width: 100%; border-collapse: collapse; font-size: 12px; color: var(--text-dark); }
        th { background: var(--hover); color: var(--text-dark); padding: 6px; font-weight: 700; border-bottom: 2px solid var(--border); position: sticky; top: 0; z-index: 5; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        td { padding: 6px; border-bottom: 1px solid var(--border); text-align: center; color: var(--text-dark); position: relative; z-index: 1; height: 32px; }
        .row-subtotal td { background: var(--hover); font-weight: 700; border-top: 1px solid var(--border); }
        .row-total td { background: var(--primary) !important; color: white; font-weight: 700; }
        
        /* DATA BARS EN LA MATRIZ - SUAVES Y NO INVADEN TODO EL ANCHO */
        .cell-bar-container {
            position: absolute;
            top: 4px; bottom: 4px;
            left: 5%; /* Centrado relativo o desde la izquierda? Mejor desde izq con margen */
            height: auto;
            background: var(--primary);
            opacity: 0.15; /* Suave para ambos temas */
            border-radius: 4px;
            z-index: -1; /* Detras del texto */
            pointer-events: none;
        }
        .cell-left { text-align: left !important; padding-left: 15px; }
        
        tr:nth-child(even) td { background-color: rgba(0,0,0,0.015); }
        tr:hover td { background-color: rgba(16, 86, 130, 0.08) !important; transition: background 0.1s; }
        [data-theme="dark"] tr:hover td { background-color: rgba(56, 189, 248, 0.15) !important; }
        
        footer { margin-top: 5px; padding: 5px; text-align: center; font-size: 9px; color: var(--text-light); border-top: 1px solid var(--border); }
        .footer-disclaimer { display: block; font-style: italic; margin-bottom: 2px; font-size: 9px; }
        .footer-legal { color: var(--primary); font-weight: 700; font-size: 9px; }
        
        @media (max-width: 1024px) { .dashboard-wrapper { flex-direction: column; } .sidebar { width: 100%; height: auto; border-right: none; } .main-content { width: 100%; } .kpi-section { flex-direction: column; } }
        
        .custom-tooltip { position: fixed; background: var(--tooltip-bg); color: var(--tooltip-text); padding: 8px 12px; border-radius: 6px; font-size: 11px; font-weight: 500; pointer-events: none; z-index: 1000; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid var(--border); max-width: 250px; display: none; }
        .spinner-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255,255,255,0.5); display: flex; align-items: center; justify-content: center; z-index: 50; backdrop-filter: blur(1px); border-radius: 12px; }
        [data-theme="dark"] .spinner-overlay { background: rgba(15, 23, 42, 0.5); }
        .spinner { width: 30px; height: 30px; border: 3px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin 0.8s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
    """

def get_js(data_json, tipos, country_order, ui_texts, data_dict, fecha_actualizacion):
    """
    Retorna el bloque de JavaScript con la lógica del dashboard.
    Incluye lógica de filtrado, actualización de gráficos Plotly,
    generación de tablas y exportación.

    Args:
        data_json (str): Datos procesados en formato JSON.
        tipos (list): Lista de tipos de socios.
        country_order (list): Lista de países ordenada jerárquicamente.
        ui_texts (dict): Diccionario de textos UI.
        data_dict (dict): Diccionario de traducción de datos.
        fecha_actualizacion (str): Fecha formateada.

    Returns:
        str: Bloque HTML <script> completo.
    """
    return f"""
    <script>
        const rawData = {data_json};
        // ORDEN ESTRICTO: Fundador, Regional No Fundador, Extrarregional (Valores exactos de SOCIO_MAP)
        const tiposOrdered = ['Fundador', 'Regional No Fundador', 'Extrarregional'];
        const tiposOpts = ['Todos', ...tiposOrdered];
        const countryOrder = {json.dumps(country_order)};
        const i18n = {json.dumps(ui_texts)};
        const dataDict = {json.dumps(data_dict)};
        
        let state = {{ tipo: 'Todos', pais: 'Todos' }};
        let currentLang = 'es';
        let showIntervals = true;
        
        function init() {{
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
            if(savedTheme === 'dark') document.getElementById('btn-theme').classList.add('active');
            renderFilters();
            updateDashboard();
            window.addEventListener('resize', function() {{ Plotly.Plots.resize('chart'); }});
            setTimeout(() => {{ Plotly.Plots.resize('chart'); }}, 100);
            
            if(currentLang === 'en') document.getElementById('btn-lang').classList.add('active');
        }}
        
        function t(key) {{ return i18n[currentLang][key] || key; }}
        function trData(txt) {{ return currentLang === 'es' ? txt : (dataDict[txt] || txt); }}

        function toggleTheme() {{
            const current = document.documentElement.getAttribute('data-theme');
            const newTheme = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            document.getElementById('btn-theme').classList.toggle('active');
            updateDashboard();
        }}

        function toggleLang() {{
            currentLang = currentLang === 'es' ? 'en' : 'es';
            document.getElementById('btn-lang').classList.toggle('active');
            
            const map = {{
                'lbl-title': 'title', 'lbl-subtitle': 'subtitle', 'lbl-sidebar': 'sidebar',
                'lbl-type': 'type', 'lbl-country': 'country',
                'btn-reset-txt': 'restore', 'lbl-context': 'context', 'lbl-last-real': 'last_real',
                'lbl-proj': 'proj', 'lbl-yoy_title': 'yoy_title', 'lbl-chart-title': 'chart_title',
                'lbl-table-title': 'table_title', 'lbl-footer': 'footer', 
                'btn-export': 'export', 'lbl-scenario': showIntervals ? 'scenario_on' : 'scenario_off',
                'lbl-theme-light': 'txt_theme_light', 'lbl-theme-dark': 'txt_theme_dark',
                'lbl-lang-es': 'txt_lang_es', 'lbl-lang-en': 'txt_lang_en'
            }};
            Object.keys(map).forEach(id => {{
                const el = document.getElementById(id);
                if(el) el.innerText = t(map[id]);
            }});

            // Special handling for HTML rights with dynamic year
            const elRights = document.getElementById('lbl-rights');
            if(elRights) {{
                let rTxt = t('rights');
                rTxt = rTxt.replace('{{year}}', new Date().getFullYear());
                elRights.innerHTML = rTxt; // Use innerHTML for line breaks
            }}
            
            document.getElementById('lbl-update').innerText = t('update') + ' {fecha_actualizacion}';
            document.getElementById('lbl-scenario').innerText = showIntervals ? t('scenario_on') : t('scenario_off');
            
            document.getElementById('lbl-theme-light').textContent = t('txt_theme_light');
            document.getElementById('lbl-theme-dark').textContent = t('txt_theme_dark');
            document.getElementById('lbl-lang-es').textContent = t('txt_lang_es');
            document.getElementById('lbl-lang-en').textContent = t('txt_lang_en');
            document.getElementById('btn-snap-txt').textContent = t('txt_snap');
            document.getElementById('btn-pdf-txt').textContent = t('txt_pdf');
            
            renderFilters();
            updateDashboard();
        }}

        function toggleIntervals() {{
            showIntervals = !showIntervals;
            document.getElementById('btn-intervals').classList.toggle('active');
            document.getElementById('lbl-scenario').innerText = showIntervals ? t('scenario_on') : t('scenario_off');
            updateDashboard();
        }}

        function exportCSV() {{
            let csv = [];
            const rows = document.querySelectorAll("table tr");
            rows.forEach(row => {{
                const cols = row.querySelectorAll("td, th");
                let rowData = [];
                cols.forEach(col => rowData.push('"' + col.innerText.replace(/\\n/g,'') + '"'));
                csv.push(rowData.join(","));
            }});
            const blob = new Blob(["\\uFEFF"+csv.join("\\n")], {{type: "text/csv;charset=utf-8;"}});
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = "bcie_projections.csv";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }}

        function resetFilters() {{
            state = {{ tipo: 'Todos', pais: 'Todos' }};
            renderFilters();
            updateDashboard();
        }}

        function sortCountries(a, b) {{
            const idxA = countryOrder.findIndex(c => c.toUpperCase() === a.toUpperCase());
            const idxB = countryOrder.findIndex(c => c.toUpperCase() === b.toUpperCase());
            if (idxA !== -1 && idxB !== -1) return idxA - idxB;
            if (idxA !== -1) return -1; 
            if (idxB !== -1) return 1;
            return a.localeCompare(b);
        }}

        function sortTypes(a, b) {{
            const idxA = tiposOrdered.indexOf(a);
            const idxB = tiposOrdered.indexOf(b);
            // Si alguno no está en la lista (ej 'Todos' o desconocido), va al final o se maneja
            if (idxA !== -1 && idxB !== -1) return idxA - idxB;
            if (idxA !== -1) return -1;
            if (idxB !== -1) return 1;
            return a.localeCompare(b);
        }}

        function renderFilters() {{
            renderButtons('tipo-container', tiposOpts, 'tipo');
            updateCountryButtons();
        }}

        function showSpinner() {{ document.getElementById('spinner-chart').style.display = 'flex'; }}
        function hideSpinner() {{ document.getElementById('spinner-chart').style.display = 'none'; }}
        
        function scheduleUpdate() {{
            showSpinner();
            setTimeout(() => {{ updateDashboard(); hideSpinner(); }}, 10);
        }}

        function renderButtons(containerId, options, key) {{
            const container = document.getElementById(containerId);
            container.innerHTML = '';
            const allTxt = t('all');
            options.forEach(opt => {{
                const label = opt === 'Todos' ? allTxt : trData(opt);
                const btn = document.createElement('button');
                btn.className = `btn-vertical ${{state[key] === opt ? 'active' : ''}}`;
                btn.innerText = label;
                btn.onclick = () => {{
                    state[key] = opt;
                    Array.from(container.children).forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    if (key !== 'pais') updateCountryButtons();
                    scheduleUpdate();
                }};
                container.appendChild(btn);
            }});
        }}

        function takeScreenshot() {{
            const btnSnap = document.getElementById('btn-snap-txt');
            const originalText = btnSnap.textContent;
            btnSnap.textContent = '...';
            
            html2canvas(document.body, {{ useCORS: true, logging: true }}).then(canvas => {{
                const link = document.createElement('a');
                link.download = 'bcie_dashboard_snapshot.png';
                link.href = canvas.toDataURL('image/png');
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                btnSnap.textContent = originalText;
            }}).catch(err => {{
                console.error('Error taking snapshot:', err);
                alert('Error: ' + err.message);
                btnSnap.textContent = originalText;
            }});
        }}

        function generatePDF() {{
            const btnPdf = document.getElementById('btn-pdf-txt');
            const originalText = btnPdf.textContent;
            btnPdf.textContent = '...';
            
            const {{ jsPDF }} = window.jspdf;
            html2canvas(document.body, {{ useCORS: true, scale: 2 }}).then(canvas => {{
                const imgData = canvas.toDataURL('image/png');
                const pdf = new jsPDF('p', 'mm', 'a4');
                const pdfWidth = pdf.internal.pageSize.getWidth();
                const pdfHeight = pdf.internal.pageSize.getHeight();
                const imgWidth = canvas.width;
                const imgHeight = canvas.height;
                const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
                
                const imgX = (pdfWidth - imgWidth * ratio) / 2;
                const imgY = 10;
                
                pdf.addImage(imgData, 'PNG', imgX, imgY, imgWidth * ratio, imgHeight * ratio);
                pdf.save('bcie_dashboard_report.pdf');
                btnPdf.textContent = originalText;
            }}).catch(err => {{
                console.error('Error generating PDF:', err);
                alert('Error generating PDF: ' + err.message);
                btnPdf.textContent = originalText;
            }});
        }}

        function updateCountryButtons() {{
            const container = document.getElementById('pais-container');
            container.innerHTML = '';
            let filtered = rawData;
            if (state.tipo !== 'Todos') filtered = filtered.filter(d => d['Tipo de Socio'] === state.tipo);
            
            const countries = [...new Set(filtered.map(d => d['País']))];
            countries.sort(sortCountries);
            const options = ['Todos', ...countries];
            const allTxt = t('all');

            options.forEach(opt => {{
                const label = opt === 'Todos' ? allTxt : trData(opt);
                const btn = document.createElement('button');
                btn.className = `btn-vertical ${{state.pais === opt ? 'active' : ''}}`;
                btn.innerText = label;
                btn.onclick = () => {{
                    state.pais = opt;
                    Array.from(container.children).forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    scheduleUpdate();
                }};
                container.appendChild(btn);
            }});
        }}

        function updateDashboard() {{
            let data = rawData;
            if (state.tipo !== 'Todos') data = data.filter(d => d['Tipo de Socio'] === state.tipo);
            if (state.pais !== 'Todos') data = data.filter(d => d['País'] === state.pais);

            const realMap = {{}}, predMap = {{}};

            data.forEach(d => {{
                const date = d['Fecha_Str'];
                if (d['Datos'] === 'Reales') {{
                    if (!realMap[date]) realMap[date] = {{ val: 0, year: d['Año'], date: date }};
                    realMap[date].val += (d['Monto Total (USD)'] || 0);
                }} else if (d['Datos'] === 'Predicción') {{
                    if (!predMap[date]) predMap[date] = {{ val: 0, low: 0, high: 0, year: d['Año'], date: date }};
                    predMap[date].val += (d['Predicción'] || 0);
                    predMap[date].low += (d['Inferior 80%'] || 0);
                    predMap[date].high += (d['Superior 80%'] || 0);
                }}
            }});

            let realArr = Object.values(realMap).sort((a,b) => new Date(a.date) - new Date(b.date));
            let predArr = Object.values(predMap).sort((a,b) => new Date(a.date) - new Date(b.date));
            let maxRealYear = realArr.length > 0 ? realArr[realArr.length - 1].year : 0;
            predArr = predArr.filter(p => p.year > maxRealYear);

            updateKPIs(realArr, predArr);
            updateChart(realArr, predArr);
            const tableData = data.filter(d => d['Datos'] === 'Predicción' && d['Año'] > maxRealYear);
            renderTable(tableData);
        }}

        function formatMoney(val) {{
            if (!val) return '-';
            return '$' + val.toLocaleString('en-US', {{maximumFractionDigits:0}});
        }}

        function formatCompact(val) {{
            if (!val) return '-';
            if (val >= 1000000000) return '$' + (val / 1000000000).toFixed(2) + 'B';
            if (val >= 1000000) return '$' + (val / 1000000).toFixed(1) + 'M';
            return '$' + val.toLocaleString('en-US', {{maximumFractionDigits:0}});
        }}

        function updateKPIs(realArr, predArr) {{
            const lastReal = realArr.length ? realArr[realArr.length-1] : null;
            const lastPred = predArr.length ? predArr[predArr.length-1] : null;
            let growthHtml = '-';
            if (lastReal && lastPred) {{
                const g = ((lastPred.val / lastReal.val) - 1) * 100;
                const color = g >= 0 ? '#10b981' : '#ef4444';
                growthHtml = `<span style="color:${{color}}">${{g.toFixed(1)}}%</span>`;
            }}
            // 1. GENERAR HTML DE TARJETAS HORIZONTALES
            let yoyHtml = '';
            if (predArr.length > 0) {{
                predArr.forEach((row, i) => {{
                    // Calcular porcentaje respecto al año anterior
                    const prevVal = i > 0 ? predArr[i-1].val : (lastReal ? lastReal.val : 0);
                    let pctStr = '-';
                    let colorStyle = 'color: var(--text-light)'; // Por defecto
                    
                    if (prevVal > 0) {{
                        const pct = ((row.val / prevVal) - 1) * 100;
                        pctStr = (pct > 0 ? '+' : '') + pct.toFixed(1) + '%';
                        // Color verde o rojo directo con variable para consistencia
                        colorStyle = pct >= 0 ? 'color: #10b981;' : 'color: #ef4444;';
                    }}
                    
                    // Tarjeta individual estilo claro
                    yoyHtml += `
                        <div class="yoy-single-card">
                            <div class="yoy-year-text">${{row.year}}</div>
                            <div class="yoy-val-text">${{formatMoney(row.val)}}</div>
                            <div class="yoy-pct-text" style="${{colorStyle}}">${{pctStr}}</div>
                        </div>
                    `;
                }});
            }}

            let ctxParts = [];
            if (state.pais !== 'Todos') ctxParts.push(trData(state.pais));
            if (state.tipo !== 'Todos') ctxParts.push(trData(state.tipo));
            const ctx = ctxParts.length > 0 ? ctxParts.join(' · ') : (currentLang==='es'?'Global':'Global');

            // 2. INYECTAR EL HTML FINAL
            // Observa que el cuarto bloque usa la clase .card-yoy que definimos arriba
            document.getElementById('kpi-section').innerHTML = `
                <div class="kpi-card">
                    <div class="kpi-label">${{t('context')}}</div>
                    <div class="kpi-value" style="font-size:18px;">${{ctx}}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">${{t('last_real')}} (${{lastReal?.year || '-'}})</div>
                    <div class="kpi-value">${{formatMoney(lastReal?.val)}}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">${{t('proj')}} (${{lastPred?.year || '-'}})</div>
                    <div class="kpi-value">${{formatMoney(lastPred?.val)}}</div>
                    <div class="kpi-growth">${{growthHtml}}</div>
                </div>
                
                <div class="card-yoy">
                    <div class="yoy-header">${{t('yoy_title')}}</div>
                    <div class="yoy-scroll-area">
                        ${{yoyHtml}}
                    </div>
                </div>
            `;
        }}

        function updateChart(realArr, predArr) {{
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            const colors = {{ text: isDark ? '#f1f5f9' : '#1e293b', grid: isDark ? '#334155' : '#f1f5f9', line: isDark ? '#f1f5f9' : '#1e293b' }};
            
            const tooltipBg = isDark ? '#1e293b' : '#ffffff';
            const tooltipText = isDark ? '#f1f5f9' : '#1e293b';
            const gridColor = isDark ? '#334155' : '#e2e8f0';

            const xReal = realArr.map(r => r.date);
            const yReal = realArr.map(r => r.val);
            const xPred = predArr.map(r => r.date);
            const yPred = predArr.map(r => r.val);
            
            if (xReal.length > 0 && xPred.length > 0) {{
                const lastRealDate = xReal[xReal.length - 1];
                const lastRealVal = yReal[yReal.length - 1];
                xPred.unshift(lastRealDate);
                yPred.unshift(lastRealVal);
            }}
            
            let yHigh = predArr.map(r => r.high);
            let yLow = predArr.map(r => r.low);
            if (xReal.length > 0 && xPred.length > 0) {{
                    yHigh.unshift(yReal[yReal.length-1]);
                    yLow.unshift(yReal[yReal.length-1]);
            }}

            const traces = [];
            if(showIntervals) {{
                traces.push({{
                    x: xPred.concat([...xPred].reverse()), y: yHigh.concat([...yLow].reverse()),
                    fill: "toself", fillcolor: "rgba(255, 0, 0, 0.08)", line: {{color: "transparent", shape: 'spline', smoothing: 1.3}}, name: "80%", hoverinfo: "skip", showlegend: true
                }});
            }}
            traces.push({{ x: xReal, y: yReal, mode: 'lines+markers', name: t('chart_hist'), line: {{color: colors.line, shape: 'spline', smoothing: 1.3, width: 2.5}}, marker: {{symbol: 'circle', size: 7, color: colors.line}} }});
            traces.push({{ x: xPred, y: yPred, mode: 'lines', name: t('chart_pred'), line: {{color: '#ef4444', dash: 'dot', shape: 'spline', smoothing: 1.3, width: 2.5}} }});

            const layout = {{
                margin: {{t:20, l:60, r:30, b:40}}, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', autosize: true,
                font: {{ family: 'Inter, sans-serif' }},
                xaxis: {{title: '', tickfont: {{color: colors.text}}, gridcolor: colors.grid, zeroline: false, gridwidth: 0.5, griddash: 'dot'}}, 
                yaxis: {{
                    title: {{text: 'USD', font: {{color: colors.text}}}}, 
                    tickfont: {{color: colors.text}}, 
                    gridcolor: colors.grid,
                    zeroline: false,
                    gridwidth: 0.5,
                    griddash: 'dot'
                }},
                legend: {{orientation: 'h', y: 1.1, x: 0.5, xanchor: 'center', font: {{color: colors.text}}}}, 
                hovermode: 'x unified',
                hoverlabel: {{ bgcolor: tooltipBg, font: {{color: tooltipText}}, bordercolor: gridColor }}
            }};
            Plotly.newPlot('chart', traces, layout, {{responsive: true}});
        }}

        function renderTable(tableData) {{
            const div = document.getElementById('table-html');
            if (tableData.length === 0) {{ div.innerHTML = '<p style="text-align:center; padding:20px; color:#999">No data</p>'; return; }}
            const years = [...new Set(tableData.map(d => d['Año']))].sort();
            
            const typeMap = {{}};
            tableData.forEach(d => {{
                const t = d['Tipo de Socio'] || 'Otro';
                const c = d['País'] || 'Otro';
                const y = d['Año'];
                const val = d['Predicción'] || 0;
                
                if (!typeMap[t]) typeMap[t] = {{}};
                if (!typeMap[t][c]) typeMap[t][c] = {{}};
                if (!typeMap[t][c][y]) typeMap[t][c][y] = 0;
                
                typeMap[t][c][y] += val;
            }});

            let html = '<table><thead><tr>';
            html += `<th>${{t('type')}}</th><th>${{t('country')}}</th>`;
            years.forEach(y => html += `<th>${{y}}</th>`);
            html += '</tr></thead><tbody>';
            
            let grandTotal = new Array(years.length).fill(0);
            
            // CALCULAR MAXIMOS POR AÑO PARA NORMALIZAR BARRAS (0-90%)
            const maxPerYear = {{}};
            years.forEach(y => {{
                let maxVal = 0;
                Object.keys(typeMap).forEach(t => {{
                    Object.keys(typeMap[t]).forEach(c => {{
                        const v = typeMap[t][c][y] || 0;
                        if(v > maxVal) maxVal = v;
                    }});
                }});
                maxPerYear[y] = maxVal > 0 ? maxVal : 1;
            }});

            Object.keys(typeMap).sort(sortTypes).forEach(typeKey => {{
                let typeSubtotal = new Array(years.length).fill(0);
                Object.keys(typeMap[typeKey]).sort().forEach(countryKey => {{
                    html += `<tr><td class="cell-left" data-k="type" data-v="${{typeKey}}">${{trData(typeKey)}}</td><td class="cell-left" data-k="country" data-v="${{countryKey}}">${{trData(countryKey)}}</td>`;
                    years.forEach((y, i) => {{
                        const val = typeMap[typeKey][countryKey][y] || 0;
                        typeSubtotal[i] += val;
                        grandTotal[i] += val;
                        
                        // Barra suave con ancho proporcional max 90%
                        const pct = (val / maxPerYear[y]) * 90;
                        const barHtml = val > 0 ? `<div class="cell-bar-container" style="width:${{pct}}%;"></div>` : '';
                        
                        html += `<td style="position:relative;">${{barHtml}}${{formatCompact(val)}}</td>`;
                    }});
                    html += '</tr>';
                }});
                html += `<tr class="row-subtotal"><td colspan="2" style="text-align:right">${{t('subtotal')}} ${{trData(typeKey)}}</td>`;
                typeSubtotal.forEach(v => html += `<td>${{formatCompact(v)}}</td>`);
                html += '</tr>';
            }});

            html += `<tr class="row-total"><td colspan="2" style="text-align:right">${{t('total')}}</td>`;
            grandTotal.forEach(v => html += `<td>${{formatCompact(v)}}</td>`);
            html += '</tr></tbody></table>';
            
            div.innerHTML = html;
            
            const cells = div.querySelectorAll('td');
            const tooltip = document.getElementById('custom-tooltip');
            cells.forEach(td => {{
                td.addEventListener('mouseenter', (e) => {{
                    const rawTxt = td.innerText;
                    if(rawTxt === '-' || rawTxt.includes('Total') || rawTxt.includes('Subtotal')) return;
                    
                    let tooltipContent = rawTxt; 
                    
                    if(rawTxt.includes('$')) {{
                            tooltipContent = rawTxt;
                    }} 
                    else {{
                            const k = td.getAttribute('data-k');
                            const v = td.getAttribute('data-v');
                            if(k && v) tooltipContent = trData(v);
                    }}

                    tooltip.innerText = tooltipContent;
                    tooltip.style.display = 'block';
                    
                    tooltip.style.left = e.clientX + 10 + 'px'; 
                    tooltip.style.top = e.clientY + 10 + 'px';
                }});
                td.addEventListener('mousemove', (e) => {{
                    tooltip.style.left = e.clientX + 10 + 'px';
                    tooltip.style.top = e.clientY + 10 + 'px';
                }});
                td.addEventListener('mouseleave', () => {{
                    tooltip.style.display = 'none';
                }});
            }});
        }}

        window.onload = init;
    </script>
    """
