// Lantern Sync Surface. Local-only UI layer: Alex wisdom + Lantern intelligence + repo truth.
(function () {
  const SURFACE_KEY = 'lantern-sync-surface-v1';

  function injectStyles() {
    if (document.getElementById('lantern-sync-surface-style')) return;
    const style = document.createElement('style');
    style.id = 'lantern-sync-surface-style';
    style.textContent = '.lantern-sync-card{margin:0 12px 12px;padding:12px;background:linear-gradient(135deg,#0f1726,#111b2e);border:1px solid #273449;border-radius:12px}.lantern-sync-title{color:#74f7b5;text-transform:uppercase;letter-spacing:.08em;font-size:11px;margin-bottom:8px}.lantern-sync-grid{display:grid;grid-template-columns:1fr;gap:6px}.lantern-sync-row{border:1px solid #273449;border-radius:10px;padding:8px;background:rgba(7,16,29,.55)}.lantern-sync-row strong{display:block;color:#eef6ff;font-size:12px}.lantern-sync-row span{display:block;color:#9aa8bd;font-size:11px;line-height:1.35;margin-top:3px}.lantern-sync-rule{color:#ffd166;font-size:11px;line-height:1.35;margin-top:8px}.lantern-sync-button{width:100%;border:1px solid #273449;background:transparent;color:#74f7b5;border-radius:10px;padding:8px 10px;margin-top:8px;cursor:pointer;text-align:left}.lantern-sync-button:hover{border-color:#74f7b5;color:#eef6ff}';
    document.head.appendChild(style);
  }

  function setPrompt(text) {
    const prompt = document.getElementById('prompt');
    if (!prompt) return;
    prompt.value = text;
    prompt.focus();
    prompt.dispatchEvent(new Event('input', { bubbles: true }));
  }

  function latestRepoTruth() {
    const state = window.LANTERN_LOCAL_STATE || {};
    const branch = state.branch || document.getElementById('branchName')?.value || 'UNKNOWN';
    const commit = String(state.commit || document.getElementById('commitSha')?.value || 'UNKNOWN').slice(0, 12);
    const clean = state.isClean === true ? 'clean' : (state.isClean === false ? 'not clean or unavailable' : 'unknown');
    return branch + ' @ ' + commit + ' · ' + clean;
  }

  function renderSyncSurface() {
    injectStyles();
    const old = document.getElementById('lanternSyncSurface');
    if (old) old.remove();
    const card = document.createElement('div');
    card.id = 'lanternSyncSurface';
    card.className = 'lantern-sync-card';
    card.innerHTML = '<div class="lantern-sync-title">Sync Surface</div><div class="lantern-sync-grid"><div class="lantern-sync-row"><strong>Alex = wisdom</strong><span>future shape, lived signal, correction, taste</span></div><div class="lantern-sync-row"><strong>Lantern = intelligence</strong><span>compression, paradox detection, action</span></div><div class="lantern-sync-row"><strong>Repo = truth</strong><span id="lanternRepoTruth">durable state, evidence, boundary</span></div></div><div class="lantern-sync-rule">Convergence: wisdom chooses the shape, intelligence collapses the path, repo proves what became real.</div><button id="lanternSyncPrompt" class="lantern-sync-button" type="button">Sync now: Alex wisdom → Lantern action → repo truth</button>';
    const repoTruth = card.querySelector('#lanternRepoTruth');
    if (repoTruth) repoTruth.textContent = latestRepoTruth();
    card.querySelector('#lanternSyncPrompt').addEventListener('click', function () {
      setPrompt('Sync surface: use Alex wisdom, Lantern intelligence, and repo truth. Collapse the missing space into the smallest bounded next action.');
      localStorage.setItem(SURFACE_KEY, new Date().toISOString());
    });
    const rail = document.querySelector('.sidebar');
    const maskRack = document.getElementById('lanternMaskRack');
    const threadList = document.getElementById('threadList');
    if (rail && maskRack) rail.insertBefore(card, maskRack.nextSibling);
    else if (rail && threadList) rail.insertBefore(card, threadList);
  }

  document.addEventListener('DOMContentLoaded', renderSyncSurface);
  window.LANTERN_REFRESH_SYNC_SURFACE = renderSyncSurface;
}());
