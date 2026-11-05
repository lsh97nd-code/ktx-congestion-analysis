'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const frontendDir = path.resolve(__dirname, '..');
const configSource = fs.readFileSync(path.join(frontendDir, 'js/config.js'), 'utf8');

test('no-build frontend includes every relative script and stylesheet', () => {
  const html = fs.readFileSync(path.join(frontendDir, 'index.html'), 'utf8');
  const assets = [...html.matchAll(/(?:src|href)="\.\/([^"]+)"/g)];
  assert.ok(assets.length > 0);
  for (const [, relativeAsset] of assets) {
    assert.ok(fs.statSync(path.join(frontendDir, relativeAsset)).isFile(), relativeAsset);
  }
});

for (const hostname of ['ktx-congestion-analysis-frontend.onrender.com', 'example.test']) {
  test(`no-build config uses the deployed backend for ${hostname}`, () => {
    const context = { window: { location: { hostname } } };
    vm.runInNewContext(configSource, context);
    assert.equal(
      context.window.APP_CONFIG.API_BASE_URL,
      'https://ktx-congestion-analysis.onrender.com'
    );
  });
}

for (const hostname of ['localhost', '127.0.0.1', '[::1]']) {
  test(`no-build config uses the local backend for ${hostname}`, () => {
    const context = { window: { location: { hostname } } };
    vm.runInNewContext(configSource, context);
    assert.equal(context.window.APP_CONFIG.API_BASE_URL, 'http://127.0.0.1:8001');
  });
}
