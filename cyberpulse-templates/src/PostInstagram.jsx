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
  const educativoAccents = [
    { border: 'border-cyan-500', text: 'text-cyan-400', bg: 'bg-cyan-500/10', bgGlow: 'bg-cyan-500', solid: 'bg-cyan-500' },
    { border: 'border-sky-500', text: 'text-sky-400', bg: 'bg-sky-500/10', bgGlow: 'bg-sky-500', solid: 'bg-sky-500' },
    { border: 'border-teal-500', text: 'text-teal-400', bg: 'bg-teal-500/10', bgGlow: 'bg-teal-500', solid: 'bg-teal-500' },
    { border: 'border-violet-500', text: 'text-violet-400', bg: 'bg-violet-500/10', bgGlow: 'bg-violet-500', solid: 'bg-violet-500' },
  ];
  const accent = isEducativo && type !== 'cover'
    ? educativoAccents[(currentSlide - 2) % educativoAccents.length]
    : educativoTheme;
  const theme = isEducativo ? { ...educativoTheme, ...accent } : (themeColors[level] || themeColors.critical);
  const isTip = type === 'tip_content' || type === 'tip_bullets';
  const detailPromptClass = isEducativo ? accent.text : 'text-green-500';
  const educationalBodyClass = 'text-slate-200';
  const educationalSecondaryClass = isEducativo ? 'text-slate-200' : 'text-slate-300';
  const impactCardClass = isEducativo
    ? 'border-transparent'
    : 'bg-red-950/20 border-red-900/40 hover:bg-red-950/40';
  const impactIconClass = isEducativo ? accent.text : 'text-red-500';
  const saveTextClass = isEducativo ? 'text-cyan-400' : 'text-yellow-400';
  const isLastEducationalSlide = isEducativo && currentSlide === totalSlides;
  const closingMantras = {
    cheatsheet: 'Aprende la herramienta. Entiende la señal. Actúa mejor.',
    checklist_steps: 'Lo que revisas hoy, te protege mañana.',
    tip_bullets: 'Pausa. Verifica. Decide con criterio.',
    impact: 'Entender el riesgo es el primer paso para reducirlo.',
    mitigation: 'La defensa empieza con una decisión consciente.',
    recap: 'Quédate con la señal. Aplícala cuando importe.',
  };
  const closingMantra = closingMantras[type] || 'Aprende hoy. Protege mejor mañana.';
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
    <div className={`${isEducativo ? 'w-[1080px] h-[1350px] bg-[#050505]' : `w-[1080px] h-[1350px] bg-[#070B14] ${theme.glow}`} flex flex-col justify-between p-16 font-sans relative overflow-hidden`}>

      {/* BARRA DE PROGRESO */}
      <div className="absolute top-0 left-0 w-full h-3 bg-slate-900 z-50">
        <div className={`h-full ${theme.bgGlow} transition-all duration-300`} style={{ width: progressWidth }}></div>
      </div>

      {/* FONDO DE MALLA SUTIL */}
      {!isEducativo && (
        <div className="absolute inset-0 opacity-10 pointer-events-none"
          style={{ backgroundImage: 'linear-gradient(#334155 1px, transparent 1px), linear-gradient(90deg, #334155 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
        </div>
      )}

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
        <div className={isEducativo
          ? `text-sm ${theme.text} uppercase tracking-[0.3em] font-bold`
          : `px-6 py-2 rounded-full border-2 ${theme.border} ${theme.bg} ${theme.text} uppercase tracking-widest font-bold text-xl`}>
          {category}
        </div>
      </div>

      {/* CONTENEDOR CENTRAL: Aquí ocurre la magia del flujo.
        flex-1 y justify-center aseguran que todo el contenido flote en el medio de la imagen, llenando los vacíos.
      */}
      <div className="flex-1 flex flex-col justify-center w-full z-10 relative mt-8 mb-8">

        {/* EL "HILO" CONDUCTOR: Una línea vertical que conecta la historia (excepto en la portada) */}
        {type !== 'cover' && (
          <>
            {isEducativo && (
              <div className={`absolute right-0 top-0 ${type === 'command_pair' ? 'text-[14rem] opacity-[0.06]' : 'text-[18rem] opacity-[0.08]'} leading-none font-brand font-bold ${theme.text} pointer-events-none select-none`}>
                {currentSlide}
              </div>
            )}
            <div className={`absolute left-0 top-10 bottom-10 w-1 ${theme.bgGlow} opacity-30 rounded-full`}></div>
          </>
        )}

        <div className={type !== 'cover' ? "pl-12" : ""}>

          {/* 1. PORTADA MEJORADA (Con Fotografía de Fondo Integrada) */}
          {type === 'cover' && (
            <>
              {isEducativo ? (
                <div className="flex flex-col items-start text-left w-full relative z-10 pt-20">
                  <div className={`flex items-center gap-4 mb-10 ${theme.text}`}>
                    <svg className="w-12 h-12" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4 12h4l2-7 4 14 2-7h4" />
                    </svg>
                    <span className="text-xl uppercase tracking-[0.35em] font-bold">Idea práctica</span>
                  </div>
                  <div className={`w-24 h-1 ${theme.bgGlow} mb-8`}></div>
                  <h2 className="text-[5.5rem] font-brand font-bold text-white leading-tight">
                    {renderHighlighted(title)}
                  </h2>
                  <p className={`text-4xl ${educationalBodyClass} leading-snug mt-8 font-light max-w-[900px]`}>
                    {renderHighlighted(description)}
                  </p>
                </div>
              ) : (
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
            </>
          )}

          {/* TITULO ESTÁNDAR PARA SLIDES 2 AL 5 */}
          {type !== 'cover' && (
            <h2 className={isEducativo ? 'text-[4.5rem] font-brand font-bold text-white leading-tight mb-10 text-left' : 'text-[4.5rem] font-extrabold text-white leading-tight mb-10'}>
              {renderHighlighted(title)}
            </h2>
          )}

          {/* 2. EL PROBLEMA (TL;DR) */}
          {type === 'problem' && (
            <div className={isEducativo ? 'p-0' : 'bg-slate-900/80 p-12 rounded-3xl border border-slate-700 backdrop-blur-md shadow-2xl'}>
              <p className={`text-4xl ${educationalBodyClass} leading-relaxed font-medium ${isEducativo ? 'border-l-4 border-current pl-8' : ''}`}>
                {renderHighlighted(description)}
              </p>
            </div>
          )}

          {/* 3. DETALLE TÉCNICO (Terminal más imponente) */}
          {type === 'detail' && (
            <div className={isEducativo ? 'py-4' : 'bg-[#0D1117] p-12 rounded-2xl border border-slate-700 shadow-2xl flex-grow flex flex-col min-h-[500px]'}>
              {isEducativo ? (
                <p className={`text-4xl ${educationalBodyClass} leading-relaxed font-medium border-l-4 pl-8`} style={{ borderColor: 'currentColor' }}>
                  {renderHighlighted(description)}
                </p>
              ) : (
                <>
              <div className="flex gap-3 mb-10 border-b border-slate-800 pb-6">
                <div className="w-6 h-6 rounded-full bg-red-500"></div>
                <div className="w-6 h-6 rounded-full bg-yellow-500"></div>
                <div className="w-6 h-6 rounded-full bg-green-500"></div>
              </div>
              <p className="text-[2.2rem] text-slate-200 leading-relaxed font-mono">
                <span className={`${detailPromptClass} font-bold`}>root@cyberpulse:~#</span> ./analyze<br /><br />
                <span className="text-slate-400"> </span>{renderHighlighted(description)}
              </p>
                </>
              )}
            </div>
          )}

          {type === 'command_pair' && (
            <div className="flex flex-col gap-6">
              {summary.map((item, index) => (
                <div key={index} className={isEducativo ? 'border-l-4 pl-6 py-4' : 'bg-[#0D1117] p-8 rounded-2xl border border-slate-700 shadow-2xl'}>
                  {isEducativo ? (
                    <>
                      <p className={`text-[2rem] ${accent.text} leading-relaxed font-mono font-bold`}>{item.sintaxis}</p>
                      <p className={`text-3xl ${educationalBodyClass} leading-snug mt-3`}>{item.explicacion}</p>
                    </>
                  ) : (
                    <>
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
                    </>
                  )}
                </div>
              ))}
            </div>
          )}

          {type === 'checklist_steps' && (
            <div className="flex flex-col gap-6">
              {summary.map((item, index) => (
                <div key={index} className={isEducativo ? 'flex items-center gap-6 py-4' : `flex items-center gap-6 p-8 rounded-2xl border ${theme.border} ${theme.bg} shadow-2xl`}>
                  <div className={`flex-shrink-0 w-14 h-14 ${isEducativo ? `border-2 ${accent.border}` : `rounded-xl border-2 ${theme.border}`} flex items-center justify-center`}>
                    <svg className={`w-9 h-9 ${theme.text}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <p className={`text-4xl ${educationalBodyClass} leading-snug font-medium`}>
                    {item.paso}
                  </p>
                </div>
              ))}
            </div>
          )}

          {type === 'tip_content' && (
            <div className="flex flex-col gap-8">
              <p className={`text-4xl ${educationalBodyClass} leading-snug font-medium`}>
                {summary.texto}
              </p>
              <div className="flex flex-wrap gap-4">
                {summary.chips.map((chip, index) => (
                  <span key={index} className={`flex items-center gap-3 px-1 py-2 text-2xl font-bold tracking-wide ${index === 0 ? accent.text : 'text-slate-200'}`}>
                    <span className={`w-3 h-3 ${index === 0 ? accent.solid : 'bg-slate-500'}`}></span>
                    {chip.texto}
                  </span>
                ))}
              </div>
              <div className="grid grid-cols-2 gap-6">
                {summary.stats.map((stat, index) => (
                  <div key={index} className={`p-4 text-center ${index > 0 ? 'border-l border-slate-700' : ''}`}>
                    <p className={`text-6xl font-extrabold ${accent.text}`}>{stat.valor}</p>
                    <p className={`${isEducativo ? 'text-3xl' : 'text-2xl'} ${educationalBodyClass} leading-snug mt-3`}>{stat.etiqueta}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {type === 'tip_bullets' && (
            <div className="flex flex-col gap-6">
              {summary.map((bullet, index) => (
                <div key={index} className="flex items-center gap-6 py-4">
                  <div className={`flex-shrink-0 w-12 h-12 ${['bg-cyan-500', 'bg-sky-500', 'bg-teal-500', 'bg-violet-500'][index]}`}></div>
                  <p className={`text-4xl ${educationalBodyClass} leading-snug font-medium`}>{bullet}</p>
                </div>
              ))}
            </div>
          )}

          {type === 'pro_tip' && (
            <div className={isEducativo ? 'py-4 border-l-4 pl-8' : `p-12 rounded-3xl border ${theme.border} ${theme.bg} shadow-2xl`}>
              <p className={`text-4xl ${educationalBodyClass} leading-relaxed font-medium`}>
                {renderHighlighted(description)}
              </p>
            </div>
          )}

          {type === 'recap' && (
            <div className="flex flex-col gap-5">
              {summary.map((item, index) => (
                <div key={index} className={isEducativo ? 'flex items-start gap-5 py-4 border-b border-slate-800' : 'flex items-start gap-5 bg-slate-900/80 p-6 rounded-2xl border border-slate-700'}>
                  <span className={`font-mono text-2xl font-bold ${theme.text}`}>{index + 1}</span>
                  <div>
                    <p className={`font-mono text-2xl font-bold ${theme.text}`}>{item.sintaxis}</p>
                    <p className={`${isEducativo ? 'text-3xl' : 'text-2xl'} ${educationalSecondaryClass} leading-snug mt-2`}>{item.explicacion}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* 4. EL IMPACTO */}
          {type === 'impact' && (
            <>
              <p className={`text-4xl ${educationalSecondaryClass} leading-snug mb-10`}>{renderHighlighted(description)}</p>
              <div className="grid grid-cols-1 gap-8">
                {summary.map((risk, index) => (
                  <div key={index} className={isEducativo ? `flex items-center gap-8 py-4 transition-colors ${impactCardClass}` : `flex items-center gap-8 p-8 rounded-2xl border shadow-lg transition-colors ${impactCardClass}`}>
                    <div className={`${impactIconClass} flex-shrink-0`}>
                      <svg className="w-14 h-14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    </div>
                    <p className={`text-4xl ${educationalBodyClass} leading-snug`}>{renderHighlighted(risk)}</p>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* 5. MITIGACIÓN */}
          {type === 'mitigation' && (
            <>
              <p className={`text-4xl ${educationalSecondaryClass} leading-snug mb-10`}>{renderHighlighted(description)}</p>
              <div className="flex flex-col gap-8">
                {summary.map((step, index) => (
                  <div key={index} className={isEducativo ? 'flex items-center gap-8 py-4' : 'flex items-center gap-8 bg-slate-900/80 p-8 rounded-2xl border-l-8 shadow-lg'} style={isEducativo ? undefined : { borderLeftColor: theme.border.replace('border-', '') }}>
                    <div className={`flex-shrink-0 w-14 h-14 ${isEducativo ? `border-2 ${accent.border}` : `rounded-full ${theme.bg} border-2 ${theme.border}`} flex items-center justify-center`}>
                      <svg className={`w-8 h-8 ${theme.text}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
                    </div>
                    <p className={`text-4xl ${educationalBodyClass} font-medium leading-snug`}>{renderHighlighted(step)}</p>
                  </div>
                ))}
              </div>
            </>
          )}

        </div>
        {isLastEducationalSlide && (
          <p className={`mt-8 text-3xl font-brand font-bold tracking-wide ${accent.text}`}>
            {closingMantra}
          </p>
        )}
      </div>

      {/* PIE DE PÁGINA */}
      <div className="z-10 border-t border-slate-800 pt-8 flex justify-between items-center text-slate-400 text-2xl mb-4">
        <p className="font-medium">@CyberPulse89</p>

        <p className="text-slate-500 font-mono tracking-widest text-2xl bg-slate-900 px-6 py-2 rounded-full border border-slate-800">
          {currentSlide} / {totalSlides}
        </p>

        {isEducativo && isLastEducationalSlide ? (
          <div className="flex items-center gap-8">
            <p className="flex items-center gap-4 text-white font-bold tracking-widest text-2xl">
              GUARDA ESTE POST
              <svg className={`w-8 h-8 ${saveTextClass}`} fill="currentColor" viewBox="0 0 24 24"><path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path></svg>
            </p>
            <p className={`text-2xl font-bold tracking-widest ${theme.text}`}>SÍGUENOS PARA MÁS</p>
          </div>
        ) : type !== 'mitigation' ? (
          <p className={`flex items-center gap-4 text-white font-bold tracking-widest text-2xl ${isEducativo ? 'text-slate-500 tracking-[0.25em]' : 'animate-pulse'}`}>
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