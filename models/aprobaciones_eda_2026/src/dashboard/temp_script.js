                    <p>La metodología del análisis exploratorio se documentará aquí</p>
                </div>
            </div>
        </div>
    </div>

    <!-- ===================== FOOTER ===================== -->
    </main>
    <!-- End of Dashboard Wrapper -->
    </div>

    <!-- ===================== JAVASCRIPT ===================== -->
    <script>
        // ===================== DATA INJECTION =====================
        const DATA_MASTER = null; // {{DATA_MASTER}}

        // ===================== STATE MANAGEMENT =====================
        const STATE = {
            filterCountry: null,
            filterPartner: null,
            originalCountries: null // Store original countries for card display
        };

        // ===================== CORE LOGIC =====================
        // 1. Filter Data
        function applyFilters() {
            if(!DATA_MASTER || !DATA_MASTER.raw) return [];
            return DATA_MASTER.raw.filter(row => {
                const matchCountry = !STATE.filterCountry || row.Pais === STATE.filterCountry;
                const matchPartner = !STATE.filterPartner || row.Tipo_Socio === STATE.filterPartner;
                return matchCountry && matchPartner;
            });
        }

        // 2. Calculate Metrics on the Fly
        function calculateMetrics(rows) {
            const total_vol = rows.reduce((sum, r) => sum + (r.Monto_Aprobado || 0), 0);
            const total_count = rows.reduce((sum, r) => sum + (r.CANTIDAD_APROBACIONES || 1), 0); // Assuming 1 row = 1 record if col missing
            const avg_ticket = total_count ? total_vol / total_count : 0;
            const records_count = rows.length;

            // Trend
            const trendMap = {};
            rows.forEach(r => {
                if(!trendMap[r.Anio]) trendMap[r.Anio] = { Anio: r.Anio, Monto_Aprobado: 0, Count: 0 };
                trendMap[r.Anio].Monto_Aprobado += r.Monto_Aprobado;
                trendMap[r.Anio].Count += (r.CANTIDAD_APROBACIONES || 1);
            });
            const trend = Object.values(trendMap).sort((a,b) => a.Anio - b.Anio);

            // Top Sector (Simple Mode if filtered)
             const sectorMap = {};
            rows.forEach(r => {
                sectorMap[r.Sector_Economico] = (sectorMap[r.Sector_Economico] || 0) + r.Monto_Aprobado;
            });
            const top_sector = Object.keys(sectorMap).reduce((a, b) => sectorMap[a] > sectorMap[b] ? a : b, "N/A");
            const top_sector_count = rows.filter(r => r.Sector_Economico === top_sector).length; // Approx

            // Top 5 Table
            const top_table = [...rows].sort((a,b) => b.Monto_Aprobado - a.Monto_Aprobado).slice(0, 5);

            // Country Cards (Aggregate by Pais)
            const countryMap = {};
            rows.forEach(r => {
                if(!countryMap[r.Pais]) {
                    countryMap[r.Pais] = { Pais: r.Pais, Monto_Aprobado: 0, Count: 0, iso: r.Iso || 'xb' };
                }
                countryMap[r.Pais].Monto_Aprobado += r.Monto_Aprobado;
                countryMap[r.Pais].Count += (r.CANTIDAD_APROBACIONES || 1);
            });
            const countries = Object.values(countryMap).sort((a,b) => b.Monto_Aprobado - a.Monto_Aprobado);

            return {
                kpis: {
                    total_volume: total_vol,
                    total_count: total_count,
                    avg_ticket: avg_ticket,
                    total_records: records_count,
                    top_sector_count: top_sector_count,
                    top_sector_name: top_sector
                },
                trend: trend,
                top_table: top_table,
                countries: countries
            };
        }

        // 3. Update UI
        function updateDashboard() {
            const filteredRows = applyFilters();
            const metrics = calculateMetrics(filteredRows);
            
            // Store original countries on first load (before any filter)
            if (!STATE.originalCountries && DATA_MASTER.overview.countries) {
                STATE.originalCountries = DATA_MASTER.overview.countries;
            }
            
            // Update Global Data Context
             DATA_MASTER.overview.kpis = metrics.kpis;
             DATA_MASTER.overview.trend = metrics.trend;
             DATA_MASTER.overview.top_table = metrics.top_table;
             // Keep original countries for cards - don't overwrite with filtered data
             // DATA_MASTER.overview.countries = metrics.countries; // REMOVED: Keep original countries

             // Re-render
             renderTabContent(currentTab);
             updateFilterUI();
        }

        function toggleFilterCountry(country) {
            STATE.filterCountry = STATE.filterCountry === country ? null : country;
            updateDashboard();
        }

        function toggleFilterPartner(partnerType) {
            STATE.filterPartner = STATE.filterPartner === partnerType ? null : partnerType;
            updateDashboard();
        }

        function updateFilterUI() {
             // Add visual cues for active filters
             const cards = document.querySelectorAll('.country-card');
             cards.forEach(c => {
                 const cName = c.getAttribute('data-country');
                 if(STATE.filterCountry && cName !== STATE.filterCountry) {
                     c.style.opacity = '0.3';
                 } else {
                     c.style.opacity = '1';
                     if(STATE.filterCountry && cName === STATE.filterCountry) {
                         c.style.border = '2px solid var(--primary)';
                     } else {
                         c.style.border = '1px solid var(--border)';
                     }
                 }
             });

             // Show/Hide Reset Button
             let resetBtn = document.getElementById('btn-reset-filters');
             if(!resetBtn) {
                 // Create if not exists (in subtitle area)
                 const sub = document.querySelector('.subtitle');
                 if(sub) {
                     const btn = document.createElement('button');
                     btn.id = 'btn-reset-filters';
                     btn.className = 'btn-action btn-ghost-primary';
                     btn.style.marginLeft = '15px';
                     btn.style.fontSize = '12px';
                     btn.innerHTML = '↺ Restablecer Filtros';
                     btn.onclick = () => { STATE.filterCountry=null; STATE.filterPartner=null; updateDashboard(); };
                     sub.appendChild(btn);
                     resetBtn = btn;
                 }
             }

             if(resetBtn) {
                 const hasFilter = STATE.filterCountry || STATE.filterPartner;
                 resetBtn.style.display = hasFilter ? 'inline-block' : 'none';
                 if(hasFilter) {
                     resetBtn.innerText = `↺ Filtro: ${STATE.filterCountry || ''} ${STATE.filterPartner || ''} (X)`;
                 }
             }
        }


        // ===================== CONFIG =====================
        const CONFIG = {
            colors: {
                primary: getComputedStyle(document.documentElement).getPropertyValue('--primary').trim(),
                success: '#10b981',
                warning: '#f59e0b',
                danger: '#ef4444',
                grey: '#94a3b8'
            },
            // Country name translations
            country_names: {
                en: {
                    'Argentina': 'Argentina',
                    'Belice': 'Belize',
                    'Bolivia': 'Bolivia',
                    'Colombia': 'Colombia',
                    'Costa Rica': 'Costa Rica',
                    'Cuba': 'Cuba',
                    'El Salvador': 'El Salvador',
                    'Guatemala': 'Guatemala',
                    'Honduras': 'Honduras',
                    'México': 'Mexico',
                    'Nicaragua': 'Nicaragua',
                    'Panamá': 'Panama',
                    'Regional': 'Regional',
                    'República Dominicana': 'Dominican Republic'
                },
                es: {} // ES uses original names from data
            },
            tr: {
                es: {
                    overview: "Vista General",
                    evolution: "Evolución Temporal",
                    sectors: "Estrategia Sectorial",
                    risk: "Riesgos y Concentración",
                    quality: "Calidad de Datos",
                    kpi_vol: "Volumen Total",
                es: {
                    title: "EDA 2026",
                    subtitle: "Análisis Exploratorio",
                    overview: "Vista General",
                    evolution: "Evolución Temporal",
                    sectors: "Estrategia Sectorial",
                    risk: "Riesgo y Concentración",
                    quality: "Calidad de Datos",
                    kpi_vol: "Volumen Total",
                    kpi_count: "Operaciones",
                    kpi_ticket: "Ticket Promedio",
                    kpi_age: "Antigüedad Cartera",
                    chart_trend: "Evolución de Aprobaciones (Monto USD)",
                    chart_partner: "Funnel por Tipo de Socio",
                    chart_heatmap: "Mapa de Calor: Intensidad por País y Década",
                    chart_cycles: "Ciclos de Inversión (Crecimiento YoY)",
                    chart_sector_vol: "Mix Sectorial: Público vs Privado",
                    chart_top_sector: "Top 10 Sectores Económicos",
                    chart_risk_dist: "Distribución de Montos por País (Boxplot)",
                    chart_pareto: "Curva de Pareto (Concentración)",
                    tab_trend: "Tendencia",
                    tab_dist: "Distribución",
                    msg_no_data: "Sin datos disponibles",
                    loading: "Cargando...",
                    axis_amount: "Monto (USD)",
                    axis_count: "Cantidad",
                    // Extra Keys
                    kpi_records: "Total Registros",
                    kpi_top_sector: "Sector Principal",
                    kpi_records_sector: "Registros: ",
                    kpi_vol_long: "Monto Total Aprobado",
                    kpi_count_long: "Cantidad de Operaciones",
                    kpi_ticket_long: "Promedio por Aprobación",
                    lbl_updated: "Actualizado: ",
                    // Table Translations
                    table_title: "Comparativo Anual",
                    col_year: "Año",
                    col_amount_curr: "Monto Actual",
                    col_amount_prev: "Monto Anterior",
                    col_var_amount: "Variación Monto",
                    col_ops_curr: "Operaciones Actuales",
                    col_ops_prev: "Operaciones Anteriores",
                    col_var_ops: "Variación Aprobaciones",
                    // Chart Titles - Temporal
                    chart_heatmap_intensity: "Mapa de Calor (Intensidad)",
                    chart_cycles_amount: "Ciclos de Inversión (Crecimiento YoY)",
                    chart_heatmap_freq: "Mapa de Calor (Frecuencia)",
                    chart_cycles_ops: "Ciclos de Operaciones (Crecimiento YoY)",
                    chart_heatmap_avg: "Mapa de Calor (Promedio)",
                    chart_cycles_avg: "Ciclos de Promedio (Crecimiento YoY)",
                    // Buttons
                    btn_capture: "Captura",
                    btn_pdf: "PDF",
                    // Navigation
                    nav_panel: "Panel de Control",
                    nav_overview: "Vista General",
                    nav_temporal: "Evolución Temporal",
                    nav_sector: "Análisis Sectorial",
                    nav_risk: "Factores de Riesgo",
                    nav_quality: "Calidad de Datos",
                    // Footer
                    footer_legal: "© 2026 | UNIR–BCIE | Trabajo de Colaboración Académica | Equipo 03-D | Todos los derechos reservados.",
                    footer_disclaimer: "Los resultados son para fines académicos y no constituyen compromiso financiero vinculante por parte del BCIE.",
                    // Toggles
                    toggle_dark: "Oscuro",
                    toggle_light: "Claro",
                    toggle_es: "Es",
                    toggle_en: "En",
                    // Sector Chart
                    chart_sector_inst: "Distribución por Sector Institucional",
                    lbl_sector_public: "Sector Público",
                    lbl_sector_private: "Sector Privado",
                    lbl_amount: "Monto",
                    lbl_quantity: "Cantidad",
                    // New Sector Keys
                    chart_sec_avg: "Promedio por Aprobación por Sector",
                    chart_sec_corr: "Correlación: Monto vs Cantidad",
                    chart_sec_dist_monto: "Distribución Anual de Montos",
                    chart_sec_dist_cant: "Distribución Anual de Cantidades",
                    findings_title: "Hallazgos Clave del Análisis Sectorial",
                    // Axis & Labels
                    axis_usd_avg: "USD Promedio",
                    axis_usd: "Monto USD",
                    axis_count_simple: "Cantidad",
                    axis_log_monto: "Monto (Log)",
                    axis_count_ops: "Cantidad Ops",
                    chart_evo_monto_title: "Evolución Sectorial por Monto",
                    chart_evo_cant_title: "Evolución Sectorial por Cantidad",
                    findings_content: `
                      <ul style="padding-left: 1.2rem;">
                        <li><strong>Promedio por Aprobación:</strong> Se observa una divergencia clara. El <strong>Sector Público</strong> (violeta) maneja montos significativamente más altos por operación, mientras que el <strong>Sector Privado</strong> (rojo) mantiene montos más bajos y constantes, indicando una capilaridad mayor.</li>
                        <li><strong>Volumen vs. Frecuencia:</strong> Aunque el Sector Público domina en volumen monetario total, el Sector Privado ha mostrado picos de alta actividad en <em>cantidad</em> de operaciones, sugiriendo múltiples intervenciones de menor escala.</li>
                        <li><strong>Cíclicidad:</strong> La serie temporal muestra que la inversión pública tiende a ser más cíclica, mientras que el flujo privado parece responder más ágilmente a coyunturas de mercado.</li>
                        <li><strong>Dispersión:</strong> El Sector Público tiene una dispersión mucho mayor (proyectos medianos a megaproyectos). El Privado es más homogéneo.</li>
                      </ul>
                      <div style="margin-top:0.5rem; font-size:0.8rem; font-style:italic; opacity:0.7">* Nota: Este análisis se basa en datos históricos de aprobaciones y no constituye una auditoría financiera.</div>
                    `
                },
                en: {
                    title: "EDA 2026",
                    subtitle: "Exploratory Analysis",
                    overview: "Overview",
                    evolution: "Temporal Evolution",
                    sectors: "Sector Strategy",
                    risk: "Risk & Concentration",
                    quality: "Data Quality",
                    kpi_vol: "Total Volume",
                    kpi_count: "Operations",
                    kpi_ticket: "Avg Ticket",
                    kpi_age: "Portfolio Age",
                    chart_trend: "Approvals Evolution (USD Amount)",
                    chart_partner: "Funnel by Partner Type",
                    chart_heatmap: "Heatmap: Intensity by Country & Decade",
                    chart_cycles: "Investment Cycles (YoY Growth)",
                    chart_sector_vol: "Sector Mix: Public vs Private",
                    chart_top_sector: "Top 10 Economic Sectors",
                    chart_risk_dist: "Amount Distribution by Country (Boxplot)",
                    chart_pareto: "Pareto Curve (Concentration)",
                    tab_trend: "Trend",
                    tab_dist: "Distribution",
                    msg_no_data: "No data available",
                    loading: "Loading...",
                    axis_amount: "Amount (USD)",
                    axis_count: "Count",
                     // Extra Keys
                    kpi_records: "Total Records",
                    kpi_top_sector: "Leading Sector",
                    kpi_records_sector: "Records: ",
                    kpi_vol_long: "Total Approved Amount",
                    kpi_count_long: "Quantity of Operations",
                    kpi_ticket_long: "Average per Approval",
                    lbl_updated: "Updated: ",
                    // Table Translations
                    table_title: "Yearly Comparison",
                    col_year: "Year",
                    col_amount_curr: "Curr Amount",
                    col_amount_prev: "Prev Amount",
                    col_var_amount: "Var Amount",
                    // New Sector Keys (EN)
                    chart_sec_avg: "Average per Approval by Sector",
                    chart_sec_corr: "Correlation: Amount vs Quantity",
                    chart_sec_dist_monto: "Annual Amount Distribution",
                    chart_sec_dist_cant: "Annual Quantity Distribution",
                    findings_title: "Key Sector Analysis Findings",
                    // Axis & Labels
                    axis_usd_avg: "Avg USD",
                    axis_usd: "Amount USD",
                    axis_count_simple: "Quantity",
                    axis_log_monto: "Amount (Log)",
                    axis_count_ops: "Ops Count",
                    chart_evo_monto_title: "Sector Evolution by Amount",
                    chart_evo_cant_title: "Sector Evolution by Quantity",
                    findings_content: `
                      <ul style="padding-left: 1.2rem;">
                        <li><strong>Average per Approval:</strong> A clear divergence is observed. The <strong>Public Sector</strong> (violet) handles significantly higher amounts per operation, while the <strong>Private Sector</strong> (red) maintains lower and more constant amounts, indicating greater capillarity.</li>
                        <li><strong>Volume vs. Frequency:</strong> Although the Public Sector dominates in total monetary volume, the Private Sector has shown peaks of high activity in <em>quantity</em> of operations, suggesting multiple smaller-scale interventions.</li>
                        <li><strong>Cyclicality:</strong> The time series shows that public investment tends to be more cyclical, while private flow seems to respond more agilely to market conditions.</li>
                        <li><strong>Dispersion:</strong> The Public Sector has much greater dispersion (medium to mega-projects). The Private sector is more homogeneous.</li>
                      </ul>
                      <div style="margin-top:0.5rem; font-size:0.8rem; font-style:italic; opacity:0.7">* Note: This analysis is based on historical approval data and does not constitute a financial audit.</div>
                    ` ,

                    col_ops_curr: "Curr Ops",
                    col_ops_prev: "Prev Ops",
                    col_var_ops: "Var Ops",
                    // Chart Titles - Temporal
                    chart_heatmap_intensity: "Heatmap (Intensity)",
                    chart_cycles_amount: "Investment Cycles (YoY Growth)",
                    chart_heatmap_freq: "Heatmap (Frequency)",
                    chart_cycles_ops: "Operations Cycles (YoY Growth)",
                    chart_heatmap_avg: "Heatmap (Average)",
                    chart_cycles_avg: "Average Cycles (YoY Growth)",
                    // Buttons
                    btn_capture: "Capture",
                    btn_pdf: "PDF",
                    // Navigation
                    nav_panel: "Control Panel",
                    nav_overview: "Overview",
                    nav_temporal: "Temporal Evolution",
                    nav_sector: "Sector Analysis",
                    nav_risk: "Risk Factors",
                    nav_quality: "Data Quality",
                    // Footer
                    footer_legal: "© 2026 | UNIR–BCIE | Academic Collaboration Work | Team 03-D | All rights reserved.",
                    footer_disclaimer: "Results are for academic purposes and do not constitute binding financial commitment by BCIE.",
                    // Toggles
                    toggle_dark: "Dark",
                    toggle_light: "Light",
                    toggle_es: "Es",
                    toggle_en: "En",
                    // Sector Chart
                    chart_sector_inst: "Institutional Sector Distribution",
                    lbl_sector_public: "Public Sector",
                    lbl_sector_private: "Private Sector",
                    lbl_amount: "Amount",
                    lbl_quantity: "Quantity"
                }
            }
        };

        let currentLang = 'es';
        let currentTab = 'overview';

        // ===================== CORE FUNCTIONS =====================
        
        function initDashboard() {
            if (!DATA_MASTER) {
                console.warn("DATA_MASTER is null. Waiting for injection...");
                // Just in case, try to update UI after a delay if injection happens late (unlikely but safe)
                setTimeout(() => { if(DATA_MASTER) initDashboard(); }, 1000);
                return;
            }
            
            // Check Theme
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark') {
                document.getElementById('btn-theme').classList.add('active');
                document.documentElement.setAttribute('data-theme', 'dark');
            }

            // Update Last Updated Badge
            const lblUpdate = document.getElementById('lbl-update');
            if(lblUpdate && DATA_MASTER.last_updated) {
                 lblUpdate.innerText = (CONFIG.tr[currentLang].lbl_updated || 'Actualizado: ') + DATA_MASTER.last_updated;
            }

            // Render Overview by default
            // switchTab('overview'); // OLD
            
            // NEW: Start the dynamic loop
            updateDashboard();
            
            // Apply translations to static elements
            applyTranslations();
        }

        // Function to apply translations to all data-key elements
        function applyTranslations() {
            const t = CONFIG.tr[currentLang];
            document.querySelectorAll('[data-key]').forEach(el => {
                const key = el.getAttribute('data-key');
                if (t[key]) {
                    el.textContent = t[key];
                }
            });
            
            // Update dynamic labels
            const lblUpdate = document.getElementById('lbl-update');
            if(lblUpdate && DATA_MASTER?.last_updated) {
                lblUpdate.innerText = (t.lbl_updated || 'Actualizado: ') + DATA_MASTER.last_updated;
            }
        }

        // Toggle language function
        function toggleLanguage() {
            const btn = document.getElementById('btn-lang');
            btn.classList.toggle('active');
            currentLang = btn.classList.contains('active') ? 'en' : 'es';
            applyTranslations();
            renderTabContent(currentTab);
        }

        // Translate a single country name
        function translateCountry(name) {
            if (currentLang === 'es') return name; // Original data is in Spanish
            const dict = CONFIG.country_names.en;
            return dict[name] || name;
        }

        // Translate an array of country names
        function translateCountries(names) {
            return names.map(n => translateCountry(n));
        }

        // Helper to Wrap Label text if too long (e.g. "Republica Dominicana" -> "Republica<br>Dominicana")
        function wrapLabel(label) {
            if(!label) return '';
            const words = label.split(' ');
            if(words.length > 1 && label.length > 10) {
                 // Simple split: if more than 1 word and long enough, break after first word (or split evenly)
                 // For countries like "El Salvador", "Costa Rica", keep "El" with "Salvador"?
                 // Let's break at the middle space closest to center
                 const mid = Math.floor(words.length / 2);
                 return words.slice(0, mid + (words.length%2)).join(' ') + '<br>' + words.slice(mid + (words.length%2)).join(' ');
            }
            return label;
        }

        function switchTab(tabId) {
            currentTab = tabId;
            
            // Update Active State in Sidebar
            document.querySelectorAll('.btn-vertical').forEach(btn => btn.classList.remove('active'));
            const activeBtn = Array.from(document.querySelectorAll('.btn-vertical')).find(b => b.getAttribute('onclick')?.includes(tabId));
            if(activeBtn) activeBtn.classList.add('active');

            // Hide all Tab Views
            document.querySelectorAll('.tab-view').forEach(v => v.style.display = 'none');
            
            // Show Target Tab View
            const target = document.getElementById(`tab-${tabId}`);
            if(target) target.style.display = 'block';

            // Render specific tab content
            renderTabContent(tabId);
        }


        // Removed resetLayout as it's no longer needed with separate views

        function renderTabContent(tabId) {
            const data = DATA_MASTER;
            const t = CONFIG.tr[currentLang];
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            
            const layoutCommon = {
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { color: isDark ? '#f1f5f9' : '#1e293b', family: 'Inter', size: 12 },
                autosize: true,
                margin: { t: 30, r: 20, l: 50, b: 20 }
            };

            // --- TAB 1: OVERVIEW ---
            if (tabId === 'overview') {
                // KPIs
                updateKPI('kpi-1', formatCurrency(data.overview.kpis.total_volume), t.kpi_vol_long || 'Monto Total Aprobado');
                updateKPI('kpi-2', data.overview.kpis.total_count, t.kpi_count_long || 'Cantidad de Operaciones');
                updateKPI('kpi-3', formatCurrency(data.overview.kpis.avg_ticket), t.kpi_ticket_long || 'Promedio por Aprobación');
                
                // KPI 4: Total Records
                const kpi4 = document.getElementById('kpi-4');
                if(kpi4) {
                    kpi4.innerText = data.overview.kpis.total_records || 0;
                    kpi4.style.fontSize = '20px'; 
                    kpi4.style.lineHeight = '1.2';
                }
                const lbl4 = kpi4?.nextElementSibling;
                if(lbl4) lbl4.innerText = t.kpi_records || 'Total Registros';

                // Chart 1: Evolution Trend (Overview ID)
                const trendData = data.overview.trend;
                const traceMonto = {
                    x: trendData.map(d => d.Anio),
                    y: trendData.map(d => d.Monto_Aprobado),
                    name: t.kpi_vol || 'Monto',
                    type: 'scatter', 
                    mode: 'lines+markers',
                    line: {color: '#34d399', width: 2, shape: 'spline'},
                    marker: {symbol: 'circle', size: 6, color: isDark ? '#1e293b' : '#ffffff', line: {color: '#34d399', width: 2}}
                };
                
                const traceCount = {
                    x: trendData.map(d => d.Anio),
                    y: trendData.map(d => d.Count), 
                    name: t.kpi_count || 'Aprobaciones',
                    yaxis: 'y2',
                    type: 'scatter', 
                    mode: 'lines+markers',
                    line: {color: CONFIG.colors.primary, width: 2, shape: 'spline'}, 
                    marker: {symbol: 'circle', size: 6, color: isDark ? '#1e293b' : '#ffffff', line: {color: CONFIG.colors.primary, width: 2}}
                };

                const layoutDual = {
                    ...layoutCommon,
                    title: '', // HTML Title used
                    margin: {t: 30, b: 30, l: 50, r: 50},
                    xaxis: {gridcolor: isDark ? '#334155' : '#e2e8f0', zeroline: false},
                    yaxis: {title: t.axis_amount, showgrid: true, gridcolor: isDark ? '#334155' : '#e2e8f0', rangemode: 'tozero'},
                    yaxis2: {
                        title: t.axis_count,
                        overlaying: 'y',
                        side: 'right',
                        showgrid: false,
                        gridcolor: 'transparent',
                        rangemode: 'tozero'
                    },
                    legend: { orientation: 'h', x: 0.5, xanchor: 'center', y: -0.2 }
                };

                Plotly.newPlot('chart-overview-1', [traceMonto, traceCount], layoutDual);

                // Chart 2: Partner Funnel (Overview ID)
                const c2 = document.getElementById('chart-overview-2');
                if(c2 && c2.innerHTML.includes('Cargando')) c2.innerHTML = ''; 

                const funnel = data.overview.funnel || [];
                
                // Always show total funnel (static, unaffected by filter)
                // Use data.overview.funnel but ensure it comes from GLOBAL context if needed
                // Actually, 'data' passed here is usually filteredData. 
                // We need the GLOBAL funnel data to stay static.
                
                let funnelDataToRender = [];
                if(DATA_MASTER && DATA_MASTER.overview && DATA_MASTER.overview.funnel) {
                     // Get funnel from INITIAL load if possible, or recalculate from raw
                     // To be safe and truly static, let's recalc from DATA_MASTER.raw locally 
                     // or assume DATA_MASTER.overview.funnel is good enough if we don't want to recalc.
                     // BUT 'data' is the result of updateDashboard() -> calculateMetrics(filteredRows)
