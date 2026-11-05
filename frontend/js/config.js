'use strict';

// Defaults for directly serving frontend/ (including Render Static Sites).
// build.js generates a replacement in dist/ from the API_BASE_URL variable.
window.APP_CONFIG = Object.freeze({
  API_BASE_URL: ['localhost', '127.0.0.1', '[::1]'].includes(window.location.hostname)
    ? 'http://127.0.0.1:8001'
    : 'https://ktx-congestion-analysis.onrender.com',
});
