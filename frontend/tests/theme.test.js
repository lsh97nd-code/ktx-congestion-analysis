'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../js/theme.js'), 'utf8');

function themeFixture({ stored = null, systemDark = false, blockedStorage = false } = {}) {
  const saved = [];
  const buttonListeners = {};
  const mediaListeners = {};
  const windowListeners = {};
  const label = { textContent: '' };
  const button = {
    dataset: {},
    attributes: {},
    setAttribute(name, value) {
      this.attributes[name] = value;
    },
    querySelector() {
      return label;
    },
    addEventListener(name, handler) {
      buttonListeners[name] = handler;
    },
  };
  const media = {
    matches: systemDark,
    addEventListener(name, handler) {
      mediaListeners[name] = handler;
    },
  };
  const localStorage = {
    getItem() {
      if (blockedStorage) {
        throw new Error('blocked');
      }
      return stored;
    },
    setItem(key, value) {
      if (blockedStorage) {
        throw new Error('blocked');
      }
      saved.push([key, value]);
    },
  };
  const documentElement = { dataset: {}, style: {} };
  const context = {
    window: {
      localStorage,
      matchMedia() {
        return media;
      },
      addEventListener(name, handler) {
        windowListeners[name] = handler;
      },
    },
    document: {
      documentElement,
      readyState: 'complete',
      getElementById() {
        return button;
      },
      addEventListener() {},
    },
  };
  vm.runInNewContext(source, context);
  return {
    ...context,
    button,
    buttonListeners,
    documentElement,
    label,
    media,
    mediaListeners,
    saved,
    windowListeners,
  };
}

test('stored preference overrides the system theme and toggle persists', () => {
  const fixture = themeFixture({ stored: 'light', systemDark: true });
  assert.equal(fixture.documentElement.dataset.theme, 'light');
  assert.equal(fixture.button.attributes['aria-pressed'], 'false');
  assert.equal(fixture.label.textContent, '다크 모드');

  fixture.buttonListeners.click();
  assert.equal(fixture.documentElement.dataset.theme, 'dark');
  assert.equal(fixture.button.attributes['aria-pressed'], 'true');
  assert.equal(fixture.label.textContent, '라이트 모드');
  assert.deepEqual(fixture.saved, [['ktx-color-theme', 'dark']]);
});

test('theme still toggles when localStorage is blocked', () => {
  const fixture = themeFixture({ systemDark: true, blockedStorage: true });
  assert.equal(fixture.documentElement.dataset.theme, 'dark');
  assert.doesNotThrow(() => fixture.buttonListeners.click());
  assert.equal(fixture.documentElement.dataset.theme, 'light');
});

test('system theme changes apply only when there is no explicit preference', () => {
  const fixture = themeFixture({ systemDark: false });
  assert.equal(fixture.documentElement.dataset.theme, 'light');
  fixture.media.matches = true;
  fixture.mediaListeners.change();
  assert.equal(fixture.documentElement.dataset.theme, 'dark');

  fixture.buttonListeners.click();
  fixture.media.matches = true;
  fixture.mediaListeners.change();
  assert.equal(fixture.documentElement.dataset.theme, 'light');
});
