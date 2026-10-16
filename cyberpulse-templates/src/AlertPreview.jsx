import './alert-preview.css';

const variants = {
  update: { label: 'ACTUALIZACIONES', number: '01', accent: '#55dce5', title: <>Una actualización.<br />Menos riesgo.</>, sub: 'Si usas la aplicación afectada, revisa tu versión antes de seguir.', next: '¿Te afecta? →' },
  scam: { label: 'SEÑALES DE ESTAFA', number: '02', accent: '#ffc476', title: <>Un correo urgente.<br />Una trampa posible.</>, sub: 'La presión para actuar puede ser una señal. Mira qué comprobar.', next: 'Reconoce las señales →' },
  context: { label: 'NOTICIAS EN CLARO', number: '03', accent: '#b5a2ff', title: <>¿Filtración o<br />cuenta comprometida?</>, sub: 'No son lo mismo. Entender la diferencia cambia qué debes revisar.', next: 'Entiende el impacto →' },
  actions: { label: 'QUÉ HACER', number: '04', accent: '#55dce5', title: <>Menos alarma.<br />Más acciones.</>, sub: 'Una alerta útil debe ayudarte a decidir, no solo a preocuparte.', next: 'Verifica la fuente →' },
};

function Pulse() {
  return <svg viewBox="0 0 60 60" fill="none" aria-hidden="true"><path d="M2 30h12l8-18 13 36 8-18h15" stroke="currentColor" strokeWidth="4" strokeLinejoin="round" /></svg>;
}

function UpdateVisual() {
  return <div className="alert-update">
    <div className="alert-app"><div className="alert-app-icon"><Pulse /></div><div><small>PRODUCTO AFECTADO</small><strong>App de ejemplo</strong><span>La versión importa, no solo el nombre.</span></div></div>
    <div className="alert-version"><div><small>ANTES</small><strong>Versión afectada</strong><span>Confirma si la usas</span></div><b aria-hidden="true">→</b><div><small>DESPUÉS</small><strong>Versión corregida</strong><span>Según aviso oficial</span></div></div>
    <div className="alert-note"><span>01</span><p>Revisa el aviso del proveedor.<br /><strong>Actualiza solo desde el canal oficial.</strong></p></div>
  </div>;
}

function ScamVisual() {
  return <div className="alert-scam">
    <div className="alert-mail"><div className="alert-mail-top"><span>MENSAJE DE EJEMPLO</span><span>✉</span></div><small>De: soporte@cuenta-segura.invalid</small><h3>Tu cuenta será suspendida</h3><p>“Tienes 10 minutos para verificar tu acceso.”</p><div className="alert-fake-button">VERIFICAR AHORA</div></div>
    <div className="alert-signals"><div><b>01</b><span>¿Quién lo envía?</span></div><div><b>02</b><span>¿Por qué tanta prisa?</span></div><div><b>03</b><span>¿Adónde lleva el enlace?</span></div></div>
    <p className="alert-verify">No decidas por el logo: abre la app o el sitio oficial por tu cuenta.</p>
  </div>;
}

function ContextVisual() {
  return <div className="alert-context">
    <div className="alert-definition"><span>A</span><div><h3>Datos expuestos</h3><p>Información sale del lugar donde debía estar protegida.</p></div></div>
    <div className="alert-not-equal">≠ <span>NO IMPLICA AUTOMÁTICAMENTE</span></div>
    <div className="alert-definition"><span>B</span><div><h3>Acceso a tu cuenta</h3><p>Alguien entra o controla una cuenta sin autorización.</p></div></div>
    <div className="alert-context-note">Pueden estar relacionados.<br /><strong>El aviso oficial define el alcance.</strong></div>
  </div>;
}

function ActionsVisual() {
  const steps = [
    ['Confirma si te afecta', 'Producto, versión y condiciones del aviso.'],
    ['Aplica la medida indicada', 'Usa las instrucciones del proveedor.'],
    ['Comprueba el resultado', 'Verifica que el cambio quedó aplicado.'],
  ];
  return <div className="alert-actions">{steps.map(([title, text], i) => <div key={title}><b>0{i + 1}</b><section><h3>{title}</h3><p>{text}</p></section></div>)}<aside><small>EN UNA ALERTA REAL INCLUIREMOS</small><p>Fuente oficial · fecha · alcance confirmado</p></aside></div>;
}

export default function AlertPreview({ variant = 'update' }) {
  const selected = Object.hasOwn(variants, variant) ? variant : 'update';
  const data = variants[selected];
  return <main className={`alert-preview alert-preview-${selected}`} style={{ '--alert-accent': data.accent }}>
    <header><div><Pulse /><span>CyberPulse</span></div><span>ALERTAS EN CLARO</span></header>
    <div className="alert-heading"><div className="alert-eyebrow"><span>{data.label}</span><span>FORMATO {data.number}</span></div><h1>{data.title}</h1><p>{data.sub}</p></div>
    <div className="alert-body">{selected === 'update' ? <UpdateVisual /> : selected === 'scam' ? <ScamVisual /> : selected === 'context' ? <ContextVisual /> : <ActionsVisual />}</div>
    <div className="alert-demo">DEMO EDITORIAL · NO ES UNA ALERTA REAL</div>
    <footer><span>@cyberpulse89</span><strong>{data.next}</strong></footer>
  </main>;
}
