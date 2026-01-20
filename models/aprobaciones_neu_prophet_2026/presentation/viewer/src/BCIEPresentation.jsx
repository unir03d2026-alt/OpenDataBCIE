import React, { useState, useEffect } from "react";
import {
  ChevronRight,
  ChevronLeft,
  Database,
  TrendingUp,
  Users,
  ShieldCheck,
  Activity,
  BarChart2,
  Layers,
  ArrowRight,
  Zap,
  Target,
  Search,
  Server,
  Maximize,
  Minimize,
} from "lucide-react";

const Slide = ({ children, className = "" }) => (
  <div
    className={`h-full w-full flex flex-col p-16 relative overflow-hidden bg-white text-slate-800 ${className}`}
  >
    {children}
    {/* Institutional Footer Strip */}
    <div className="absolute bottom-0 left-0 w-full h-4 bg-blue-900"></div>
    <div className="absolute bottom-4 left-16 text-xl text-slate-400 font-sans">
      BCIE Data Lab | Confidencial
    </div>
  </div>
);

const SlideHeader = ({ title, subtitle }) => (
  <div className="mb-12 border-l-8 border-blue-900 pl-8">
    <h2 className="text-5xl md:text-6xl font-bold text-blue-900 tracking-tight">
      {title}
    </h2>
    {subtitle && (
      <h3 className="text-3xl text-blue-500 mt-4 font-light">{subtitle}</h3>
    )}
  </div>
);

