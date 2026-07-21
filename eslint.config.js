// Copyright (c) 2024-2026 Bryan Everly
// Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
// See the LICENSE file in the project root for the full terms.

// Minimal flat ESLint config for the docs repo's first-party JS/MJS.
// Uses @eslint/js recommended rules and the same max-lines: 1000 maintainability
// cap the other SysManage frontends enforce. Two file groups: the browser-side
// assets/js/* bundle (window/document globals) and the Node screenshot scripts
// (require/process/__dirname).
//
// Authored as CommonJS (require/module.exports) so it loads cleanly whether or
// not package.json declares a module type — the repo's two Node CLI scripts
// (screenshot-generator.js, real-screenshot.js) use CommonJS `require`, so the
// package intentionally stays CommonJS.
const js = require('@eslint/js');

const browserGlobals = {
  window: 'readonly',
  document: 'readonly',
  console: 'readonly',
  navigator: 'readonly',
  localStorage: 'readonly',
  sessionStorage: 'readonly',
  location: 'readonly',
  fetch: 'readonly',
  alert: 'readonly',
  setTimeout: 'readonly',
  clearTimeout: 'readonly',
  setInterval: 'readonly',
  clearInterval: 'readonly',
  requestAnimationFrame: 'readonly',
  MutationObserver: 'readonly',
  IntersectionObserver: 'readonly',
  CustomEvent: 'readonly',
  Event: 'readonly',
  URL: 'readonly',
  URLSearchParams: 'readonly',
  // UMD export guard (`if (typeof module !== 'undefined')`) at the foot of the
  // shared browser bundles.
  module: 'readonly',
};

const nodeGlobals = {
  require: 'readonly',
  module: 'writable',
  process: 'readonly',
  console: 'readonly',
  __dirname: 'readonly',
  __filename: 'readonly',
  Buffer: 'readonly',
  setTimeout: 'readonly',
  clearTimeout: 'readonly',
  URL: 'readonly',
  // `document` appears inside Playwright page.evaluate()/waitForFunction()
  // callbacks, which execute in the browser page context, not in Node.
  document: 'readonly',
};

module.exports = [
  {
    // Never lint vendored / generated trees.
    ignores: ['node_modules/**', 'screenshots/.venv/**', 'repo/**', '*.config.js'],
  },
  js.configs.recommended,
  {
    // Maintainability limit: 1000 total lines per file (uniform across all
    // SysManage repos; matches the pylint max-module-lines / make lint gate).
    rules: {
      'max-lines': ['error', { max: 1000, skipBlankLines: false, skipComments: false }],
    },
  },
  {
    files: ['assets/js/**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'script',
      globals: browserGlobals,
    },
  },
  {
    files: ['real-screenshot.js', 'screenshot-generator.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: nodeGlobals,
    },
  },
  {
    files: ['screenshots/**/*.mjs'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: nodeGlobals,
    },
  },
];
