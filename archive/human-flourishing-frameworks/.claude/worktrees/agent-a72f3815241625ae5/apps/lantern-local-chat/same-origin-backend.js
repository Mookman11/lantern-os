// Same-origin backend guard. Runs before the main app script.
(function () {
  const STORAGE_KEY = 'lantern-real-local-backend-v1';

  function isLocalHttp() {
    return window.location.protocol === 'http:' && /^(127\.0\.0\.1|localhost)$/.test(window.location.hostname);
  }

  function sameOrigin() {
    return window.location.origin;
  }

  function rewriteSavedBackendUrl() {
    if (!isLocalHttp()) return;
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      saved.fields = saved.fields || {};
      saved.fields.backendUrl = sameOrigin();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
    } catch (error) {
      localStorage.removeItem(STORAGE_KEY);
    }
  }

  function rewriteRuntimeState() {
    if (!isLocalHttp()) return;
    window.LANTERN_LOCAL_STATE = window.LANTERN_LOCAL_STATE || {};
    window.LANTERN_LOCAL_STATE.backendUrl = sameOrigin();
    window.LANTERN_LOCAL_STATE.uiUrl = sameOrigin() + '/';
  }

  function syncVisibleField() {
    if (!isLocalHttp()) return;
    const input = document.getElementById('backendUrl');
    if (input) input.value = sameOrigin();
  }

  rewriteSavedBackendUrl();
  rewriteRuntimeState();
  document.addEventListener('DOMContentLoaded', syncVisibleField);
  window.LANTERN_BACKEND_ORIGIN = isLocalHttp() ? sameOrigin() : null;
}());
