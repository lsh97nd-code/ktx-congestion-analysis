'use strict';

(function initializeThemeModule(windowObject, documentObject) {
  const STORAGE_KEY = 'ktx-color-theme';
  const DARK_QUERY = '(prefers-color-scheme: dark)';
  const root = documentObject.documentElement;
  const mediaQuery = windowObject.matchMedia?.(DARK_QUERY) ?? null;
  let explicitTheme = readStoredTheme();
  let toggleButton = null;

  function isTheme(value) {
    return value === 'light' || value === 'dark';
  }

  function readStoredTheme() {
    try {
      const stored = windowObject.localStorage?.getItem(STORAGE_KEY);
      return isTheme(stored) ? stored : null;
    } catch {
      return null;
    }
  }

  function getSystemTheme() {
    return mediaQuery?.matches ? 'dark' : 'light';
  }

  function getActiveTheme() {
    return explicitTheme ?? getSystemTheme();
  }

  function updateButton(theme) {
    if (!toggleButton) {
      return;
    }

    const isDark = theme === 'dark';
    toggleButton.setAttribute('aria-pressed', String(isDark));
    const label = toggleButton.querySelector('span');
    if (label) {
      label.textContent = isDark ? '라이트 모드' : '다크 모드';
    }
  }

  function applyTheme(theme) {
    const safeTheme = isTheme(theme) ? theme : 'light';
    root.dataset.theme = safeTheme;
    root.style.colorScheme = safeTheme;
    updateButton(safeTheme);
    return safeTheme;
  }

  function saveTheme(theme) {
    try {
      windowObject.localStorage?.setItem(STORAGE_KEY, theme);
    } catch {
      // 저장소가 차단돼도 현재 페이지에서는 선택한 테마를 유지합니다.
    }
  }

  function toggleTheme() {
    const nextTheme = getActiveTheme() === 'dark' ? 'light' : 'dark';
    explicitTheme = nextTheme;
    saveTheme(nextTheme);
    return applyTheme(nextTheme);
  }

  function handleSystemThemeChange() {
    if (explicitTheme === null) {
      applyTheme(getSystemTheme());
    }
  }

  function handleStorageChange(event) {
    if (event.key !== STORAGE_KEY) {
      return;
    }

    explicitTheme = isTheme(event.newValue) ? event.newValue : null;
    applyTheme(getActiveTheme());
  }

  function bindThemeToggle() {
    toggleButton = documentObject.getElementById('theme-toggle');
    updateButton(getActiveTheme());

    if (!toggleButton || toggleButton.dataset.themeBound === 'true') {
      return;
    }

    toggleButton.dataset.themeBound = 'true';
    toggleButton.addEventListener('click', toggleTheme);
  }

  applyTheme(getActiveTheme());
  mediaQuery?.addEventListener?.('change', handleSystemThemeChange);
  windowObject.addEventListener?.('storage', handleStorageChange);

  if (documentObject.readyState === 'loading') {
    documentObject.addEventListener('DOMContentLoaded', bindThemeToggle);
  } else {
    bindThemeToggle();
  }

  windowObject.KTX_THEME = Object.freeze({
    applyTheme,
    bindThemeToggle,
    getActiveTheme,
    toggleTheme,
  });
})(window, document);
