import test from 'node:test';
import assert from 'node:assert/strict';
import { readSupportVisual } from '../src/alert-support-data.js';

const source = 'https://www.mozilla.org/en-US/security/advisories/mfsa2026-106/';
const visual = JSON.stringify({ tipo: 'firefox_version', version: '158' });

test('versión explícita con aviso de Mozilla', () => {
  assert.equal(readSupportVisual(visual, source).version, '158');
});

test('datos ausentes, dominios engañosos y texto arbitrario no dibujan versiones', () => {
  assert.equal(readSupportVisual('{}', source), null);
  assert.equal(readSupportVisual('null', source), null);
  assert.equal(readSupportVisual('{', source), null);
  assert.equal(readSupportVisual(visual, 'https://mozilla.org.attacker.invalid/en-US/security/advisories/'), null);
  assert.equal(readSupportVisual(JSON.stringify({ tipo: 'firefox_version', version: '<script>' }), source), null);
});
