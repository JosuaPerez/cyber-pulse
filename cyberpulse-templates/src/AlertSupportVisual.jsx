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

export function IsolationVisual() {
  return <figure className="daily-isolation"><svg viewBox="0 0 860 170" role="img" aria-label="Una máquina virtual, un límite de aislamiento y el equipo anfitrión"><rect x="10" y="25" width="245" height="110" rx="15" fill="#18333f" stroke="#55dce5" strokeWidth="2" /><text x="132" y="75" textAnchor="middle">MÁQUINA VIRTUAL</text><text className="isolation-sub" x="132" y="106" textAnchor="middle">Entorno invitado</text><path d="M290 80h265m-15-12 15 12-15 12" stroke="#ffc476" strokeWidth="4" fill="none" /><path d="M420 12v138" stroke="#55dce5" strokeWidth="2" strokeDasharray="7 8" /><rect x="595" y="25" width="255" height="110" rx="15" fill="#18333f" stroke="#55dce5" strokeWidth="2" /><text x="722" y="75" textAnchor="middle">EQUIPO ANFITRIÓN</text><text className="isolation-sub" x="722" y="106" textAnchor="middle">Ejecuta las VM</text></svg><figcaption>Esquema ilustrativo del escape descrito. No demuestra que tu equipo esté afectado.</figcaption></figure>;
}

export function IsolationScope() {
  return <div className="daily-isolation-scope"><div><small>SI ADMINISTRAS EL ANFITRIÓN</small><p>Revisa el aviso y su corrección.</p></div><div><small>SI USAS UN PROVEEDOR</small><p>Consulta el estado con su soporte.</p></div><span>Roles orientativos, no una comprobación de exposición.</span></div>;
}
