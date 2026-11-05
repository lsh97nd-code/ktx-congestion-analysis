'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { test } = require('node:test');
const vm = require('node:vm');

const frontendDir = path.resolve(__dirname, '..');

function buildFixture(t, apiBaseUrl) {
  const fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'ktx-frontend-test-'));
  t.after(() => {
    assert.equal(path.dirname(fixture), path.resolve(os.tmpdir()));
    assert.ok(path.basename(fixture).startsWith('ktx-frontend-test-'));
    fs.rmSync(fixture, { recursive: true, force: true });
  });
  for (const entry of ['build.js', 'index.html', 'css', 'js']) {
    fs.cpSync(path.join(frontendDir, entry), path.join(fixture, entry), {
      recursive: true,
    });
  }
  const result = spawnSync(process.execPath, [path.join(fixture, 'build.js')], {
    env: { ...process.env, API_BASE_URL: apiBaseUrl },
    encoding: 'utf8',
  });
  return { fixture, result };
}

test('build emits runnable config and all relative script/style assets', (t) => {
  const { fixture, result } = buildFixture(t, ' https://example.test/backend/// ');
  assert.equal(result.status, 0, result.stderr);
  const outputDir = path.join(fixture, 'dist');
  const html = fs.readFileSync(path.join(outputDir, 'index.html'), 'utf8');
  for (const [, relativeAsset] of html.matchAll(/(?:src|href)="\.\/([^"]+)"/g)) {
    assert.ok(fs.existsSync(path.join(outputDir, relativeAsset)), relativeAsset);
  }
  const context = { window: {} };
  vm.runInNewContext(fs.readFileSync(path.join(outputDir, 'js/config.js'), 'utf8'), context);
  assert.equal(context.window.APP_CONFIG.API_BASE_URL, 'https://example.test/backend');
});

for (const apiBaseUrl of [
  '',
  'backend.example.test',
  'https:example.test',
  'http:/example.test',
  'ftp://example.test',
  'https://example.test?route=/api',
  'https://example.test#backend',
  'https://user:secret@example.test',
]) {
  test(`build rejects unusable API URL: ${apiBaseUrl || '(missing)'}`, (t) => {
    const { fixture, result } = buildFixture(t, apiBaseUrl);
    assert.equal(result.status, 1);
    assert.match(result.stderr, /API_BASE_URL/);
    assert.ok(!fs.existsSync(path.join(fixture, 'dist')));
  });
}

test('missing runtime config shows an error without starting API requests', () => {
  const elements = new Map();
  const listeners = new Map();
  let requestCount = 0;
  const document = {
    getElementById(id) {
      if (!elements.has(id)) {
        elements.set(id, {
          textContent: '',
          disabled: false,
          classList: { add() {}, remove() {} },
        });
      }
      return elements.get(id);
    },
    addEventListener(event, handler) { listeners.set(event, handler); },
  };
  vm.runInNewContext(fs.readFileSync(path.join(frontendDir, 'js/app.js'), 'utf8'), {
    window: {},
    document,
    console: { error() {} },
    fetch() { requestCount += 1; },
  });
  listeners.get('DOMContentLoaded')();
  assert.equal(requestCount, 0);
  for (const id of ['summary-message', 'data-message', 'form-message', 'history-message']) {
    assert.match(elements.get(id).textContent, /서비스 연결 설정/);
  }
  for (const id of [
    'refresh-summary-button', 'refresh-data-button', 'add-data-button',
    'submit-button', 'refresh-conversations-button',
  ]) {
    assert.equal(elements.get(id).disabled, true);
  }
});
