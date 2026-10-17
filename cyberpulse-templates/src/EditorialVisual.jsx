export default function EditorialVisual({ visual, summary, policy = false }) {
  if (policy) {
    return <figure className="editorial-visual editorial-policy"><small>EL PUNTO DE REVISIÓN ES LA ORGANIZACIÓN</small><div className="editorial-nodes"><div><b>01</b><span>Personas</span></div><div><b>02</b><span>Herramientas</span></div><div><b>03</b><span>Políticas de uso</span></div></div><figcaption>Ámbitos para revisar, no una cadena de ataque ni evidencia de una brecha.</figcaption></figure>;
  }
  if (visual && ['cadena', 'comparacion'].includes(visual.clase)) {
    return <figure className="editorial-visual"><small>{visual.clase === 'cadena' ? 'CÓMO OCURRIÓ · ESQUEMA' : 'ELEMENTOS DEL CASO · COMPARACIÓN'}</small><div className="editorial-nodes">{visual.nodos.map((node, i) => <div key={i}><b>{String(i + 1).padStart(2, '0')}</b><span>{node}</span>{i < visual.nodos.length - 1 && <em aria-hidden="true">{visual.clase === 'cadena' ? '→' : '↔'}</em>}</div>)}</div><figcaption>Ilustración del caso descrito, no una prueba sobre tu dispositivo.</figcaption></figure>;
  }
  return <figure className="editorial-visual editorial-map"><small>EL HALLAZGO Y TU SITUACIÓN SON COSAS DISTINTAS</small><div><article><svg viewBox="0 0 80 80" aria-hidden="true"><path d="M20 8h30l12 12v51H20Z M30 34h22 M30 45h22 M30 56h14" /></svg><strong>LA FUENTE REPORTA</strong><p>{summary}</p></article><span aria-hidden="true">≠</span><article><svg viewBox="0 0 80 80" aria-hidden="true"><rect x="8" y="12" width="64" height="44" rx="4"/><path d="M40 56v12 M23 68h34"/></svg><strong>TU DISPOSITIVO</strong><p>No lo hemos evaluado.<br />Comprueba el alcance antes de asumir exposición.</p></article></div><figcaption>Mapa de lectura: no representa una cadena de ataque.</figcaption></figure>;
}
