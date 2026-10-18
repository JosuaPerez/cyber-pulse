export function readSupportVisual(value, sourceUrl) {
  try {
    const data = JSON.parse(value);
    const url = new URL(sourceUrl);
    if (data?.tipo === 'editorial' && url.protocol === 'https:') {
      if (['cadena', 'comparacion'].includes(data.clase) && Array.isArray(data.nodos) &&
          data.nodos.length >= 2 && data.nodos.length <= 3 &&
          data.nodos.every(n => typeof n === 'string' && n.trim().length >= 2 && n.length <= 26)) {
        return { tipo: 'editorial', clase: data.clase, nodos: data.nodos };
      }
      return { tipo: 'editorial', clase: 'resumen', nodos: [] };
    }
    if (data?.tipo === 'vm_isolation' && url.protocol === 'https:') return { tipo: 'vm_isolation' };
    if (data?.tipo === 'firefox_version' && typeof data.version === 'string' &&
        /^\d{1,3}(?:\.\d{1,3}){0,3}$/.test(data.version) && url.protocol === 'https:' &&
        ['mozilla.org', 'www.mozilla.org'].includes(url.hostname) &&
        url.pathname.startsWith('/en-US/security/advisories/')) return data;
  } catch { /* Sin datos comprobables no se dibuja una versión. */ }
  return null;
}

export function readEditorial(value) {
  try {
    let e = JSON.parse(value);
    if (typeof e?.resumen_hallazgo === 'string') {
      e = { ...e, limite: e.lo_que_no_podemos_concluir, alcance: e.a_quien_concierne };
    }
    if (!e || !['general', 'administradores', 'mixta'].includes(e.audiencia) ||
        !['historica', 'vigencia_no_confirmada'].includes(e.temporalidad) ||
        typeof e.limite !== 'string' || e.limite.length < 15 || e.limite.length > 100) return null;
    const tipo = e.tipo_noticia ?? 'incidente';
    if (!['incidente', 'vulnerabilidad', 'riesgo_operativo'].includes(tipo)) return null;
    return { tipo_noticia: tipo, audiencia: e.audiencia, temporalidad: e.temporalidad, limite: e.limite,
      nota_vigencia: typeof e.nota_vigencia === 'string' && e.nota_vigencia.length <= 110 ? e.nota_vigencia : '',
      alcance: typeof e.alcance === 'string' && e.alcance.length <= 240 ? e.alcance : '' };
  } catch { return null; }
}

export function editorialLabels(e) {
  const policy = e?.tipo_noticia === 'riesgo_operativo';
  return {
    policy,
    context: policy ? 'RIESGO OPERATIVO' : null,
    status: e?.nota_vigencia || (policy ? 'Prácticas y políticas de uso; no confirma una brecha en tu organización.' :
      e?.temporalidad === 'historica' ? 'Hechos pasados documentados; actividad actual no confirmada.' :
        'Vigencia actual sin confirmar: consulta el contexto de la fuente.'),
    scopePrompt: policy ? 'Identifica qué personas, herramientas y políticas intervienen en tu organización.' :
      'Comprueba las condiciones del caso antes de asumir que estás afectado.',
    reference: 'Consulta el informe original para conocer el contexto y sus límites.',
  };
}
