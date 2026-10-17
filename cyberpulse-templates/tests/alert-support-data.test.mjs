import test from 'node:test';
import assert from 'node:assert/strict';
import { readSupportVisual, readEditorial, editorialLabels } from '../src/alert-support-data.js';

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

test('riesgo operativo tiene marco organizativo, sin severidad ni falsa vigencia de ataque', () => {
  const e = readEditorial(JSON.stringify({ tipo_noticia: 'riesgo_operativo', audiencia: 'mixta', temporalidad: 'vigencia_no_confirmada', limite: 'No demuestra una brecha en tu organización.' }));
  const labels = editorialLabels(e);
  assert.equal(labels.policy, true);
  assert.equal(labels.context, 'RIESGO OPERATIVO');
  assert.ok(!labels.status.includes('Vigencia'));
  assert.ok(!labels.reference.includes('indicadores'));
  assert.notEqual(labels.scopePrompt, e.limite);
  assert.equal(readEditorial(JSON.stringify({ ...e, tipo_noticia: 'arbitrario' })), null);
});

test('fichas anteriores conservan marco de incidente y el límite no se duplica en alcance', () => {
  const e = readEditorial(JSON.stringify({ audiencia: 'general', temporalidad: 'historica', limite: 'No demuestra una brecha en tu organización.' }));
  assert.equal(e.tipo_noticia, 'incidente');
  assert.equal(editorialLabels(e).context, null);
  assert.ok(editorialLabels(e).status.includes('pasados'));
  assert.notEqual(editorialLabels(e).scopePrompt, e.limite);
});
