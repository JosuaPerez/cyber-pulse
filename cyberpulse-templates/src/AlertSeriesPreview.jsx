import DailyAlert from './DailyAlert';
import './alert-series-preview.css';

const examples = {
  update: [
    { type: 'cover', title: 'Una actualización. Menos riesgo.', description: 'En este caso ficticio, una app recibe una corrección. La versión instalada define si debes actuar.' },
    { type: 'problem', title: 'Primero, revisa si te afecta', description: 'El aviso de ejemplo describe un fallo en una app. No todas las instalaciones estarían afectadas: hay que revisar producto, versión y condiciones antes de aplicar una medida.' },
    { type: 'detail', title: 'Qué se corrigió', description: 'Una validación de entradas defectuosa puede permitir comportamientos no previstos. Una corrección cambia esa validación; actualizar no sustituye comprobar el alcance del aviso.' },
    { type: 'impact', title: 'El alcance cambia el riesgo', description: 'Lo que habría que confirmar en un aviso real', summary: ['Qué versiones y funciones están afectadas.', 'Si el fallo exige condiciones o permisos específicos.', 'Qué evidencia existe de explotación.'] },
    { type: 'mitigation', title: 'Actualiza con criterio', description: 'Tres pasos para pasar de la noticia a la acción', summary: ['Consulta el aviso y confirma la versión instalada.', 'Aplica la corrección desde el canal oficial del proveedor.', 'Comprueba la versión final y los pasos adicionales del aviso.'] },
  ],
  context: [
    { type: 'cover', title: 'Datos expuestos: ¿qué significa?', description: 'Un incidente no prueba por sí solo que alguien entró en tu cuenta. Importa qué datos quedaron expuestos.' },
    { type: 'problem', title: 'La noticia necesita contexto', description: 'Imaginemos un incidente donde se exponen nombres y correos. Eso no permite afirmar que también salieron contraseñas o que hubo accesos a cuentas. Son hechos distintos que requieren confirmación.' },
    { type: 'detail', title: 'No todas las filtraciones son iguales', description: 'El tipo de dato, su protección y quién pudo acceder cambian el impacto. Una investigación puede ampliar o corregir lo que se sabe; conviene separar hechos confirmados de preguntas abiertas.' },
    { type: 'impact', title: 'Qué cambia para ti', description: 'Posibles consecuencias según los datos afectados', summary: ['Correos expuestos pueden facilitar mensajes engañosos dirigidos.', 'Credenciales expuestas requieren revisar accesos y reutilización.', 'No podemos asumir robo de cuenta sin evidencia de acceso.'] },
    { type: 'mitigation', title: 'Actúa según lo confirmado', description: 'Evita respuestas automáticas a un titular', summary: ['Consulta el aviso y qué datos de tu cuenta están afectados.', 'Sigue las medidas específicas indicadas por la organización.', 'Verifica mensajes sobre el incidente por un canal conocido.'] },
  ],
};

function VersionFlow() {
  return <div className="series-version"><article><small>COMPRUEBA</small><strong>Tu versión</strong><p>¿Está en el alcance?</p></article><span aria-hidden="true">→</span><article><small>VERIFICA</small><strong>La corrección</strong><p>Según el proveedor</p></article></div>;
}

function ScopeFlow() {
  return <div className="series-scope"><article><span>01</span><strong>Producto</strong></article><article><span>02</span><strong>Versión</strong></article><article><span>03</span><strong>Condiciones</strong></article><p>El aviso define el alcance. No lo deduzcas solo del titular.</p></div>;
}

function DataFlow({ detail = false }) {
  return <div className="series-data"><article><small>{detail ? 'HECHO CONFIRMADO' : 'DATOS EXPUESTOS'}</small><strong>{detail ? 'Qué se sabe' : 'Información fuera de su lugar'}</strong></article><div className="series-separator"><b>≠</b><span>{detail ? 'SEPARAR DE' : 'NO DEMUESTRA POR SÍ SOLO'}</span></div><article><small>{detail ? 'PREGUNTA ABIERTA' : 'ACCESO A CUENTAS'}</small><strong>{detail ? 'Qué falta por confirmar' : 'Entrada sin autorización'}</strong></article></div>;
}

export default function AlertSeriesPreview({ variant, slide }) {
  const selected = Object.hasOwn(examples, variant) ? variant : 'update';
  const parsedSlide = Number(slide);
  const index = Number.isInteger(parsedSlide) && parsedSlide >= 1 && parsedSlide <= 5 ? parsedSlide - 1 : 0;
  return <DailyAlert {...examples[selected][index]} level="demo" currentSlide={index + 1} totalSlides={5}
    layout={selected} seriesLabel={selected === 'update' ? 'ACTUALIZACIONES' : 'NOTICIAS EN CLARO'}
    sourceName="DEMO EDITORIAL · NO ES UNA ALERTA REAL" sourceUrl="" exploitation="desconocido"
    coverVisual={selected === 'update' ? <VersionFlow /> : <DataFlow />}
    detailVisual={selected === 'update' ? <ScopeFlow /> : <DataFlow detail />} />;
}
