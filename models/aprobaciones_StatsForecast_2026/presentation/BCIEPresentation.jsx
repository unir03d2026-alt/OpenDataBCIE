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
} from "lucide-react";

const Slide = ({ children, className = "" }) => (
  <div
    className={`h-full w-full flex flex-col p-8 md:p-12 relative overflow-hidden bg-white text-slate-800 ${className}`}
  >
    {children}
    {/* Institutional Footer Strip */}
    <div className="absolute bottom-0 left-0 w-full h-2 bg-blue-900"></div>
    <div className="absolute bottom-2 right-12 text-xs text-slate-400 font-sans">
      BCIE Data Lab | Confidencial
    </div>
  </div>
);

const SlideHeader = ({ title, subtitle }) => (
  <div className="mb-8 border-l-4 border-blue-900 pl-4">
    <h2 className="text-3xl md:text-4xl font-bold text-blue-900 tracking-tight">
      {title}
    </h2>
    {subtitle && (
      <h3 className="text-xl text-blue-500 mt-2 font-light">{subtitle}</h3>
    )}
  </div>
);

export default function BCIEPresentation() {
  const [currentSlide, setCurrentSlide] = useState(0);

  const totalSlides = 7;

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

  const slides = [
    // SLIDE 1: PORTADA
    <Slide key="1" className="justify-center">
      <div className="absolute top-8 left-12 flex items-center space-x-4">
        {/* Placeholder for BCIE Logo Concept */}
        <div className="text-blue-900 font-bold text-2xl tracking-widest flex items-center">
          <div className="w-8 h-8 bg-blue-900 rounded-sm mr-2"></div>
          BCIE
        </div>
      </div>
      <div className="absolute top-8 right-12">
        <span className="text-slate-400 font-semibold tracking-wide">UNIR</span>
      </div>

      <div className="max-w-4xl mt-12">
        <div className="w-24 h-1 bg-yellow-500 mb-6"></div>
        <h1 className="text-5xl md:text-6xl font-extrabold text-blue-900 leading-tight mb-4">
          BCIE Data Lab
        </h1>
        <p className="text-2xl text-blue-600 font-light mb-12">
          Transformando Datos Abiertos en Estrategia Predictiva
        </p>

        <div className="bg-slate-50 p-6 rounded-lg border-l-4 border-slate-300 inline-block">
          <p className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">
            Equipo de Innovación
          </p>
          <div className="flex space-x-6 text-slate-700">
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

      <div className="flex flex-col md:flex-row h-full gap-8 items-center justify-center mb-12">
        {/* Pasado */}
        <div className="flex-1 bg-slate-50 p-8 rounded-xl border border-slate-200 h-64 flex flex-col justify-center items-center text-center opacity-80 hover:opacity-100 transition-opacity">
          <div className="w-16 h-16 bg-slate-200 rounded-full flex items-center justify-center mb-4 text-slate-500">
            <Search size={32} />
          </div>
          <h3 className="text-xl font-bold text-slate-600 mb-2">
            Análisis Descriptivo
          </h3>
          <p className="text-slate-500 italic">"¿Qué pasó ayer?"</p>
          <ul className="mt-4 text-sm text-left list-disc list-inside text-slate-500">
            <li>Reportes estáticos</li>
            <li>Procesos manuales (Excel)</li>
            <li>Visión reactiva</li>
          </ul>
        </div>

        <div className="text-slate-300">
          <ArrowRight size={48} />
        </div>

        {/* Futuro */}
        <div className="flex-1 bg-gradient-to-br from-blue-50 to-white p-8 rounded-xl border-2 border-blue-600 shadow-lg h-80 flex flex-col justify-center items-center text-center relative overflow-hidden">
          <div className="absolute top-0 right-0 bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-bl-lg">
            META 2026-2030
          </div>
          <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mb-4 text-blue-700">
            <Target size={40} />
          </div>
          <h3 className="text-2xl font-bold text-blue-900 mb-2">
            Inteligencia Artificial
          </h3>
          <p className="text-blue-600 font-medium">"¿Qué pasará mañana?"</p>
          <ul className="mt-4 text-sm text-left space-y-2 text-blue-800">
            <li className="flex items-center">
              <Zap size={14} className="mr-2" /> Anticipación de demanda
            </li>
            <li className="flex items-center">
              <Zap size={14} className="mr-2" /> Modelos dinámicos
            </li>
            <li className="flex items-center">
              <Zap size={14} className="mr-2" /> Calidad de riesgo AA+
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

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
        {/* Pilar 1 */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
          <div className="w-12 h-12 bg-blue-900 rounded-lg flex items-center justify-center mb-4">
            <Database className="text-white" />
          </div>
          <h3 className="text-xl font-bold text-blue-900 mb-3">
            1. Automatización
          </h3>
          <p className="text-slate-600 mb-4">
            Conexión directa a API CKAN de Datos Abiertos.
          </p>
          <div className="text-xs font-semibold text-red-500 bg-red-50 inline-block px-2 py-1 rounded">
            Adiós Excel Manual
          </div>
        </div>

        {/* Pilar 2 */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
          <div className="w-12 h-12 bg-blue-700 rounded-lg flex items-center justify-center mb-4">
            <TrendingUp className="text-white" />
          </div>
          <h3 className="text-xl font-bold text-blue-900 mb-3">
            2. Predicción
          </h3>
          <p className="text-slate-600">
            Algoritmos avanzados para proyectar escenarios de crédito.
          </p>
          <div className="mt-4 text-xs font-mono text-slate-500 bg-slate-100 p-2 rounded">
            Models: Prophet & ARIMA
          </div>
        </div>

        {/* Pilar 3 */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
          <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center mb-4">
            <Users className="text-white" />
          </div>
          <h3 className="text-xl font-bold text-blue-900 mb-3">
            3. Segmentación
          </h3>
          <p className="text-slate-600">
            Clustering inteligente para identificar patrones únicos entre
            países.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <span className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full">
              Socios Fundadores
            </span>
            <span className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full">
              Extra-regionales
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

      <div className="flex flex-col items-center justify-center mt-8">
        <div className="w-full max-w-5xl flex items-center justify-between relative">
          {/* Connecting Line */}
          <div className="absolute top-1/2 left-0 w-full h-1 bg-slate-200 -z-10"></div>

          {/* Node 1 */}
          <div className="flex flex-col items-center bg-white p-4">
            <div className="w-20 h-20 bg-gradient-to-br from-amber-600 to-amber-800 rounded-full flex items-center justify-center shadow-lg text-white mb-4 border-4 border-white">
              <Database size={32} />
            </div>
            <h4 className="font-bold text-lg text-blue-900">Ingesta</h4>
            <p className="text-sm text-slate-500 text-center w-48">
              Conexión Segura API
              <br />
              Datos Abiertos
            </p>
          </div>

          {/* Node 2 */}
          <div className="flex flex-col items-center bg-white p-4">
            <div className="w-20 h-20 bg-gradient-to-br from-slate-400 to-slate-600 rounded-full flex items-center justify-center shadow-lg text-white mb-4 border-4 border-white">
              <ShieldCheck size={32} />
            </div>
            <h4 className="font-bold text-lg text-blue-900">Limpieza</h4>
            <p className="text-sm text-slate-500 text-center w-48">
              Validación de calidad
              <br />
              Estructuración
            </p>
          </div>

          {/* Node 3 */}
          <div className="flex flex-col items-center bg-white p-4">
            <div className="w-20 h-20 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center shadow-lg text-white mb-4 border-4 border-white">
              <Activity size={32} />
            </div>
            <h4 className="font-bold text-lg text-blue-900">Modelado</h4>
            <p className="text-sm text-slate-500 text-center w-48">
              Entrenamiento AI
              <br />
              Calibración
            </p>
          </div>
        </div>

        <div className="mt-16 bg-blue-50 p-4 rounded-lg flex items-start max-w-2xl border border-blue-100">
          <ShieldCheck className="text-blue-600 mr-3 mt-1 shrink-0" size={20} />
          <div>
            <h5 className="font-bold text-blue-900 text-sm">
              Nota sobre Seguridad:
            </h5>
            <p className="text-sm text-slate-600">
              Utilizamos datos públicos (Open Data) para esta fase, garantizando
              cero riesgo de filtración. La arquitectura es escalable para
              manejar datos confidenciales privados en futuras iteraciones.
            </p>
          </div>
        </div>
      </div>
    </Slide>,

    // SLIDE 5: EL PRODUCTO (DASHBOARD)
    <Slide key="5">
      <SlideHeader
        title="El Producto: Dashboard Ejecutivo"
        subtitle="De código complejo a decisiones simples"
      />

      <div className="w-full h-full bg-slate-100 rounded-lg shadow-inner p-4 border border-slate-300 relative overflow-hidden flex flex-col">
        {/* Mockup Header */}
        <div className="flex justify-between items-center bg-white p-3 rounded shadow-sm mb-4">
          <span className="font-bold text-blue-900 flex items-center gap-2">
            <Activity size={18} /> Proyecciones Crediticias 2030
          </span>
          <div className="flex space-x-2">
            <div className="px-3 py-1 bg-green-100 text-green-700 text-xs rounded-full font-bold cursor-pointer">
              Escenario Optimista
            </div>
            <div className="px-3 py-1 bg-slate-100 text-slate-400 text-xs rounded-full cursor-pointer">
              Escenario Pesimista
            </div>
          </div>
        </div>

        <div className="flex gap-4 flex-1">
          {/* KPI Cards */}
          <div className="w-1/4 flex flex-col gap-4">
            <div className="bg-white p-4 rounded shadow-sm border-l-4 border-blue-500">
              <div className="text-xs text-slate-500 uppercase">
                Proyección 2026
              </div>
              <div className="text-2xl font-bold text-blue-900">$2.4B</div>
              <div className="text-xs text-green-500 font-bold">
                ▲ 5.2% vs 2025
              </div>
            </div>
            <div className="bg-white p-4 rounded shadow-sm border-l-4 border-yellow-500">
              <div className="text-xs text-slate-500 uppercase">
                Precisión (MAPE)
              </div>
              <div className="text-2xl font-bold text-slate-700">94.8%</div>
              <div className="text-xs text-slate-400">Modelo validado</div>
            </div>
          </div>

          {/* Main Chart Area */}
          <div className="flex-1 bg-white p-6 rounded shadow-sm flex items-end justify-between relative">
            <div className="absolute top-4 left-6 text-sm font-bold text-slate-500">
              Volumen de Aprobaciones (Proyección)
            </div>

            {/* Bars */}
            {[40, 55, 45, 60, 75, 85, 95].map((h, i) => (
              <div
                key={i}
                className="w-full mx-2 flex flex-col justify-end h-full group"
              >
                <div
                  className={`w-full rounded-t transition-all duration-500 ${
                    i > 3
                      ? "bg-blue-400 pattern-diagonal-lines"
                      : "bg-slate-300"
                  }`}
                  style={{ height: `${h}%` }}
                ></div>
                <div className="text-xs text-center text-slate-500 mt-2 font-mono">
                  {2022 + i}
                </div>
                {i === 4 && (
                  <div className="absolute top-1/2 left-1/2 bg-blue-900 text-white text-xs px-2 py-1 rounded -translate-x-1/2 shadow-lg animate-pulse">
                    Predicción IA
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </Slide>,

    // SLIDE 6: BENEFICIOS
    <Slide key="6">
      <SlideHeader
        title="Beneficios Estratégicos"
        subtitle="Generando valor tangible para el Banco"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-6">
        <div className="flex gap-4">
          <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center shrink-0">
            <Zap className="text-blue-600" size={28} />
          </div>
          <div>
            <h4 className="text-lg font-bold text-blue-900">
              Eficiencia Operativa
            </h4>
            <p className="text-slate-600 text-sm mt-1">
              Reducción drástica de horas-hombre en preparación de datos.
              Liberamos al talento para analizar, no para procesar.
            </p>
          </div>
        </div>

        <div className="flex gap-4">
          <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center shrink-0">
            <BarChart2 className="text-blue-600" size={28} />
          </div>
          <div>
            <h4 className="text-lg font-bold text-blue-900">
              Planificación (ALM)
            </h4>
            <p className="text-slate-600 text-sm mt-1">
              Gestión de Activos y Pasivos basada en IA. Visión clara de
              desembolsos futuros para optimizar liquidez.
            </p>
          </div>
        </div>

        <div className="flex gap-4">
          <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center shrink-0">
            <Users className="text-blue-600" size={28} />
          </div>
          <div>
            <h4 className="text-lg font-bold text-blue-900">
              Conocimiento del Socio
            </h4>
            <p className="text-slate-600 text-sm mt-1">
              Estrategias diferenciadas por Cluster de países. Entendimiento
              profundo de patrones regionales.
            </p>
          </div>
        </div>

        <div className="flex gap-4">
          <div className="w-14 h-14 bg-yellow-50 rounded-full flex items-center justify-center shrink-0">
            <Target className="text-yellow-600" size={28} />
          </div>
          <div>
            <h4 className="text-lg font-bold text-blue-900">
              Innovación Visible
            </h4>
            <p className="text-slate-600 text-sm mt-1">
              Modernización tecnológica tangible alineada a nuestra calificación
              AA+.
            </p>
          </div>
        </div>
      </div>
    </Slide>,

    // SLIDE 7: HOJA DE RUTA
    <Slide key="7">
      <SlideHeader title="Hoja de Ruta y Próximos Pasos" subtitle="" />

      <div className="flex flex-col h-full justify-between pb-12">
        {/* Timeline */}
        <div className="relative mt-8">
          <div className="absolute top-1/2 w-full h-1 bg-slate-200 transform -translate-y-1/2"></div>

          <div className="grid grid-cols-3 gap-4 text-center relative z-10">
            {/* Phase 1 */}
            <div className="flex flex-col items-center">
              <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center text-white border-4 border-white shadow">
                <ShieldCheck size={20} />
              </div>
              <h4 className="font-bold text-blue-900 mt-3">FASE 1</h4>
              <p className="text-xs font-bold text-green-600 uppercase mb-1">
                Completado
              </p>
              <p className="text-sm text-slate-500 px-4">
                Prototipo, validación de datos y arquitectura base.
              </p>
            </div>

            {/* Phase 2 */}
            <div className="flex flex-col items-center">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white border-4 border-blue-200 shadow-lg animate-pulse">
                <Layers size={24} />
              </div>
              <h4 className="font-bold text-blue-900 mt-3 text-lg">FASE 2</h4>
              <p className="text-xs font-bold text-blue-600 uppercase mb-1">
                Solicitud Actual
              </p>
              <p className="text-sm text-slate-800 font-medium px-4">
                Calibración de modelos y despliegue a producción.
              </p>
            </div>

            {/* Phase 3 */}
            <div className="flex flex-col items-center opacity-60">
              <div className="w-10 h-10 bg-slate-300 rounded-full flex items-center justify-center text-white border-4 border-white shadow">
                <Server size={20} />
              </div>
              <h4 className="font-bold text-slate-600 mt-3">FASE 3</h4>
              <p className="text-xs font-bold text-slate-400 uppercase mb-1">
                Futuro
              </p>
              <p className="text-sm text-slate-500 px-4">
                Integración total con sistemas Core Bancarios.
              </p>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="bg-blue-900 text-white p-8 rounded-xl shadow-2xl text-center mt-8">
          <h2 className="text-3xl font-bold mb-4">Solicitud de Aprobación</h2>
          <p className="text-lg text-blue-100 mb-6 max-w-2xl mx-auto">
            Solicitamos luz verde para avanzar a la Fase 2: Calibración y
            Despliegue.
            <br />
            <span className="italic text-sm opacity-80">
              Porque en el BCIE, los datos deben construir desarrollo.
            </span>
          </p>
          <button className="bg-yellow-500 text-blue-900 font-bold py-3 px-8 rounded-full hover:bg-yellow-400 transition-colors shadow-lg">
            Aprobar Fase 2
          </button>
        </div>
      </div>
    </Slide>,
  ];

  return (
    <div className="w-full h-screen bg-slate-200 flex items-center justify-center font-sans">
      <div className="w-full h-full md:w-[1024px] md:h-[768px] bg-white shadow-2xl relative overflow-hidden flex flex-col">
        {/* Slide Content */}
        <div className="flex-grow relative">{slides[currentSlide]}</div>

        {/* Controls Overlay */}
        <div className="absolute bottom-8 right-8 flex space-x-2 z-20">
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
