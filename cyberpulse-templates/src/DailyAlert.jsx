import './daily-alert.css';
import './alert-series-preview.css';
import './alert-support-visual.css';
import { AboutFirefoxMockup, ReleaseVisual, ScopeVisual } from './AlertSupportVisual';
import { readSupportVisual } from './alert-support-data';

const sections = { cover: 'LO ESENCIAL', scope: '¿TE AFECTA?', context_risks: 'CONTEXTO Y FUENTE', problem: 'QUÉ PASÓ', detail: 'BAJO LA LUPA', impact: 'QUÉ ESTÁ EN RIESGO', mitigation: 'QUÉ HACER' };
const severities = { critical: ['CRÍTICA', '#ff8f93'], high: ['ALTA', '#ffc476'], medium: ['MEDIA', '#c8d4e9'] };
const exploitationLabels = { explotacion_activa: 'Explotación activa reportada', exploit_publico: 'Exploit público reportado', sin_evidencia: 'Sin evidencia reportada de explotación', desconocido: 'Explotación: estado desconocido' };

function Text({ children = '' }) {
  return String(children).split('*').map((part, i) => i % 2 ? <strong key={i}>{part}</strong> : part);
}

function sourceHost(url) {
  try {
    const parsed = new URL(url);
    return ['https:', 'http:'].includes(parsed.protocol) ? parsed.hostname : '';
  } catch { return ''; }
}

function identifiers(value) {
  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed.filter(item => typeof item === 'string' && /^CVE-\d{4}-\d{4,7}$/i.test(item)).slice(0, 3) : [];
  } catch { return []; }
}

export default function DailyAlert({ type, level, title, description, summary = [], currentSlide = 1, totalSlides = 5, sourceName = '', sourceUrl = '', exploitation = 'desconocido', cves = '[]', layout = 'editorial', seriesLabel = 'ALERTAS DIARIAS', coverVisual = null, detailVisual = null, sourceDate = '', statusText = '', reviewLabel = '', preparedOn = '', supportVisual = '{}' }) {
  const severity = Object.hasOwn(severities, level) ? severities[level] : ['SIN CLASIFICAR', '#c8d4e9'];
  const section = Object.hasOwn(sections, type) ? sections[type] : 'EN CONTEXTO';
  const status = statusText || (Object.hasOwn(exploitationLabels, exploitation) ? exploitationLabels[exploitation] : exploitationLabels.desconocido);
  const points = Array.isArray(summary) ? summary.filter(item => typeof item === 'string').slice(0, 3) : [];
  const ids = identifiers(cves);
  const host = sourceHost(sourceUrl);
  const safeLayout = ['update', 'context'].includes(layout) ? layout : 'editorial';
  const compact = safeLayout === 'update' && totalSlides === 4;
  const visual = compact ? readSupportVisual(supportVisual, sourceUrl) : null;
  return <main className={`daily-alert daily-alert-${type} daily-layout-${safeLayout}${compact ? ' daily-compact' : ''}${visual ? ' daily-has-visual' : ''}`}>
    <header><div><svg viewBox="0 0 60 60" fill="none" aria-hidden="true"><path d="M2 30h12l8-18 13 36 8-18h15" stroke="currentColor" strokeWidth="4" strokeLinejoin="round" /></svg><span>CyberPulse</span></div><span>{seriesLabel}</span></header>
    <div className="daily-eyebrow"><span>{section}</span><span style={{ color: severity[1] }}>SEVERIDAD {severity[0]}</span></div>
    <h1><Text>{title}</Text></h1>
    <div className="daily-content">
      {type === 'cover' ? <>
        <article className="daily-paper"><div className="daily-paper-label"><span>RESUMEN DEL AVISO</span><span aria-hidden="true">↗</span></div><p><Text>{description}</Text></p><small>{status}</small></article>
        {visual && <ReleaseVisual version={visual.version} />}
        {coverVisual || (safeLayout === 'update' ? <p className="daily-next-step">Primero revisa si te afecta.<br /><strong>Las medidas están en la diapositiva {totalSlides}.</strong></p> : <><div className="daily-guide"><div><b>01</b><span>Entiende<br />lo que pasó</span></div><div><b>02</b><span>Revisa<br />si te afecta</span></div><div><b>03</b><span>Aplica<br />las medidas</span></div></div><p className="daily-prompt">La noticia, su contexto y qué puedes hacer.</p></>)}
      </> : type === 'scope' ? <>
        <article className="daily-paper"><div className="daily-paper-label"><span>CONTEXTO Y ALCANCE REPORTADOS</span></div><p><Text>{description}</Text></p></article>
        {visual && <ScopeVisual version={visual.version} />}
        <p className="daily-next-step">Comprueba si el producto o la situación coincide con tu caso. Si falta información, consulta la fuente antes de asumir que estás afectado.</p>
      </> : type === 'context_risks' ? <>
        <article className="daily-paper daily-technical"><div className="daily-paper-label"><span>DETALLE DEL ANÁLISIS</span></div><p><Text>{description}</Text></p></article>
        <div className="daily-context-risks"><small>RIESGOS DEL ANÁLISIS</small>{points.map((point, index) => <p key={index}><b>{index + 1}</b><span><Text>{point}</Text></span></p>)}</div>
        {ids.length > 0 && <p className="daily-cves">{ids.join(' · ')}</p>}
      </> : type === 'impact' || type === 'mitigation' ? <>
        <p className="daily-intro"><Text>{description}</Text></p>
        {visual && type === 'mitigation' && <AboutFirefoxMockup version={visual.version} />}
        <div className="daily-points">{points.length ? points.map((point, index) => <article key={index}><b>{type === 'mitigation' ? '✓' : `0${index + 1}`}</b><p><Text>{point}</Text></p></article>) : <p>Sin puntos disponibles en este análisis.</p>}</div>
        {compact && type === 'mitigation' && <p className="daily-save-action">{visual ? 'Guarda este post hasta confirmar que actualizaste.' : 'Guarda este post hasta revisar y aplicar las medidas.'}</p>}
      </> : <>
        <article className={`daily-paper ${type === 'detail' ? 'daily-technical' : ''}`}><div className="daily-paper-label"><span>{type === 'detail' ? 'DETALLE DEL ANÁLISIS' : 'CONTEXTO DEL AVISO'}</span><span aria-hidden="true">{type === 'detail' ? '</>' : '↗'}</span></div><p><Text>{description}</Text></p></article>
        {type === 'detail' && (detailVisual || <div className="daily-evidence"><small>REFERENCIAS EN LOS DATOS</small><div>{ids.length ? ids.map(id => <span key={id}>{id}</span>) : <span>Sin identificador CVE aportado</span>}</div><p>{status}</p></div>)}
      </>}
    </div>
    <aside className="daily-source"><span>{reviewLabel || 'FUENTE DEL AVISO'}{preparedOn ? ` · PREPARADO ${preparedOn} UTC` : ''}</span><strong>{sourceName || 'No indicada en los datos'}{sourceDate ? ` · ${sourceDate}` : ''}</strong><small>{host || 'Sin enlace de fuente aportado'}</small></aside>
    <footer><span>@cyberpulse89</span><span>{currentSlide} / {totalSlides}</span><strong>{compact && currentSlide === totalSlides ? 'GUÁRDALO PARA REVISAR' : currentSlide === totalSlides ? 'Consulta la fuente →' : 'Continúa →'}</strong></footer>
  </main>;
}
