function BrowserIcon() {
  return <svg viewBox="0 0 80 80" fill="none" aria-hidden="true"><circle cx="40" cy="40" r="32" stroke="currentColor" strokeWidth="3" /><ellipse cx="40" cy="40" rx="16" ry="32" stroke="currentColor" strokeWidth="3" /><path d="M8 40h64M15 22h50M15 58h50" stroke="currentColor" strokeWidth="3" /></svg>;
}

export function ReleaseVisual({ version }) {
  return <div className="daily-release"><BrowserIcon /><div><small>FIREFOX · VERSIÓN CORREGIDA DEL AVISO</small><strong>{version}</strong><span>Compárala con la versión que tienes instalada.</span></div></div>;
}

export function ScopeVisual({ version }) {
  return <div className="daily-version-check"><div><small>EN TU EQUIPO</small><strong>Comprueba<br />tu versión</strong></div><span aria-hidden="true">↔</span><div><small>CORREGIDA EN EL AVISO</small><strong>{version}</strong></div></div>;
}

export function AboutFirefoxMockup({ version }) {
  return <figure className="daily-about"><div className="daily-window-bar"><span>● ● ●</span><strong>Acerca de Firefox</strong></div><div className="daily-window-body"><BrowserIcon /><div><strong>Firefox</strong><p>Versión <mark>{version}</mark><span>← revisa este número</span></p></div></div><figcaption>Vista ilustrativa · versión corregida del aviso, no la de tu equipo.</figcaption></figure>;
}
