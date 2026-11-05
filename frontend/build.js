'use strict';

const fs = require('fs');
const path = require('path');

const apiBaseUrl = String(process.env.API_BASE_URL || '')
  .trim()
  .replace(/\/+$/, '');

if (!apiBaseUrl) {
  console.error('[build] API_BASE_URL environment variable is required.');
  process.exit(1);
}

try {
  const parsedUrl = new URL(apiBaseUrl);
  if (
    !/^https?:\/\//i.test(apiBaseUrl) ||
    !['http:', 'https:'].includes(parsedUrl.protocol) ||
    parsedUrl.username ||
    parsedUrl.password ||
    parsedUrl.search ||
    parsedUrl.hash
  ) {
    throw new Error('Unsupported API URL');
  }
} catch {
  console.error(
    '[build] API_BASE_URL must be an absolute HTTP(S) URL without credentials, a query, or a fragment.'
  );
  process.exit(1);
}

const distDir = path.join(__dirname, 'dist');
const distJsDir = path.join(distDir, 'js');

fs.rmSync(distDir, { recursive: true, force: true });
fs.mkdirSync(distJsDir, { recursive: true });

fs.copyFileSync(
  path.join(__dirname, 'index.html'),
  path.join(distDir, 'index.html')
);

fs.cpSync(
  path.join(__dirname, 'css'),
  path.join(distDir, 'css'),
  { recursive: true }
);

fs.copyFileSync(
  path.join(__dirname, 'js', 'app.js'),
  path.join(distJsDir, 'app.js')
);

const config = `window.APP_CONFIG = Object.freeze({
  API_BASE_URL: ${JSON.stringify(apiBaseUrl)}
});
`;

fs.writeFileSync(
  path.join(distJsDir, 'config.js'),
  config,
  'utf8'
);

console.log(
  `[build] Static frontend generated in dist/ for API: ${apiBaseUrl}`
);
