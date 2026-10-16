import DailyAlert from './DailyAlert';
import examples from './content/real-alerts.json';
import './alert-series-preview.css';

function UpdateFlow() {
  return <div className="series-version"><article><small>COMPRUEBA</small><strong>Tu Firefox</strong><p>Versión instalada</p></article><span aria-hidden="true">→</span><article><small>AVISO DE MOZILLA</small><strong>158</strong><p>Versión corregida</p></article></div>;
}

function IncidentFlow() {
  return <div className="series-data"><article><small>DATOS AFECTADOS</small><strong>Información del soporte</strong></article><div className="series-separator"><b>≠</b><span>NO EQUIVALE A</span></div><article><small>EXCLUIDOS SEGÚN DISCORD</small><strong>Contraseñas y autenticación</strong></article></div>;
}

export default function RealAlertPreview({ variant, slide }) {
  const selected = Object.hasOwn(examples, variant) ? variant : 'update';
  const data = examples[selected];
  const parsed = Number(slide);
  const index = Number.isInteger(parsed) && parsed >= 1 && parsed <= 5 ? parsed - 1 : 0;
  return <DailyAlert {...data} {...data.slides[index]} currentSlide={index + 1} totalSlides={5}
    reviewLabel="PRUEBA VISUAL · NOTICIA REAL · REVISADA 14/10/2026"
    coverVisual={selected === 'update' ? <UpdateFlow /> : selected === 'context' ? <IncidentFlow /> : null} />;
}
