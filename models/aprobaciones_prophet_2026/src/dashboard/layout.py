"""
Módulo Constructor de HTML

Este módulo es el responsable de ensamblar la estructura final del archivo HTML.
No realiza cálculos numéricos, solo orquesta la inyección de estilos (CSS),
lógica (JS) y la estructura del DOM (HTML).
"""

from datetime import datetime
from src.dashboard.assets import get_css, get_js
from src.dashboard.config import COUNTRY_ORDER, DATA_DICT, UI_TEXTS, UI_HIST_TEXTS
import json
import pandas as pd

def get_dashboard_html(df_unico):
    """Genera el código HTML completo del tablero de PREDICCIONES (Prophet)."""
    cols = ['Fecha_Str', 'Año', 'País', 'Tipo de Socio', 'Sector Institucional', 'Datos', 'Monto Total (USD)', 'Predicción', 'Inferior 80%', 'Superior 80%']
    data_json = df_unico[cols].fillna(0).to_json(orient='records')
    
    tipos = sorted(list(df_unico['Tipo de Socio'].dropna().unique()))
    
    now = datetime.now()
    fecha_actualizacion = now.strftime("%d/%m/%Y %H:%M")
    anio_actual = now.year
    
    css = get_css()
    js = get_js(data_json, tipos, COUNTRY_ORDER, UI_TEXTS, DATA_DICT, fecha_actualizacion)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tablero Estratégico BCIE</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        {css}
    </head>
    <body>
        <div id="custom-tooltip" class="custom-tooltip"></div>
        
        <nav class="top-nav">
            <div class="header-title">
                <h1 id="lbl-title">Análisis de Proyección de Aprobaciones de Datos Abiertos del BCIE</h1>
                <div class="subtitle" id="lbl-subtitle">Modelo de Inteligencia Artificial (Prophet) • Escenarios 2026-2030</div>
            </div>
            <div class="nav-controls">
                <div class="update-badge" id="lbl-update">Datos Actualizados: {fecha_actualizacion}</div>
                <div class="toggle-wrapper">
                    <div class="toggle-switch" id="btn-theme" onclick="toggleTheme()" title="Cambiar Tema">
                        <div class="toggle-knob"></div>
                        <span class="toggle-icon">☀️</span>
                        <span class="toggle-icon">🌙</span>
                    </div>
                    <div class="toggle-labels">
                        <span id="lbl-theme-light">Claro</span>
                        <span id="lbl-theme-dark">Oscuro</span>
                    </div>
                </div>
                <div class="toggle-wrapper">
                    <div class="toggle-switch" id="btn-lang" onclick="toggleLang()" title="Cambiar Idioma">
                        <div class="toggle-knob"></div>
                    </div>
                    <div class="toggle-labels">
                        <span id="lbl-lang-es">Esp</span>
                        <span id="lbl-lang-en">Ing</span>
                    </div>
                </div>
            </div>
        </nav>

        <div class="dashboard-wrapper">
            <aside class="sidebar">
                <div class="sidebar-title" id="lbl-sidebar">Filtros de Control</div>
                <div class="filter-group"><span class="filter-label" id="lbl-type">Tipo de Socio</span><div id="tipo-container"></div></div>
                <div class="filter-group"><span class="filter-label" id="lbl-country">País</span><div id="pais-container"></div></div>
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--border);">
                    <button class="btn-reset" onclick="resetFilters()">
                        <span id="btn-reset-txt">↺ RESTAURAR</span>
                    </button>
                </div>
                <!-- THESE BUTTONS ARE NOT NEEDED HERE FOR STRATEGIC DASH AS IT HAS ITS OWN JS IN ASSETS.PY 
                     BUT WE LEAVE THEM IF USER WANTS THEM FOR SYNC. 
                     HOWEVER, STRATEGIC DASHBOARD USES A DIFFERENT LAYOUT.PY?
                     WAIT, layout.py IS FOR BOTH?
                     get_dashboard_html -> predictive (uses get_js)
                     get_executive_html -> executive (has embedded js)
                -->
            </aside>

            <main class="main-content">
                <div class="kpi-section" id="kpi-section"></div>
                
                <div class="charts-wrapper">
                    <div class="card-fill section-chart">
                        <div class="card-header-compact">
                            <h3 class="card-title-compact" id="lbl-chart-title">Tendencia Histórica y Proyección</h3>
                            <button class="btn-action btn-toggle active" id="btn-intervals" onclick="toggleIntervals()">
                                <span id="lbl-scenario">Ver Intervalos</span>
                            </button>
                        </div>
                        <div id="chart" style="position: relative; flex: 1; width: 100%; height: 100%;">
                            <div id="spinner-chart" class="spinner-overlay" style="display: none;"><div class="spinner"></div></div>
                        </div>
                    </div>

                    <div class="card-fill section-table">
                        <div class="card-header-compact">
                            <h3 class="card-title-compact" id="lbl-table-title">Matriz Detallada de Pronósticos</h3>
                            <button class="btn-action btn-export" id="btn-export" onclick="exportCSV()">Exportar CSV</button>
                        </div>
                        <div id="table-html" class="table-container" style="flex:1; overflow:auto;"></div>
                    </div>
                </div>

                <footer class="footer-compact" style="grid-column: 1 / -1; margin-top: 10px;">
                    <div class="footer-disclaimer" id="lbl-footer">Este tablero presenta proyecciones financieras basadas en datos históricos auditados y modelos de machine learning. Los resultados reflejan un análisis estadístico basado en patrones históricos y no constituyen un compromiso financiero vinculante por parte del BCIE.</div>
                    <div class="footer-legal" id="lbl-rights">© {anio_actual} | UNIR–BCIE | Trabajo de Colaboración Académica | Proyecto Final de Máster | Equipo 03-D | Desarrollado por Edgar García, Norman Sabillón y Wilson Aguilar | Todos los derechos reservados.</div>
                </footer>
            </main>
        </div>
        {js}
    </body>
    </html>
    """
    return html_content

def formatInteger(num):
    if pd.isna(num): return "0"
    return "{:,.0f}".format(num)

def formatCompact(val):
    if val >= 1e9: return f"USD {val/1e9:.2f} B"
    if val >= 1e6: return f"USD {val/1e6:.1f} M"
    return f"USD {val:,.0f}"

def get_executive_html(data_processed, fecha_actualizacion, anio_actual):
    """Construye el HTML para el Dashboard EJECUTIVO (Histórico) con layout similar al predictivo."""
    
    json_year = data_processed['year'].to_json(orient='records')
    json_sector = data_processed['sector'].to_json(orient='records')
    json_tipo = data_processed['tipo'].to_json(orient='records')
    json_pais = data_processed['pais'].to_json(orient='records')
    json_kpis = json.dumps(data_processed['kpis'])
    
    css = get_css()
    
    # Obtener el ultimo año de los datos
    years = data_processed['year']['Año'].tolist()
    yr_max = max(years) if years else anio_actual
    
    js = f"""
    <script>
        const dYear={json_year}, dSector={json_sector}, dTipo={json_tipo}, dPais={json_pais}, kpis={json_kpis}, txt={json.dumps(UI_HIST_TEXTS)};
        const dataDict={json.dumps(DATA_DICT)};
        let curLang='es';
        let socMetric='monto', couMetric='monto';

        function fmt(n){{return '$'+n.toLocaleString('en-US',{{maximumFractionDigits:0}})}}
        
        function init(){{
            const st=localStorage.getItem('theme')||'light'; document.documentElement.setAttribute('data-theme',st);
            if(st==='dark') document.getElementById('btn-theme').classList.add('active');
            if(curLang==='en') document.getElementById('btn-lang').classList.add('active');
            plot(); updT(); tbl();
        }}
        
        function toggleTheme() {{
            const current = document.documentElement.getAttribute('data-theme');
            const newTheme = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            document.getElementById('btn-theme').classList.toggle('active');
            plot(); // Redraw charts
        }}

        function toggleLang() {{
            curLang = curLang === 'es' ? 'en' : 'es';
            document.getElementById('btn-lang').classList.toggle('active');
            plot(); updT(); tbl();
        }}
        
        function toggleMetric(chart) {{
            const current = chart === 'soc' ? socMetric : couMetric;
            const newState = current === 'monto' ? 'cant' : 'monto';
            if(chart === 'soc') socMetric = newState; else couMetric = newState;
            
            const btn = document.getElementById(chart === 'soc' ? 'btn-soc-metric' : 'btn-cou-metric');
            if(newState === 'monto') {{
                btn.classList.remove('cant'); btn.classList.add('monto');
            }} else {{
                btn.classList.remove('monto'); btn.classList.add('cant');
            }}
            plot();
        }}

        function updT(){{
            const t=txt[curLang];
            const ids={{'lbl-main':t.main_title,'lbl-sub':t.sub_title,'lbl-kt':t.kpi_total,'lbl-kc':t.kpi_count,'lbl-ka':t.kpi_avg,
                       'lbl-ce':t.card_evolution,'lbl-cs':t.card_sector,'lbl-cp':t.card_partner,'lbl-cc':t.card_country,'lbl-th':t.card_table,
                       'lbl-footer':t.footer, 'btn-snap-txt':t.txt_snap, 'btn-pdf-txt':t.txt_pdf,
                       'lbl-th-year':t.col_year, 'lbl-th-amount':t.col_amount, 'lbl-th-count':t.col_count,
                       'lbl-th-avg':t.col_avg, 'lbl-th-var':t.col_var}};
            for(let k in ids) {{
                const el = document.getElementById(k);
                if(el) el.innerHTML=ids[k];
            }}
            
            // Special handling for rights with HTML and Year
            const elRights = document.getElementById('lbl-rights');
            if(elRights) {{
                let rTxt = t.rights;
                rTxt = rTxt.replace('{{year}}', new Date().getFullYear());
                elRights.innerHTML = rTxt;
            }}
            // Header controls text updates
            document.getElementById('lbl-update').innerText = t.update + ' {fecha_actualizacion}';
            document.getElementById('lbl-theme-light').innerText = t.txt_theme_light || 'Claro';
            document.getElementById('lbl-theme-dark').innerText = t.txt_theme_dark || 'Oscuro';
            document.getElementById('lbl-lang-es').innerText = t.txt_lang_es || 'Esp';
            document.getElementById('lbl-lang-en').innerText = t.txt_lang_en || 'Ing';

            // Translate Country Chart Labels (Robust)
            const cCou = document.getElementById('c-cou');
            if(cCou && cCou.data && t.countries) {{
                // Store original labels on first run to avoid lost translation mapping
                if(!cCou._originalLabels && cCou.data[0] && cCou.data[0].x) {{
                    cCou._originalLabels = [...cCou.data[0].x]; 
                }}
                
                if(cCou._originalLabels) {{
                    const newData = cCou.data.map((trace, i) => {{
                        if(trace.x) {{
                            trace.x = cCou._originalLabels.map(lbl => t.countries[lbl] || lbl);
                        }}
                        return trace;
                    }});
                    // Reduce bargap dynamically if needed (0.1 gives more space for bars/labels)
                    const newLayout = {{...cCou.layout, bargap: 0.1}};
                    Plotly.react(cCou, newData, newLayout);
                }}
            }}

            // Translate Donut Chart Center Text
            // Translate Donut Chart Center Text
            const cSecMonto = document.getElementById('c-sec-monto');
            if(cSecMonto) {{
                Plotly.relayout(cSecMonto, {{'annotations[0].text': t.lbl_amount || 'Monto'}});
            }}

            const cSecCant = document.getElementById('c-sec-cant');
            if(cSecCant) {{
                Plotly.relayout(cSecCant, {{'annotations[0].text': t.lbl_quantity || 'Cantidad'}});
            }}
        }}
        
        async function takeScreenshot() {{
            const btnSnap = document.getElementById('btn-snap-txt');
            const originalText = btnSnap.textContent;
            btnSnap.textContent = '...';
            
            try {{
                const canvas = await html2canvas(document.body, {{ useCORS: true, logging: false }});
                const link = document.createElement('a');
                link.download = 'Dashboard_Exec_' + new Date().toISOString().slice(0,10) + '.png';
                link.href = canvas.toDataURL('image/png');
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                btnSnap.textContent = originalText;
            }} catch(err) {{
                console.error('Error taking snapshot:', err);
                alert('Error: ' + err.message);
                btnSnap.textContent = originalText;
            }}
        }}

        async function generatePDF() {{
            const btnPdf = document.getElementById('btn-pdf-txt');
            const originalText = btnPdf.textContent;
            btnPdf.textContent = '...';
            
            try {{
                const {{ jsPDF }} = window.jspdf;
                // Capture document body
                const canvas = await html2canvas(document.body, {{ useCORS: true, scale: 2 }});
                const imgData = canvas.toDataURL('image/png');
                
                // Landscape A4
                const pdf = new jsPDF('l', 'mm', 'a4'); 
                
                const pdfWidth = pdf.internal.pageSize.getWidth();
                const pdfHeight = pdf.internal.pageSize.getHeight();
                const imgWidth = canvas.width;
                const imgHeight = canvas.height;
                
                // Calculate Ratio to FIT PAGE without distortion
                const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
                const imgX = (pdfWidth - imgWidth * ratio) / 2;
                const imgY = 10; // Top margin
                
                pdf.addImage(imgData, 'PNG', imgX, imgY, imgWidth * ratio, imgHeight * ratio);
                pdf.save('Report_Exec_' + new Date().toISOString().slice(0,10) + '.pdf');
                btnPdf.textContent = originalText;
            }} catch(e) {{ 
                console.error("PDF error:", e); 
                alert("Error generating PDF: " + e.message); 
                btnPdf.textContent = originalText;
            }}
        }}
        
        function plot(){{
            const dark=document.documentElement.getAttribute('data-theme')==='dark';
            const cT=dark?'#f1f5f9':'#1e293b', cG=dark?'#334155':'#e2e8f0';
            // Brighter Blue for Dark Mode (#60a5fa), Standard Blue for Light Mode (#1e3a8a)
            const cBlue = dark ? '#60a5fa' : '#1e3a8a';
            const lay={{paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{{family:'Inter',color:cT}},margin:{{t:10,b:30,l:40,r:10}},xaxis:{{gridcolor:cG}},yaxis:{{gridcolor:cG}}}};
            
            
            // DUAL AXIS CHART FOR EVOLUTION
            const traceMonto = {{
                x: dYear.map(d=>d.Año), 
                y: dYear.map(d=>d.Monto), 
                name: txt[curLang].kpi_total, 
                type: 'scatter', 
                mode: 'lines+markers',
                line: {{color: '#34d399', width: 2, shape: 'spline'}},
                marker: {{symbol: 'circle', size: 6, color: dark?'#1e293b':'#ffffff', line: {{color: '#34d399', width: 2}}}}
            }};
            
            const traceCant = {{
                x: dYear.map(d=>d.Año), 
                y: dYear.map(d=>d.Cantidad), 
                name: txt[curLang].kpi_count, 
                yaxis: 'y2', 
                type: 'scatter', 
                mode: 'lines+markers',
                line: {{color: cBlue, width: 2, shape: 'spline'}},
                marker: {{symbol: 'circle', size: 6, color: dark?'#1e293b':'#ffffff', line: {{color: cBlue, width: 2}}}}
            }};

            const layEvo = {{
                ...lay,
                margin: {{t: 10, b: 30, l: 50, r: 50}},
                legend: {{orientation: 'h', x: 0.5, xanchor: 'center', y: -0.2}},
                xaxis: {{gridcolor: cG, zeroline: false}},
                yaxis: {{title: txt[curLang].axis_amount, gridcolor: cG, color: cT, rangemode: 'tozero'}},
                yaxis2: {{title: txt[curLang].axis_count, overlaying: 'y', side: 'right', gridcolor: 'transparent', color: cT, rangemode: 'tozero'}}
            }};
            
            Plotly.newPlot('c-evo', [traceMonto, traceCant], layEvo, {{responsive:true}});
            
            
            // SECTOR CHART SEGURO (Dual Donuts + Legend)
            const secColors = {{'Sector Público': '#7c3aed', 'Sector Privado': '#ef4444', 'Sector Financiero': '#3b82f6', 'Público': '#7c3aed', 'Privado': '#ef4444', 'Otro': '#9ca3af'}};
            const secLabels = {{'Sector Público': txt[curLang].lbl_sector_public, 'Sector Privado': txt[curLang].lbl_sector_private, 'Sector Financiero': txt[curLang].lbl_sector_financial}};
            
            try {{
                // Donut 1: Monto
                const traceM = {{
                    labels: dSector.map(d => d.Sector),
                    values: dSector.map(d => d.Monto),
                    type: 'pie',
                    hole: 0.7,
                    textinfo: 'percent',
                    textposition: 'outside',
                    hoverinfo: 'label+value+percent',
                    marker: {{colors: dSector.map(d => secColors[d.Sector] || '#cbd5e1')}},
                    showlegend: false,
                    title: {{text: 'Monto', position: 'middle center', font:{{size: 12, color:cT}}}}
                }};
                
                // Donut 2: Cantidad
                const traceC = {{
                    labels: dSector.map(d => d.Sector),
                    values: dSector.map(d => d.Cantidad),
                    type: 'pie',
                    hole: 0.7,
                    textinfo: 'percent',
                    textposition: 'outside',
                    hoverinfo: 'label+value+percent',
                    marker: {{colors: dSector.map(d => secColors[d.Sector] || '#cbd5e1')}},
                    showlegend: false,
                    title: {{text: 'Cantidad', position: 'middle center', font:{{size: 11, color:cT}}}}
                }};
                
                // Layout mas compacto pero igualado
                const layDonut = {{...lay, margin:{{t:35, b:35, l:35, r:35}}, showlegend:false}};
                
                Plotly.newPlot('c-sec-monto', [traceM], layDonut, {{responsive:true}});
                Plotly.newPlot('c-sec-cant', [traceC], layDonut, {{responsive:true}});
                
                // Generate Legend Safely (Left Border Style)
                let legH = '<div style="display:flex;flex-direction:column;gap:5px;align-items:center;width:100%;margin-top:5px">';
                dSector.forEach(d => {{
                    const c = secColors[d.Sector] || '#cbd5e1';
                    const montoS = (d.Monto!=null) ? d.Monto.toLocaleString('en-US',{{maximumFractionDigits:0}}) : '0';
                    const cantS = (d.Cantidad!=null) ? d.Cantidad.toLocaleString('en-US') : '0';
                    const avgVal = d.Cantidad > 0 ? d.Monto / d.Cantidad : 0;
                    const avgS = avgVal.toLocaleString('en-US',{{maximumFractionDigits:0}});
                    const label = secLabels[d.Sector] || d.Sector;
                    
                    const lblM = curLang === 'es' ? 'Monto' : 'Amount';
                    const lblA = curLang === 'es' ? 'Promedio' : 'Avg';

                    legH += `
                    <div style="display:flex;flex-direction:column;gap:1px;border-left:4px solid ${{c}};padding-left:10px;margin-bottom:12px;width:100%;align-items:flex-start">
                        <div style="font-weight:700;font-size:12px;color:var(--text-dark);margin-bottom:2px">${{label}}</div>
                        <div style="font-size:11px;color:var(--text-light);display:flex;gap:4px">
                            <span style="font-weight:600;min-width:55px">${{lblM}}:</span> 
                            <span style="font-weight:700;color:var(--primary)">USD ${{montoS}}</span>
                        </div>
                        <div style="font-size:11px;color:var(--text-light);display:flex;gap:4px">
                            <span style="font-weight:600;min-width:55px">${{txt[curLang].axis_count}}:</span> 
                            <span>${{cantS}}</span>
                        </div>
                        <div style="font-size:11px;color:var(--text-light);display:flex;gap:4px">
                            <span style="font-weight:600;min-width:55px">${{lblA}}:</span> 
                            <span>USD ${{avgS}}</span>
                        </div>
                    </div>`;
                }});
                legH += '</div>';
                const legEl = document.getElementById('leg-sec');
                if(legEl) legEl.innerHTML = legH;
                
            }} catch(e) {{
                console.error("Error drawing sector chart/legend:", e);
                const legEl = document.getElementById('leg-sec');
                if(legEl) legEl.innerHTML = '<div style="color:red;font-size:10px">Error loading legend</div>';
            }}

            // SOCIO CHART (Dynamic Metric)
            const isSocMonto = socMetric === 'monto';
            const dataSoc = dTipo.map(d => ({{
                label: (curLang === 'en' && dataDict[d.Tipo]) ? dataDict[d.Tipo] : d.Tipo,
                val: isSocMonto ? d.Monto : d.Cantidad,
                fmt: isSocMonto ? 'USD ' + (d.Monto!=null?d.Monto.toLocaleString('en-US',{{maximumFractionDigits:0}}):'0') : d.Cantidad.toLocaleString('en-US')
            }})).sort((a,b) => a.val - b.val);

            const traceSoc = {{
                y: dataSoc.map(d => d.label),
                x: dataSoc.map(d => d.val),
                type: 'bar',
                orientation: 'h',
                text: dataSoc.map(d => d.fmt),
                textposition: 'outside',
                cliponaxis: false,
                textfont: {{size: 11, color: cT}},
                hoverinfo: 'none',
                marker: {{color: isSocMonto ? '#10b981' : cBlue}}
            }};
            
            const maxValSoc = Math.max(...dataSoc.map(d => d.val)) || 1;
            const laySoc = {{
                ...lay, 
                margin: {{t: 30, b: 20, l: 150, r: 100}},
                xaxis: {{ showgrid: false, showticklabels: false, zeroline: false, range: [0, maxValSoc * 1.45] }},
                yaxis: {{automargin: true}}
            }};
            
            Plotly.newPlot('c-soc', [traceSoc], laySoc, {{responsive:true}});
            
            // COUNTRY CHART (Dynamic Metric)
            const formatCountry = (name) => {{
               // Translate if needed
               let n = (curLang === 'en' && dataDict[name]) ? dataDict[name] : name;
               
               // Formatting Logic
               n = n.toLowerCase().split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
               if(n.includes('Republica Dominicana') || n.includes('República Dominicana') || n.includes('Dominican Republic')) {{
                   return n.replace('Republica', 'Republica<br>').replace('República', 'República<br>').replace('Dominican', 'Dominican<br>');
               }}
               if(n.length > 15 && !n.includes('<br>')) {{
                   const parts = n.split(' ');
                   if(parts.length > 1) return parts[0] + '<br>' + parts.slice(1).join(' ');
               }}
               return n;
            }};

            const isCouMonto = couMetric === 'monto';
            const dataCou = dPais.map(d => ({{
                label: d.País,
                val: isCouMonto ? d.Monto : d.Cantidad,
                fmt: isCouMonto ? 'USD ' + (d.Monto!=null?d.Monto.toLocaleString('en-US',{{maximumFractionDigits:0}}):'0') : d.Cantidad.toLocaleString('en-US')
            }})).sort((a,b) => b.val - a.val).slice(0, 15);

            const traceCou = {{
                x: dataCou.map(d => formatCountry(d.label)),
                y: dataCou.map(d => d.val),
                type: 'bar',
                text: dataCou.map(d => d.fmt),
                textposition: 'outside',
                cliponaxis: false,
                textfont: {{size: 11, color: cT}},
                hoverinfo: 'none',
                marker: {{color: isCouMonto ? '#10b981' : cBlue}}
            }};
            
            const maxValCou = Math.max(...dataCou.map(d => d.val)) || 1;
            const layCou = {{
                ...lay,
                margin: {{t: 40, b: 40, l: 40, r: 40}},
                xaxis: {{tickangle: 0, tickfont: {{size: 11}}}},
                yaxis: {{
                    showgrid: false, 
                    showticklabels: false, 
                    zeroline: false,
                    range: [0, maxValCou * 1.25]
                }}
            }};

            Plotly.newPlot('c-cou', [traceCou], layCou, {{responsive:true}});
        }}
        
        function tbl(){{
            const t=txt[curLang];
            // Table with restricted header widths to force wrapping
            let h=`<table style="width:100%;margin:0 auto;border-collapse:collapse;font-size:11px"><thead><tr style="border-bottom:2px solid var(--border)">
            <th id="lbl-th-year" style="text-align:left;padding:8px 4px;color:var(--text-light)">${{t.col_year}}</th>
            <th id="lbl-th-amount" style="text-align:right;padding:8px 4px;color:var(--text-light)">${{t.col_amount}}</th>
            <th id="lbl-th-count" style="text-align:center;padding:8px 4px;color:var(--text-light)">${{t.col_count}}</th>
            <th id="lbl-th-avg" style="padding:8px 4px;text-align:right;color:var(--text-light);white-space:normal;max-width:100px;line-height:1.2">${{t.col_avg}}</th>
            <th id="lbl-th-var" style="padding:8px 4px;text-align:right;color:var(--text-light);white-space:normal;max-width:120px;line-height:1.2">${{t.col_var}}</th>
            </tr></thead><tbody>`;
            const sorted = [...dYear].sort((a,b)=>b.Año-a.Año);
            sorted.forEach(d=>{{
                const cM = d.Var_YOY >= 0 ? '#10b981' : '#ef4444';
                const cC = d.Var_YOY_Cant >= 0 ? '#10b981' : '#ef4444';
                
                let vM = '-';
                if(d.Var_YOY != null) {{
                    const val = d.Var_YOY; // Safe access
                    if(Math.abs(val) < 0.001) vM = '<span style="color:var(--text-light)">0%</span>';
                    else vM = `<span style="color:${{cM}}">${{val.toFixed(1)}}%</span>`;
                }}

                let vC = '-';
                if(d.Var_YOY_Cant != null) {{
                    const val = d.Var_YOY_Cant;
                    if(Math.abs(val) < 0.001) vC = '<span style="color:var(--text-light)">0%</span>';
                    else vC = `<span style="color:${{cC}}">${{val.toFixed(1)}}%</span>`;
                }}

                const varTxt = `${{vM}} / ${{vC}}`;
                
                const avg = d.Cantidad > 0 ? d.Monto / d.Cantidad : 0;
                
                h+=`<tr style="border-bottom:1px solid var(--border)"><td style="padding:10px 4px;font-weight:700;color:var(--text-dark)">${{d.Año}}</td><td style="padding:10px 4px;text-align:right;color:var(--text-dark)">${{fmt(d.Monto)}}</td><td style="padding:10px 4px;text-align:center;color:var(--text-dark)">${{d.Cantidad}}</td><td style="padding:10px 4px;text-align:right;color:var(--text-dark)">${{fmt(avg)}}</td><td style="padding:10px 4px;text-align:right;color:var(--text-dark)">${{varTxt}}</td></tr>`;
            }});
            document.getElementById('tbl').innerHTML=h+'</tbody></table>';
        }}
        window.addEventListener('resize', function() {{
            const chartIds = ['c-evo', 'c-sec-monto', 'c-sec-cant', 'c-soc', 'c-cou'];
            chartIds.forEach(id => {{
               const el = document.getElementById(id);
               if(el) Plotly.Plots.resize(el);
            }});
        }});
        window.onload=init;
    </script>
    """
    
    return f"""
    <!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Dashboard Ejecutivo</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">{css}</head>
    
    <body>
        <nav class="top-nav">
            <div class="header-title">
                <h1 id="lbl-main">Dashboard Ejecutivo BCIE</h1>
                <div class="subtitle" id="lbl-sub">Análisis Integral de Aprobaciones Históricas (Datos Reales)</div>
            </div>
            <div class="nav-controls">
                <div style="display:flex; gap:10px; margin-right:15px">
                    <button class="btn-action btn-ghost-primary" onclick="takeScreenshot()">
                        <span id="btn-snap-txt">Captura</span>
                    </button>
                    <button class="btn-action btn-solid-primary" onclick="generatePDF()">
                        <span id="btn-pdf-txt">PDF</span>
                    </button>
                </div>
                <div class="update-badge" id="lbl-update">Datos Actualizados: {fecha_actualizacion}</div>
                <div class="toggle-wrapper">
                    <div class="toggle-switch" id="btn-theme" onclick="toggleTheme()" title="Cambiar Tema">
                        <div class="toggle-knob"></div>
                        <span class="toggle-icon">☀️</span>
                        <span class="toggle-icon">🌙</span>
                    </div>
                    <div class="toggle-labels">
                        <span id="lbl-theme-light">Claro</span>
                        <span id="lbl-theme-dark">Oscuro</span>
                    </div>
                </div>
                <div class="toggle-wrapper">
                    <div class="toggle-switch" id="btn-lang" onclick="toggleLang()" title="Cambiar Idioma">
                        <div class="toggle-knob"></div>
                    </div>
                    <div class="toggle-labels">
                        <span id="lbl-lang-es">Esp</span>
                        <span id="lbl-lang-en">Ing</span>
                    </div>
                </div>
            </div>
        </nav>

        <div class="dashboard-wrapper">
            <!-- SIN SIDEBAR -->
            <main class="main-content-exec">
                <div class="exec-grid">
                    <!-- COLUMNA 1: KPIs -->
                    <div style="display:grid;grid-template-rows:repeat(3, 1fr);gap:20px;height:100%">
                        <div class="kpi-box"><div class="kpi-title-exec" id="lbl-kt"></div><div class="kpi-val-exec">USD {formatInteger(data_processed['kpis']['total'])}</div></div>
                        <div class="kpi-box"><div class="kpi-title-exec" id="lbl-kc"></div><div class="kpi-val-exec">{formatInteger(data_processed['kpis']['count'])}</div></div>
                        <div class="kpi-box"><div class="kpi-title-exec" id="lbl-ka"></div><div class="kpi-val-exec">USD {formatInteger(data_processed['kpis']['avg'])}</div></div>
                    </div>
                    
                    <!-- COLUMNA 2: GRÁFICOS CENTRALES -->
                    <div style="display:grid;grid-template-rows:repeat(3, 1fr);gap:20px;height:100%;min-width:0">
                        <!-- FILA 1: EVOLUCION -->
                        <div class="chart-box" style="min-height:0"><div class="card-title-compact" id="lbl-ce"></div><div id="c-evo" style="height:100%"></div></div>
                        
                        <!-- FILA 2: SECTOR Y SOCIO (Ajustado) -->
                        <div style="display:flex;gap:20px;min-height:0;height:100%">
                            <!-- Sector con Doble Dona y Leyenda Apretada -->
                            <div class="chart-box" style="flex:1.4;display:flex;flex-direction:row;align-items:center;padding:20px">
                                <div style="display:flex;flex-direction:column;flex:2;height:100%">
                                    <div class="card-title-compact" id="lbl-cs" style="margin-bottom:15px"></div>
                                    <div style="display:flex;flex:1;min-height:0;gap:0px">
                                        <div id="c-sec-monto" style="flex:1;height:100%"></div>
                                        <div id="c-sec-cant" style="flex:1;height:100%"></div>
                                    </div>
                                </div>
                                <div id="leg-sec" style="flex:0 0 220px;height:100%;overflow-y:auto;padding-left:10px;margin-left:5px;display:flex;align-items:center"></div>
                            </div>
                            
                            <div class="chart-box" style="flex:1">
                                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
                                    <div class="card-title-compact" id="lbl-cp"></div>
                                    <div class="toggle-compact monto" id="btn-soc-metric" onclick="toggleMetric('soc')" title="Cambiar Monto/Cantidad">
                                        <div class="u-knob"></div>
                                        <span class="toggle-txt" style="color:var(--success)">$</span>
                                        <span class="toggle-txt" style="color:var(--primary)">#</span>
                                    </div>
                                </div>
                                <div id="c-soc" style="height:100%"></div>
                            </div>
                        </div>
                        
                        <!-- FILA 3: PAIS -->
                        <div class="chart-box" style="min-height:0">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
                                <div class="card-title-compact" id="lbl-cc"></div>
                                <div class="toggle-compact monto" id="btn-cou-metric" onclick="toggleMetric('cou')" title="Cambiar Monto/Cantidad">
                                    <div class="u-knob"></div>
                                    <span class="toggle-txt" style="color:var(--success)">$</span>
                                    <span class="toggle-txt" style="color:var(--primary)">#</span>
                                </div>
                            </div>
                            <div id="c-cou" style="height:100%"></div>
                        </div>
                    </div>
                    
                    <!-- COLUMNA 3: TABLA DETALLE -->
                    <div class="table-box" style="height:100%"><div class="table-header"><div class="card-title-compact" style="margin:0;border:none" id="lbl-th"></div></div><div class="table-scroll" id="tbl"></div></div>
                </div>
                <footer class="footer-compact" style="grid-column: 1 / -1; margin-top: 10px;">
                    <div class="footer-disclaimer" id="lbl-footer"></div>
                    <div class="footer-legal" id="lbl-rights">© {anio_actual} | UNIR–BCIE | Trabajo de Colaboración Académica | Proyecto Final de Máster | Equipo 03-D | Desarrollado por Edgar García, Norman Sabillón y Wilson Aguilar | Todos los derechos reservados.</div>
                </footer>
            </main>
        </div>
    {js}
    </body>
    </html>
    """
