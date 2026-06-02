// Lantern Mask Rack. Local-only UI layer.
(function () {
  const MODE_KEY = 'lantern-active-mask-v1';
  const MODES = [
    ['engineer', 'Engineer', 'build the smallest working change'],
    ['storyteller', 'Storyteller', 'make meaning and continuity'],
    ['comedian', 'Comedian', 'keep oxygen in the room'],
    ['doctor', 'Doctor', 'check reality underneath'],
    ['game-master', 'Game Master', 'turn it into a playable world'],
    ['anchor-keeper', 'Anchor Keeper', 'compress into restore phrases'],
    ['art-mirror', 'Art Mirror', 'make the visual language'],
    ['planner', 'Planner', 'order people, time, money, next action'],
  ];

  function activeMode() {
    return localStorage.getItem(MODE_KEY) || 'engineer';
  }

  function setActiveMode(mode) {
    localStorage.setItem(MODE_KEY, mode);
    window.LANTERN_ACTIVE_MODE = mode;
    renderMaskRack();
  }

  function injectStyles() {
    if (document.getElementById('lantern-mask-rack-style')) return;
    const style = document.createElement('style');
    style.id = 'lantern-mask-rack-style';
    style.textContent = '.lantern-mask-rack{margin:0 12px 12px;padding:12px;background:#0f1726;border:1px solid #273449;border-radius:12px}.lantern-mask-title{color:#9aa8bd;text-transform:uppercase;letter-spacing:.08em;font-size:11px;margin-bottom:8px}.lantern-mask-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px}.lantern-mask-button{border:1px solid #273449;background:transparent;color:#9aa8bd;border-radius:10px;padding:8px 7px;text-align:left;cursor:pointer}.lantern-mask-button strong{display:block;color:#eef6ff;font-size:12px}.lantern-mask-button span{display:block;font-size:10px;line-height:1.25;margin-top:3px}.lantern-mask-button.active{border-color:#74f7b5;box-shadow:0 0 18px rgba(116,247,181,.13)}.lantern-mask-note{color:#ffd166;font-size:11px;line-height:1.35;margin-top:8px}';
    document.head.appendChild(style);
  }

  function renderMaskRack() {
    injectStyles();
    const prior = document.getElementById('lanternMaskRack');
    if (prior) prior.remove();
    const active = activeMode();
    window.LANTERN_ACTIVE_MODE = active;
    const card = document.createElement('div');
    card.id = 'lanternMaskRack';
    card.className = 'lantern-mask-rack';
    const title = document.createElement('div');
    title.className = 'lantern-mask-title';
    title.textContent = 'Mask Rack';
    card.appendChild(title);
    const grid = document.createElement('div');
    grid.className = 'lantern-mask-grid';
    MODES.forEach(function (mode) {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'lantern-mask-button' + (mode[0] === active ? ' active' : '');
      button.dataset.mode = mode[0];
      const label = document.createElement('strong');
      label.textContent = mode[1];
      const desc = document.createElement('span');
      desc.textContent = mode[2];
      button.appendChild(label);
      button.appendChild(desc);
      button.addEventListener('click', function () { setActiveMode(mode[0]); });
      grid.appendChild(button);
    });
    card.appendChild(grid);
    const note = document.createElement('div');
    note.className = 'lantern-mask-note';
    note.textContent = 'Lantern shifts form; the Doctor still checks reality underneath.';
    card.appendChild(note);
    const rail = document.querySelector('.sidebar');
    const threadList = document.getElementById('threadList');
    const door = document.getElementById('lanternDoorCard');
    if (rail && threadList) rail.insertBefore(card, door ? door.nextSibling : threadList);
  }

  document.addEventListener('DOMContentLoaded', renderMaskRack);
  window.LANTERN_REFRESH_MASK_RACK = renderMaskRack;
}());
