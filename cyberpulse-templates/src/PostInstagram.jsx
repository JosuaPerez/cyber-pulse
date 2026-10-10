import React from 'react';

const PostInstagram = ({ familia = 'alerta', level, type, category, title, description, summary, currentSlide = 1, totalSlides = 5 }) => {
  const themeColors = {
    basic: { border: 'border-green-500', text: 'text-green-400', bg: 'bg-green-500/10', glow: 'shadow-[0_0_50px_rgba(34,197,94,0.15)]', bgGlow: 'bg-green-500', icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /> },
    intermediate: { border: 'border-yellow-500', text: 'text-yellow-400', bg: 'bg-yellow-500/10', glow: 'shadow-[0_0_50px_rgba(234,179,8,0.15)]', bgGlow: 'bg-yellow-500', icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /> },
    critical: { border: 'border-red-500', text: 'text-red-400', bg: 'bg-red-500/10', glow: 'shadow-[0_0_50px_rgba(239,68,68,0.15)]', bgGlow: 'bg-red-500', icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /> },
    high: { border: 'border-amber-500', text: 'text-amber-400', bg: 'bg-amber-500/10', glow: 'shadow-[0_0_50px_rgba(245,158,11,0.15)]', bgGlow: 'bg-amber-500', icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /> },
  };

  themeColors.medium = themeColors.intermediate;

  const isEducativo = familia === 'educativo';
  const educativoTheme = {
    border: 'border-cyan-500',
    text: 'text-cyan-400',
    bg: 'bg-cyan-500/10',
    glow: 'shadow-[0_0_50px_rgba(6,182,212,0.15)]',
    bgGlow: 'bg-cyan-500',
    icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 5.5A2.5 2.5 0 016.5 3H20v16H6.5A2.5 2.5 0 014 16.5v-11zM4 5.5A2.5 2.5 0 016.5 8H20M8 12h8m-8 4h5" />,
  };
  const theme = isEducativo ? educativoTheme : (themeColors[level] || themeColors.critical);
  const detailPromptClass = isEducativo ? 'text-cyan-400' : 'text-green-500';
  const impactCardClass = isEducativo
    ? 'bg-cyan-950/20 border-cyan-900/40 hover:bg-cyan-950/40'
    : 'bg-red-950/20 border-red-900/40 hover:bg-red-950/40';
  const impactIconClass = isEducativo ? 'text-cyan-400' : 'text-red-500';
  const saveTextClass = isEducativo ? 'text-cyan-400' : 'text-yellow-400';
  const progressWidth = `${(currentSlide / totalSlides) * 100}%`;

  const renderHighlighted = (text) => {
    if (!text) return null;
    const parts = text.split('*');
    return parts.map((part, index) =>
      index % 2 === 1 ? (
        <span key={index} className={`font-black ${theme.text} bg-slate-900/90 px-3 py-1 rounded-lg shadow-lg border border-slate-700/50 inline-block mx-1 transform -translate-y-1`}>
          {part}
        </span>
      ) : part
    );
  };

  return (
    <div className={`w-[1080px] h-[1350px] bg-[#070B14] flex flex-col justify-between p-16 font-sans relative overflow-hidden ${theme.glow}`}>

      {/* BARRA DE PROGRESO */}
      <div className="absolute top-0 left-0 w-full h-3 bg-slate-900 z-50">
        <div className={`h-full ${theme.bgGlow} transition-all duration-300`} style={{ width: progressWidth }}></div>
      </div>

      {/* FONDO DE MALLA SUTIL */}
      <div className="absolute inset-0 opacity-10 pointer-events-none"
        style={{ backgroundImage: 'linear-gradient(#334155 1px, transparent 1px), linear-gradient(90deg, #334155 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
      </div>

      {/* CABECERA */}
      <div className="flex justify-between items-center z-10 mt-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center text-slate-900 shadow-[0_0_15px_rgba(255,255,255,0.4)]">
            <svg className="w-9 h-9" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 12h-4l-3-9l-5 18l-3-9H2"></path>
            </svg>
          </div>
          <h1 className="text-4xl font-bold text-white tracking-widest">Cyber<span className={theme.text}>Pulse</span></h1>
        </div>
        <div className={`px-6 py-2 rounded-full border-2 ${theme.border} ${theme.bg} ${theme.text} uppercase tracking-widest font-bold text-xl`}>
          {category}
        </div>
      </div>

      {/* CONTENEDOR CENTRAL: Aquí ocurre la magia del flujo.
        flex-1 y justify-center aseguran que todo el contenido flote en el medio de la imagen, llenando los vacíos.
      */}
      <div className="flex-1 flex flex-col justify-center w-full z-10 relative mt-8 mb-8">

        {/* EL "HILO" CONDUCTOR: Una línea vertical que conecta la historia (excepto en la portada) */}
        {type !== 'cover' && (
          <div className={`absolute left-0 top-10 bottom-10 w-1 ${theme.bgGlow} opacity-30 rounded-full`}></div>
        )}

        <div className={type !== 'cover' ? "pl-12" : ""}>

          {/* 1. PORTADA MEJORADA (Con Fotografía de Fondo Integrada) */}
          {type === 'cover' && (
            <>
              {/* NUEVA IMAGEN DE FONDO (Con opacidad baja y mezcla) */}
              <div className="absolute inset-0 z-0 opacity-20 mix-blend-luminosity">
                <img
                  src="https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1080&q=80"
                  alt="Cyber background"
                  className="w-full h-full object-cover"
                />
                {/* Gradiente para suavizar los bordes de la foto */}
                <div className="absolute inset-0 bg-gradient-to-t from-[#070B14] via-[#070B14]/40 to-[#070B14]"></div>
              </div>

              {/* Contenido de la portada (Asegúrate de que tenga z-10 o relative para estar sobre la foto) */}
              <div className="flex flex-col items-center text-center w-full relative z-10">
                <div className={`w-64 h-64 ${theme.bg} border-2 ${theme.border} rounded-full flex items-center justify-center mb-12 shadow-[0_0_80px_rgba(0,0,0,0.5)] backdrop-blur-sm`}>
                  <svg className={`w-32 h-32 ${theme.text}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    {theme.icon}
                  </svg>
                </div>

                <div className={`w-32 h-2 ${theme.bg} ${theme.border} border-t-4 mb-8 mx-auto`}></div>
                <h2 className="text-[5.5rem] font-extrabold text-white leading-tight drop-shadow-2xl">
                  {renderHighlighted(title)}
                </h2>
                <p className="text-4xl text-slate-300 leading-snug mt-8 font-light drop-shadow-lg">
                  {renderHighlighted(description)}
                </p>
              </div>
            </>
          )}

          {/* TITULO ESTÁNDAR PARA SLIDES 2 AL 5 */}
          {type !== 'cover' && (
            <h2 className="text-[4.5rem] font-extrabold text-white leading-tight mb-10">
              {renderHighlighted(title)}
            </h2>
          )}

          {/* 2. EL PROBLEMA (TL;DR) */}
          {type === 'problem' && (
            <div className="bg-slate-900/80 p-12 rounded-3xl border border-slate-700 backdrop-blur-md shadow-2xl">
              <p className="text-4xl text-slate-200 leading-relaxed font-medium">
                {renderHighlighted(description)}
              </p>
            </div>
          )}

          {/* 3. DETALLE TÉCNICO (Terminal más imponente) */}
          {type === 'detail' && (
            <div className="bg-[#0D1117] p-12 rounded-2xl border border-slate-700 shadow-2xl flex-grow flex flex-col min-h-[500px]">
              <div className="flex gap-3 mb-10 border-b border-slate-800 pb-6">
                <div className="w-6 h-6 rounded-full bg-red-500"></div>
                <div className="w-6 h-6 rounded-full bg-yellow-500"></div>
                <div className="w-6 h-6 rounded-full bg-green-500"></div>
              </div>
              <p className="text-[2.2rem] text-slate-200 leading-relaxed font-mono">
                <span className={`${detailPromptClass} font-bold`}>root@cyberpulse:~#</span> ./analyze<br /><br />
                <span className="text-slate-400"> </span>{renderHighlighted(description)}
              </p>
            </div>
          )}

          {type === 'command_pair' && (
            <div className="flex flex-col gap-6">
              {summary.map((item, index) => (
                <div key={index} className="bg-[#0D1117] p-8 rounded-2xl border border-slate-700 shadow-2xl">
                  <div className="flex gap-3 mb-5 border-b border-slate-800 pb-4">
                    <div className="w-5 h-5 rounded-full bg-red-500"></div>
                    <div className="w-5 h-5 rounded-full bg-yellow-500"></div>
                    <div className="w-5 h-5 rounded-full bg-green-500"></div>
                  </div>
                  <p className="text-[1.8rem] text-slate-200 leading-relaxed font-mono">
                    <span className={`${detailPromptClass} font-bold`}>root@cyberpulse:~#</span>{' '}
                    {item.sintaxis}
                  </p>
                  <p className="text-2xl text-slate-300 leading-snug mt-4">
                    {item.explicacion}
                  </p>
                </div>
              ))}
            </div>
          )}

          {type === 'checklist_steps' && (
            <div className="flex flex-col gap-6">
              {summary.map((item, index) => (
                <div key={index} className={`flex items-center gap-6 p-8 rounded-2xl border ${theme.border} ${theme.bg} shadow-2xl`}>
                  <div className={`flex-shrink-0 w-16 h-16 rounded-xl border-2 ${theme.border} flex items-center justify-center`}>
                    <svg className={`w-9 h-9 ${theme.text}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <p className="text-4xl text-slate-200 leading-snug font-medium">
                    {item.paso}
                  </p>
                </div>
              ))}
            </div>
          )}

          {type === 'pro_tip' && (
            <div className={`p-12 rounded-3xl border ${theme.border} ${theme.bg} shadow-2xl`}>
              <p className="text-4xl text-slate-200 leading-relaxed font-medium">
                {renderHighlighted(description)}
              </p>
            </div>
          )}

          {type === 'recap' && (
            <div className="flex flex-col gap-5">
              {summary.map((item, index) => (
                <div key={index} className="flex items-start gap-5 bg-slate-900/80 p-6 rounded-2xl border border-slate-700">
                  <span className={`font-mono text-2xl font-bold ${theme.text}`}>{index + 1}</span>
                  <div>
                    <p className={`font-mono text-2xl font-bold ${theme.text}`}>{item.sintaxis}</p>
                    <p className="text-2xl text-slate-300 leading-snug mt-2">{item.explicacion}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* 4. EL IMPACTO */}
          {type === 'impact' && (
            <>
              <p className="text-4xl text-slate-300 leading-snug mb-10">{renderHighlighted(description)}</p>
              <div className="grid grid-cols-1 gap-8">
                {summary.map((risk, index) => (
                  <div key={index} className={`flex items-center gap-8 p-8 rounded-2xl border shadow-lg transition-colors ${impactCardClass}`}>
                    <div className={`${impactIconClass} flex-shrink-0`}>
                      <svg className="w-14 h-14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    </div>
                    <p className="text-4xl text-slate-200 leading-snug">{renderHighlighted(risk)}</p>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* 5. MITIGACIÓN */}
          {type === 'mitigation' && (
            <>
              <p className="text-4xl text-slate-300 leading-snug mb-10">{renderHighlighted(description)}</p>
              <div className="flex flex-col gap-8">
                {summary.map((step, index) => (
                  <div key={index} className="flex items-center gap-8 bg-slate-900/80 p-8 rounded-2xl border-l-8 shadow-lg" style={{ borderLeftColor: theme.border.replace('border-', '') }}>
                    <div className={`flex-shrink-0 w-14 h-14 rounded-full ${theme.bg} border-2 ${theme.border} flex items-center justify-center`}>
                      <svg className={`w-8 h-8 ${theme.text}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
                    </div>
                    <p className="text-4xl text-slate-200 font-medium leading-snug">{renderHighlighted(step)}</p>
                  </div>
                ))}
              </div>
            </>
          )}

        </div>
      </div>

      {/* PIE DE PÁGINA */}
      <div className="z-10 border-t border-slate-800 pt-8 flex justify-between items-center text-slate-400 text-2xl mb-4">
        <p className="font-medium">@CyberPulse89</p>

        <p className="text-slate-500 font-mono tracking-widest text-2xl bg-slate-900 px-6 py-2 rounded-full border border-slate-800">
          {currentSlide} / {totalSlides}
        </p>

        {type !== 'mitigation' ? (
          <p className="flex items-center gap-4 text-white animate-pulse font-bold tracking-widest text-2xl">
            DESLIZA
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
          </p>
        ) : (
          <p className={`flex items-center gap-4 text-white font-bold tracking-widest text-2xl ${saveTextClass}`}>
            GUARDA ESTE POST
            <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24"><path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path></svg>
          </p>
        )}
      </div>
    </div>
  );
};

export default PostInstagram;