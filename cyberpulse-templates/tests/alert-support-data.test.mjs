import test from 'node:test';
import assert from 'node:assert/strict';
import { readSupportVisual, readEditorial } from '../src/alert-support-data.js';

const source = 'https://www.mozilla.org/en-US/security/advisories/mfsa2026-106/';
const visual = JSON.stringify({ tipo: 'firefox_version', version: '158' });

test('versión explícita con aviso de Mozilla', () => {
  assert.equal(readSupportVisual(visual, source).version, '158');
});

test('diagrama de aislamiento solo por tipo explícito, sin textos arbitrarios ni versión de Firefox', () => {
  assert.deepEqual(readSupportVisual(JSON.stringify({ tipo: 'vm_isolation', version: '158', label: '<script>' }), 'https://example.org/research'), { tipo: 'vm_isolation' });
  assert.equal(readSupportVisual('{"tipo":"vm_isolation"}', 'http://example.org'), null);
  assert.equal(readSupportVisual('{"tipo":"unknown"}', source), null);
});

test('datos ausentes, dominios engañosos y texto arbitrario no dibujan versiones', () => {
  assert.equal(readSupportVisual('{}', source), null);
  assert.equal(readSupportVisual('null', source), null);
  assert.equal(readSupportVisual('{', source), null);
  assert.equal(readSupportVisual(visual, 'https://mozilla.org.attacker.invalid/en-US/security/advisories/'), null);
  assert.equal(readSupportVisual(JSON.stringify({ tipo: 'firefox_version', version: '<script>' }), source), null);
});

test('visual común valida clase y nodos; un contrato incompleto usa resumen', () => {
  assert.equal(readSupportVisual('{"tipo":"editorial","clase":"cadena","nodos":["Anuncio","Dispositivo"]}', source).clase, 'cadena');
  assert.equal(readSupportVisual('{"tipo":"editorial","clase":"cadena","nodos":["Uno"]}', source).clase, 'resumen');
  assert.equal(readSupportVisual('{"tipo":"editorial","clase":"arbitraria"}', source).clase, 'resumen');
  assert.equal(readSupportVisual('{"tipo":"editorial"}', 'javascript:alert(1)'), null);
});

test('datos editoriales admiten solo audiencias y temporalidad conocidas', () => {
  const e = { audiencia: 'mixta', temporalidad: 'historica', limite: 'No confirma que tu dispositivo esté afectado.' };
  assert.equal(readEditorial(JSON.stringify(e)).temporalidad, 'historica');
  assert.equal(readEditorial('{'), null);
  assert.equal(readEditorial('{}'), null);
  assert.equal(readEditorial(JSON.stringify({ ...e, temporalidad: 'activa_ahora' })), null);
});