export default function BCIEPresentation() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const totalSlides = 9;


  const nextSlide = () => {
    if (currentSlide < totalSlides - 1) setCurrentSlide((prev) => prev + 1);
  };

  const prevSlide = () => {
    if (currentSlide > 0) setCurrentSlide((prev) => prev - 1);
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "ArrowRight") nextSlide();
      if (e.key === "ArrowLeft") prevSlide();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [currentSlide]);

  const [isFullscreen, setIsFullscreen] = useState(false);
  const [scale, setScale] = useState(1);

  useEffect(() => {
    const handleResize = () => {
      // Calculate scale to fit 1920x1080 into current window
      // We use a small buffer (0.95) to ensure it doesn't touch the edges in windowed mode
      // In fullscreen, we might want 1.0, but let's stick to "contain" logic
      const targetWidth = 1920;
      const targetHeight = 1080;
      
      const scaleX = window.innerWidth / targetWidth;
      const scaleY = window.innerHeight / targetHeight;
      
      // Use the smaller scale factor to ensure it fits entirely
      const newScale = Math.min(scaleX, scaleY);
      
      // Optional: Cap scale at 1 if you don't want it to zoom in on huge screens, 
      // but usually for presentation you want it to fill.
      setScale(newScale);
    };

    window.addEventListener("resize", handleResize);
    handleResize(); // Initial calculation

    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const toggleFullScreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
        setIsFullscreen(false);
      }
    }
  };

  const slides = [
    // SLIDE 1: PORTADA
    <Slide key="1" className="justify-center">
      <div className="absolute top-12 left-16 flex items-center space-x-6">
        <img 
          src="https://www.bcie.org/_next/image?url=%2Flogo-bcie-oficial.svg&w=384&q=75" 
          alt="Logo BCIE" 
          className="h-16 w-auto"
        />
      </div>
      <div className="absolute top-12 right-16">
        <img 
          src="https://campusvirtual.mexico.unir.net/pluginfile.php/3/core_admin/logo/0x200/1766046579/logo_unir_1666x348.png" 
          alt="Logo UNIR" 
          className="h-16 w-auto"
        />
      </div>

      <div className="max-w-7xl mt-20">
        <div className="w-40 h-2 bg-yellow-500 mb-10"></div>
        <h1 className="text-7xl md:text-8xl font-extrabold text-blue-900 leading-tight mb-8">
          BCIE Data Lab
        </h1>
        <p className="text-4xl text-blue-600 font-light mb-20">
          Transformando Datos Abiertos en Estrategia Predictiva
        </p>

        <div className="bg-slate-50 p-10 rounded-2xl border-l-8 border-slate-300 inline-block">
          <p className="text-xl font-bold text-slate-500 uppercase tracking-wider mb-4">
            Equipo de Innovación
          </p>
          <div className="flex space-x-10 text-slate-700 text-2xl">
            <span>Willson Aguilar</span>
            <span className="text-slate-300">|</span>
            <span>Edgar García</span>
            <span className="text-slate-300">|</span>
            <span>Norman Sabillón</span>
          </div>
        </div>
      </div>
    </Slide>,

    // SLIDE 2: CONTEXTO
    <Slide key="2">
      <SlideHeader
        title="El Contexto y El Desafío"
        subtitle="De la descripción retrospectiva a la anticipación estratégica"
      />

      <div className="flex flex-col md:flex-row h-full gap-16 items-center justify-center mb-16 px-8">
        {/* Pasado */}
        <div className="flex-1 bg-slate-50 p-12 rounded-3xl border border-slate-200 h-96 flex flex-col justify-center items-center text-center opacity-80 hover:opacity-100 transition-opacity">
          <div className="w-24 h-24 bg-slate-200 rounded-full flex items-center justify-center mb-8 text-slate-500">
            <Search size={48} />
          </div>
          <h3 className="text-3xl font-bold text-slate-600 mb-4">
            Análisis Descriptivo
          </h3>
          <p className="text-slate-500 italic text-2xl">"¿Qué pasó ayer?"</p>
          <ul className="mt-8 text-xl text-left list-disc list-inside text-slate-500 space-y-2">
            <li>Reportes estáticos</li>
            <li>Procesos manuales (Excel)</li>
            <li>Visión reactiva</li>
          </ul>
        </div>

        <div className="text-slate-300">
          <ArrowRight size={80} />
        </div>

        {/* Futuro */}
        <div className="flex-1 bg-gradient-to-br from-blue-50 to-white p-12 rounded-3xl border-4 border-blue-600 shadow-xl h-[28rem] flex flex-col justify-center items-center text-center relative overflow-hidden">
          <div className="absolute top-0 right-0 bg-blue-600 text-white text-lg font-bold px-6 py-2 rounded-bl-2xl">
            META 2026-2030
          </div>
          <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mb-8 text-blue-700">
            <Target size={64} />
          </div>
          <h3 className="text-4xl font-bold text-blue-900 mb-4">
            Inteligencia Artificial
          </h3>
          <p className="text-blue-600 font-medium text-2xl">"¿Qué pasará mañana?"</p>
          <ul className="mt-8 text-xl text-left space-y-4 text-blue-800">
            <li className="flex items-center">
              <Zap size={24} className="mr-4" /> Anticipación de demanda
            </li>
            <li className="flex items-center">
              <Zap size={24} className="mr-4" /> Modelos dinámicos
            </li>
            <li className="flex items-center">
              <Zap size={24} className="mr-4" /> Calidad de riesgo AA+
            </li>
          </ul>
        </div>
      </div>
    </Slide>,

    // SLIDE 3: QUÉ ES
    <Slide key="3">
      <SlideHeader
        title="¿Qué es el BCIE Data Lab?"
        subtitle="Arquitectura de inteligencia institucional en tres pilares"
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-10 mt-32 px-8">
        {/* Pilar 1 */}
        <div className="bg-white p-10 rounded-2xl shadow-md border border-slate-100 hover:shadow-xl transition-shadow">
          <div className="w-20 h-20 bg-blue-900 rounded-2xl flex items-center justify-center mb-6">
            <Database className="text-white" size={40} />
          </div>
          <h3 className="text-3xl font-bold text-blue-900 mb-4">
            1. Automatización
          </h3>
          <p className="text-slate-600 mb-6 text-xl">
            Conexión directa a API CKAN de Datos Abiertos.
          </p>
          <div className="text-lg font-semibold text-red-500 bg-red-50 inline-block px-4 py-2 rounded-lg">
            Adiós Excel Manual
          </div>
        </div>

        {/* Pilar 2 */}
        <div className="bg-white p-10 rounded-2xl shadow-md border border-slate-100 hover:shadow-xl transition-shadow">
          <div className="w-20 h-20 bg-blue-700 rounded-2xl flex items-center justify-center mb-6">
            <TrendingUp className="text-white" size={40} />
          </div>
          <h3 className="text-3xl font-bold text-blue-900 mb-4">
            2. Predicción
          </h3>
          <p className="text-slate-600 text-xl">
            Algoritmos avanzados para proyectar escenarios de crédito.
          </p>
          <div className="mt-8 text-lg font-mono text-slate-500 bg-slate-100 p-4 rounded-lg">
            Models: Prophet & ARIMA
          </div>
        </div>

        {/* Pilar 3 */}
        <div className="bg-white p-10 rounded-2xl shadow-md border border-slate-100 hover:shadow-xl transition-shadow">
          <div className="w-20 h-20 bg-blue-500 rounded-2xl flex items-center justify-center mb-6">
            <Users className="text-white" size={40} />
          </div>
          <h3 className="text-3xl font-bold text-blue-900 mb-4">
            3. Segmentación
          </h3>
          <p className="text-slate-600 text-xl">
            Clustering inteligente para identificar patrones únicos entre
            países.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <span className="px-4 py-2 bg-blue-50 text-blue-700 text-lg rounded-full">
              Socios Fundadores
            </span>
            <span className="px-4 py-2 bg-blue-50 text-blue-700 text-lg rounded-full">
              Socios No Fundadores
            </span>
            <span className="px-4 py-2 bg-blue-50 text-blue-700 text-lg rounded-full">
              Extraregionales
            </span>
          </div>
        </div>
      </div>
    </Slide>,

    // SLIDE 4: RIGOR TÉCNICO
    <Slide key="4">
      <SlideHeader
        title="Rigor Técnico"
        subtitle="Metodología CRISP-DM y Estándares MLOps"
      />

      <div className="flex flex-col items-center justify-center mt-16 scale-110 origin-center">
        <div className="w-full max-w-7xl flex items-center justify-between relative px-20">
          {/* Connecting Line */}
          <div className="absolute top-1/2 left-0 w-full h-2 bg-slate-200 -z-10"></div>

          {/* Node 1 */}
          <div className="flex flex-col items-center bg-white p-8 rounded-2xl">
            <div className="w-32 h-32 bg-gradient-to-br from-amber-600 to-amber-800 rounded-full flex items-center justify-center shadow-xl text-white mb-6 border-8 border-white">
              <Database size={48} />
            </div>
            <h4 className="font-bold text-3xl text-blue-900 mb-2">Ingesta</h4>
            <p className="text-xl text-slate-500 text-center w-64">
              Conexión Segura API
              <br />
              Datos Abiertos
            </p>
          </div>

          {/* Node 2 */}
          <div className="flex flex-col items-center bg-white p-8 rounded-2xl">
            <div className="w-32 h-32 bg-gradient-to-br from-slate-400 to-slate-600 rounded-full flex items-center justify-center shadow-xl text-white mb-6 border-8 border-white">
              <ShieldCheck size={48} />
            </div>
            <h4 className="font-bold text-3xl text-blue-900 mb-2">Limpieza</h4>
            <p className="text-xl text-slate-500 text-center w-64">
              Validación de calidad
              <br />
              Estructuración
            </p>
          </div>

          {/* Node 3 */}
          <div className="flex flex-col items-center bg-white p-8 rounded-2xl">
            <div className="w-32 h-32 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center shadow-xl text-white mb-6 border-8 border-white">
              <Activity size={48} />
            </div>
            <h4 className="font-bold text-3xl text-blue-900 mb-2">Modelado</h4>
            <p className="text-xl text-slate-500 text-center w-64">
              Entrenamiento AI
              <br />
              Calibración
            </p>
          </div>
        </div>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-full px-12">
          {/* Note 1: Seguridad */}
          <div className="bg-slate-50 p-6 rounded-2xl border-l-8 border-blue-500 flex items-start h-full">
            <ShieldCheck className="text-blue-600 mr-4 mt-1 shrink-0" size={32} />
            <div>
              <h5 className="font-bold text-blue-900 text-xl mb-2">
                Nota sobre Seguridad
              </h5>
              <p className="text-lg text-slate-600">
                Utilizamos datos públicos (Open Data) para esta fase, garantizando
                cero riesgo de filtración. Arquitectura escalable.
              </p>
            </div>
          </div>

          {/* Note 2: CRISP-DM */}
          <div className="bg-slate-50 p-6 rounded-2xl border-l-8 border-green-500 flex items-start h-full">
            <div className="text-green-600 mr-4 mt-1 shrink-0">
               <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </div>
            <div>
              <h5 className="font-bold text-blue-900 text-xl mb-2">
                ¿Por qué CRISP-DM?
              </h5>
              <p className="text-lg text-slate-600">
                Estándar industrial que garantiza un ciclo de vida estructurado
                para resolver problemas reales.
              </p>
            </div>
          </div>

          {/* Note 3: MLOps */}
          <div className="bg-slate-50 p-6 rounded-2xl border-l-8 border-purple-500 flex items-start h-full">
            <div className="text-purple-600 mr-4 mt-1 shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
            </div>
            <div>
              <h5 className="font-bold text-blue-900 text-xl mb-2">
                ¿Por qué MLOps?
              </h5>
              <p className="text-lg text-slate-600">
                Integra Dev y Ops. Permite reproducibilidad, escalabilidad y
                monitoreo continuo.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Slide>,

    // SLIDE 5: DASHBOARD EJECUTIVO
    <Slide key="5">
      <div className="flex justify-between items-start mb-4">
        <SlideHeader
          title="El Producto: Dashboard Ejecutivo"
          subtitle="De código complejo a decisiones simples"
        />
        <a
          href="/dashboards/dashboard_ejecutivo.html"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 bg-blue-900 text-white px-6 py-3 rounded-full font-bold shadow-lg hover:bg-blue-800 transition-all hover:scale-105 mt-4 mr-8"
        >
          Abrir en Nueva Pestaña <ArrowRight size={20} />
        </a>
      </div>

      <div className="flex flex-col h-full pb-8">
        <div className="flex-grow bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200 relative">
          <iframe
            src="/dashboards/dashboard_ejecutivo.html"
            title="Dashboard Ejecutivo"
            className="w-full h-full border-0"
            style={{ transform: "scale(1)", transformOrigin: "0 0" }}
          />
        </div>
      </div>
    </Slide>,

    // SLIDE 6: DASHBOARD PROPHET
    <Slide key="6">
      <div className="flex justify-between items-start mb-4">
        <SlideHeader
          title="Dashboard de Prophet"
          subtitle="Proyecciones y Análisis Predictivo 2026"
        />
        <a
          href="/dashboards/dashboard_estrategico.html"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 bg-blue-900 text-white px-6 py-3 rounded-full font-bold shadow-lg hover:bg-blue-800 transition-all hover:scale-105 mt-4 mr-8"
        >
          Abrir en Nueva Pestaña <ArrowRight size={20} />
        </a>
      </div>

      <div className="flex flex-col h-full pb-8">
        <div className="flex-grow bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200 relative">
          <iframe
            src="/dashboards/dashboard_estrategico.html"
            title="Dashboard Prophet - Estratégico"
            className="w-full h-full border-0"
            style={{ transform: "scale(1)", transformOrigin: "0 0" }}
          />
        </div>
      </div>
    </Slide>,

    // SLIDE 7: BENEFICIOS
    <Slide key="7">
      <SlideHeader
        title="Beneficios Estratégicos"
        subtitle="Generando valor tangible para el Banco"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-16 mt-32 px-16">
        <div className="flex gap-8">
          <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center shrink-0">
            <Zap className="text-blue-600" size={48} />
          </div>
          <div>
            <h4 className="text-4xl font-bold text-blue-900 mb-2">
              Eficiencia Operativa
            </h4>
            <p className="text-slate-600 text-2xl mt-1 leading-relaxed">
              Reducción drástica de horas-hombre en preparación de datos.
              Liberamos al talento para analizar, no para procesar.
            </p>
          </div>
        </div>

        <div className="flex gap-8">
          <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center shrink-0">
            <BarChart2 className="text-blue-600" size={48} />
          </div>
          <div>
            <h4 className="text-4xl font-bold text-blue-900 mb-2">
              Planificación (ALM)
            </h4>
            <p className="text-slate-600 text-2xl mt-1 leading-relaxed">
              Gestión de Activos y Pasivos basada en IA. Visión clara de
              desembolsos futuros para optimizar liquidez.
            </p>
          </div>
        </div>

        <div className="flex gap-8">
          <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center shrink-0">
            <Users className="text-blue-600" size={48} />
          </div>
          <div>
            <h4 className="text-4xl font-bold text-blue-900 mb-2">
              Conocimiento del Socio
            </h4>
            <p className="text-slate-600 text-2xl mt-1 leading-relaxed">
              Estrategias diferenciadas por Cluster de países. Entendimiento
              profundo de patrones regionales.
            </p>
          </div>
        </div>

        <div className="flex gap-8">
          <div className="w-24 h-24 bg-yellow-50 rounded-full flex items-center justify-center shrink-0">
            <Target className="text-yellow-600" size={48} />
          </div>
          <div>
            <h4 className="text-4xl font-bold text-blue-900 mb-2">
              Innovación Visible
            </h4>
            <p className="text-slate-600 text-2xl mt-1 leading-relaxed">
              Modernización tecnológica tangible alineada a nuestra calificación
              AA+.
            </p>
          </div>
        </div>
      </div>
    </Slide>,

    // SLIDE 8: EXPANSION TECNICA
    <Slide key="8">
      <SlideHeader
        title="Expansión y Validación del Modelado"
        subtitle="Rigor estadístico y segmentación profunda para 2026"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-16 mt-20 px-12 h-full items-start">
        {/* Columna 1: Validación de Series Temporales */}
        <div className="bg-white p-10 rounded-3xl shadow-lg border-t-8 border-blue-600 h-[32rem] relative overflow-hidden">
          <div className="absolute top-0 right-0 bg-blue-100 p-4 rounded-bl-3xl">
            <Activity className="text-blue-600" size={40} />
          </div>
          <h3 className="text-3xl font-bold text-blue-900 mb-6 pr-16 bg-white inline-block relative z-10">
            Validación de Pronóstico
          </h3>
          <p className="text-slate-600 text-xl mb-8 leading-relaxed">
            Implementación de modelos híbridos para minimizar el error (RMSE) y
            garantizar robustez ante volatilidad.
          </p>

          <div className="space-y-6">
            <div className="flex items-center bg-slate-50 p-4 rounded-xl border border-slate-100">
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold mr-4 shrink-0">
                A
              </div>
              <div>
                <span className="font-bold text-blue-900 text-xl block">
                  ARIMA
                </span>
                <span className="text-slate-500 text-lg">
                  Línea base estadística para series estacionarias.
                </span>
              </div>
            </div>

            <div className="flex items-center bg-blue-50 p-4 rounded-xl border border-blue-100 relative">
               <div className="absolute -left-3 top-1/2 -translate-y-1/2 bg-yellow-400 text-blue-900 text-xs font-bold px-2 py-1 rounded shadow rotate-90 origin-center hidden">VS</div>
              <div className="w-12 h-12 bg-blue-400 rounded-lg flex items-center justify-center text-white font-bold mr-4 shrink-0">
                P
              </div>
              <div>
                <span className="font-bold text-blue-900 text-xl block">
                  Prophet (Meta)
                </span>
                <span className="text-slate-600 text-lg">
                  Manejo superior de estacionalidad y días festivos.
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Columna 2: Clustering Avanzado */}
        <div className="bg-white p-10 rounded-3xl shadow-lg border-t-8 border-indigo-500 h-[32rem] relative overflow-hidden">
          <div className="absolute top-0 right-0 bg-indigo-100 p-4 rounded-bl-3xl">
            <Users className="text-indigo-600" size={40} />
          </div>
          <h3 className="text-3xl font-bold text-indigo-900 mb-6 pr-16 bg-white inline-block relative z-10">
            Estrategia de Clustering
          </h3>
          <p className="text-slate-600 text-xl mb-8 leading-relaxed">
            Identificación de patrones ocultos para personalizar la oferta de
            productos financieros.
          </p>

          <div className="space-y-5">
            <div className="flex items-start">
              <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold mr-4 mt-1 shrink-0">
                1
              </div>
              <div>
                <h4 className="font-bold text-indigo-800 text-xl">K-Means</h4>
                <p className="text-slate-500 text-lg">
                  Segmentación rápida por volumen y perfil de riesgo.
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold mr-4 mt-1 shrink-0">
                2
              </div>
              <div>
                <h4 className="font-bold text-indigo-800 text-xl">
                  Jerárquico (Hierarchical)
                </h4>
                <p className="text-slate-500 text-lg">
                  Dendrogramas para visualizar relaciones taxonómicas.
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold mr-4 mt-1 shrink-0">
                3
              </div>
              <div>
                <h4 className="font-bold text-indigo-800 text-xl">
                  Dynamic Time Warping (DTW)
                </h4>
                <p className="text-slate-500 text-lg">
                  Agrupamiento por <i>tendencia temporal</i>, ideal para series
                  financieras.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Slide>,

    // SLIDE 9: HOJA DE RUTA
    <Slide key="9">
      <SlideHeader title="Hoja de Ruta y Próximos Pasos" subtitle="" />

      <div className="flex flex-col h-full justify-between pb-24 px-12">
        {/* Timeline */}
        <div className="relative mt-20">
          <div className="absolute top-11 w-full h-2 bg-slate-200 transform -translate-y-1/2"></div>

          <div className="grid grid-cols-3 gap-16 text-center relative z-10">
            {/* Phase 1 */}
            <div className="flex flex-col items-center">
              <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center text-white border-8 border-white shadow">
                <ShieldCheck size={40} />
              </div>
              <h4 className="font-bold text-blue-900 mt-6 text-2xl">FASE 1</h4>
              <p className="text-lg font-bold text-green-600 uppercase mb-2">
                Completado
              </p>
              <p className="text-xl text-slate-500 px-8">
                Prototipo, validación de datos y arquitectura base.
              </p>
            </div>

            {/* Phase 2 */}
            <div className="flex flex-col items-center">
              <div className="w-24 h-24 bg-blue-600 rounded-full flex items-center justify-center text-white border-8 border-blue-200 shadow-lg animate-pulse">
                <Layers size={48} />
              </div>
              <h4 className="font-bold text-blue-900 mt-6 text-3xl">FASE 2</h4>
              <p className="text-lg font-bold text-blue-600 uppercase mb-2">
                Solicitud Actual
              </p>
              <p className="text-xl text-slate-800 font-medium px-8">
                Calibración de modelos y despliegue a producción.
              </p>
            </div>

            {/* Phase 3 */}
            <div className="flex flex-col items-center opacity-60">
              <div className="w-20 h-20 bg-slate-300 rounded-full flex items-center justify-center text-white border-8 border-white shadow">
                <Server size={40} />
              </div>
              <h4 className="font-bold text-slate-600 mt-6 text-2xl">FASE 3</h4>
              <p className="text-lg font-bold text-slate-400 uppercase mb-2">
                Futuro
              </p>
              <p className="text-xl text-slate-500 px-8">
                Integración total con sistemas Core Bancarios.
              </p>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="bg-blue-900 text-white p-10 rounded-3xl shadow-2xl text-center mt-8 mx-32 relative z-20">
          <h2 className="text-4xl font-bold mb-6">Solicitud de Aprobación</h2>
          <p className="text-2xl text-blue-100 mb-8 max-w-4xl mx-auto leading-relaxed">
            Solicitamos luz verde para avanzar a la Fase 2: Calibración y
            Despliegue.
            <br />
            <span className="italic text-xl opacity-80 block mt-4">
              Porque en el BCIE, los datos deben construir desarrollo.
            </span>
          </p>
          <button className="bg-yellow-500 text-blue-900 font-bold py-4 px-12 text-xl rounded-full hover:bg-yellow-400 transition-colors shadow-xl">
            Aprobar Fase 2
          </button>
        </div>
      </div>
    </Slide>,
  ];

  return (
    <div className="w-screen h-screen bg-slate-900 flex items-center justify-center overflow-hidden font-sans">
      <div
        style={{
          width: "1920px",
          height: "1080px",
          transform: `scale(${scale})`,
        }}
        className="bg-white shadow-2xl relative overflow-hidden flex flex-col shrink-0 origin-center"
      >
        {/* Slide Content */}
        <div className="flex-grow relative">{slides[currentSlide]}</div>

        {/* Controls Overlay */}
        <div className="absolute bottom-8 right-8 flex space-x-2 z-20">
          <button
            onClick={toggleFullScreen}
            className="p-3 bg-slate-800 text-white rounded-full hover:bg-slate-700 transition-all shadow-lg mr-4"
            title="Pantalla Completa"
          >
            {isFullscreen ? <Minimize size={24} /> : <Maximize size={24} />}
          </button>
          <button
            onClick={prevSlide}
            disabled={currentSlide === 0}
            className="p-3 bg-blue-900 text-white rounded-full disabled:opacity-30 hover:bg-blue-800 transition-all shadow-lg"
          >
            <ChevronLeft size={24} />
          </button>
          <div className="bg-white/90 backdrop-blur px-4 py-3 rounded-full font-mono text-blue-900 font-bold shadow-lg border border-slate-100">
            {currentSlide + 1} / {totalSlides}
          </div>
          <button
            onClick={nextSlide}
            disabled={currentSlide === totalSlides - 1}
            className="p-3 bg-blue-900 text-white rounded-full disabled:opacity-30 hover:bg-blue-800 transition-all shadow-lg"
          >
            <ChevronRight size={24} />
          </button>
        </div>
      </div>
    </div>
  );
}
