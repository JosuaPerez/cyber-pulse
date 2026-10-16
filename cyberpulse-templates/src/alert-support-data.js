export function readSupportVisual(value, sourceUrl) {
  try {
    const data = JSON.parse(value);
    const url = new URL(sourceUrl);
    if (data?.tipo === 'vm_isolation' && url.protocol === 'https:') return { tipo: 'vm_isolation' };
    if (data?.tipo === 'firefox_version' && typeof data.version === 'string' &&
        /^\d{1,3}(?:\.\d{1,3}){0,3}$/.test(data.version) && url.protocol === 'https:' &&
        ['mozilla.org', 'www.mozilla.org'].includes(url.hostname) &&
        url.pathname.startsWith('/en-US/security/advisories/')) return data;
  } catch { /* Sin datos comprobables no se dibuja una versión. */ }
  return null;
}
