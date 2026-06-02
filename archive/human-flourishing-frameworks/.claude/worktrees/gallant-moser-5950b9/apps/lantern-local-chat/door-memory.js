// Lantern door return memory. Local-only UI layer.
(function () {
  const CHAT_KEY = 'lantern-real-local-backend-v1';
  const DOOR_KEY = 'lantern-door-return-v1';

  function readJson(key) {
    try { return JSON.parse(localStorage.getItem(key) || '{}'); } catch { return {}; }
  }

  function latestUserMessage() {
    const saved = readJson(CHAT_KEY);
    const chats = Array.isArray(saved.chats) ? saved.chats : [];
    for (const chat of chats) {
      const messages = Array.isArray(chat.messages) ? chat.messages.slice().reverse() : [];
      const user = messages.find((item) => item && item.role === 'user' && item.text);
      if (user) return String(user.text).replace(/\s+/g, ' ').trim();
    }
    return '';
  }

  function shortText(text) {
    if (!text) return 'Last time, you asked for a Lantern door that remembers the conversation when the page reloads.';
    return text.length > 180 ? text.slice(0, 177) + '...' : text;
  }

  function rememberDoor() {
    const latest = latestUserMessage();
    if (!latest) return readJson(DOOR_KEY);
    const door = { title: 'The Local Door', summary: shortText(latest), updatedAt: new Date().toISOString() };
    localStorage.setItem(DOOR_KEY, JSON.stringify(door));
    return door;
  }

  function addStyles() {
    if (document.getElementById('lantern-door-style')) return;
    const style = document.createElement('style');
    style.id = 'lantern-door-style';
    style.textContent = '.lantern-door-card{margin:12px;border:1px solid rgba(116,247,181,.45);border-radius:16px;background:radial-gradient(circle at 50% 10%,rgba(116,247,181,.16),rgba(15,23,38,.95) 48%);padding:14px}.lantern-door-title{color:#eef6ff;font-weight:700;margin-bottom:8px}.lantern-door-art{height:145px;border-radius:14px;border:1px solid rgba(141,211,255,.25);background:radial-gradient(circle at 50% 45%,rgba(255,209,102,.38) 0 7%,transparent 8%),linear-gradient(90deg,transparent 0 41%,rgba(116,247,181,.28) 42% 58%,transparent 59%),radial-gradient(circle at 50% 30%,rgba(141,211,255,.22),transparent 44%),linear-gradient(135deg,#07101d,#172033 55%,#09111f);position:relative}.lantern-door-art:before{content:"";position:absolute;left:34%;top:17%;width:32%;height:78%;border:2px solid rgba(238,246,255,.52);border-bottom:0;border-radius:48% 48% 0 0;box-shadow:0 0 24px rgba(116,247,181,.22),inset 0 0 22px rgba(116,247,181,.13)}.lantern-door-art:after{content:"";position:absolute;left:49%;top:28%;width:2px;height:58%;background:rgba(238,246,255,.32);box-shadow:0 0 18px rgba(255,209,102,.7)}.lantern-door-summary{color:#9aa8bd;font-size:12px;line-height:1.45;margin-top:10px}.lantern-door-return{width:100%;margin-top:10px;padding:9px 10px;border-radius:10px;border:1px solid rgba(116,247,181,.55);background:transparent;color:#74f7b5;cursor:pointer}.lantern-wish-note{color:#ffd166;font-size:12px;margin-top:6px}';
    document.head.appendChild(style);
  }

  function makeText(tag, className, text) {
    const node = document.createElement(tag);
    node.className = className;
    node.textContent = text;
    return node;
  }

  function injectDoor() {
    addStyles();
    const old = document.getElementById('lanternDoorCard');
    if (old) old.remove();
    const door = rememberDoor();
    const card = document.createElement('div');
    card.id = 'lanternDoorCard';
    card.className = 'lantern-door-card';
    card.appendChild(makeText('div', 'lantern-door-title', 'The Local Door'));
    const art = document.createElement('div');
    art.className = 'lantern-door-art';
    art.setAttribute('aria-label', 'A glowing Lantern door that remembers the last conversation');
    card.appendChild(art);
    card.appendChild(makeText('div', 'lantern-door-summary', 'Last time: ' + shortText(door.summary)));
    card.appendChild(makeText('div', 'lantern-wish-note', 'Return rule: show the door, remember the wish, then ask what changed.'));
    const button = makeText('button', 'lantern-door-return', 'Return through this door');
    button.type = 'button';
    button.addEventListener('click', function () {
      const prompt = document.getElementById('prompt');
      if (!prompt) return;
      prompt.value = 'Return through the Local Door. Remind me what we were building last time, what changed, and the next brave bounded move.';
      prompt.focus();
    });
    card.appendChild(button);
    const rail = document.querySelector('.sidebar');
    const threadList = document.getElementById('threadList');
    if (rail && threadList) rail.insertBefore(card, threadList);
  }

  document.addEventListener('DOMContentLoaded', injectDoor);
  window.LANTERN_REFRESH_DOOR = injectDoor;
}());
