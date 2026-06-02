// Default placeholder. The batch launcher writes runtime-state.generated.js locally.
// No GPT call, no network request, no command execution from browser.
window.LANTERN_LOCAL_STATE = null;

(function loadGeneratedLanternRuntimeState() {
  if (typeof document === "undefined") return;
  const script = document.createElement("script");
  script.src = "runtime-state.generated.js?t=" + Date.now();
  script.async = false;
  script.onload = function () {
    syncLanternSameOriginBackend();
  };
  script.onerror = function () {
    window.LANTERN_LOCAL_STATE = window.LANTERN_LOCAL_STATE || null;
    syncLanternSameOriginBackend();
  };
  document.head.appendChild(script);
}());

function syncLanternSameOriginBackend() {
  if (typeof window === "undefined") return;
  const isLocalHttp = window.location.protocol === "http:" && /^(127\.0\.0\.1|localhost)$/.test(window.location.hostname);
  if (!isLocalHttp) return;
  const origin = window.location.origin;
  window.LANTERN_BACKEND_ORIGIN = origin;
  window.LANTERN_LOCAL_STATE = window.LANTERN_LOCAL_STATE || {};
  window.LANTERN_LOCAL_STATE.backendUrl = origin;
  window.LANTERN_LOCAL_STATE.uiUrl = origin + "/";
  try {
    const storageKey = "lantern-real-local-backend-v1";
    const saved = JSON.parse(localStorage.getItem(storageKey) || "{}");
    saved.fields = saved.fields || {};
    saved.fields.backendUrl = origin;
    localStorage.setItem(storageKey, JSON.stringify(saved));
  } catch (error) {
    // Keep the UI usable even when localStorage contains stale or invalid data.
  }
}
