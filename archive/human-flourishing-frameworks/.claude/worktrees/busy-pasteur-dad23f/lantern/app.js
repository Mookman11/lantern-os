// Lantern frontend — slice 2.
//
// Wires the real chat endpoint (now backed by the Anthropic API on the
// server) and renders live repo / doctrine / memory state in the right
// pane. Tracks conversation history client-side so the operator owns
// session memory; sends the trailing N turns with each request so the
// substrate has context.

(function () {
    'use strict';

    const messagesEl = document.getElementById('messages');
    const inputEl = document.getElementById('input');
    const sendBtn = document.getElementById('send');

    // History window kept client-side. The server is stateless wrt
    // conversation history; the operator owns it. Slice 3 may add an
    // explicit "clear history" button.
    const history = [];
    const HISTORY_WINDOW = 20;

    function appendMessage(role, text) {
        const div = document.createElement('div');
        div.className = 'message ' + role;
        div.textContent = text;
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function appendSystem(text) {
        appendMessage('system', text);
    }

    function setStateRow(id, value, klass) {
        const el = document.getElementById(id);
        if (!el) return;
        el.textContent = (value === null || value === undefined) ? '—' : value;
        el.className = 'v ' + (klass || '');
    }

    async function loadHealth() {
        try {
            const r = await fetch('/api/lantern/health');
            const data = await r.json();
            setStateRow('state-role', data.role);
            setStateRow('state-wired',
                data.substrate_wired ? 'yes' : 'no',
                data.substrate_wired ? 'on' : 'off');
            setStateRow('state-key',
                data.anthropic_api_key_set ? 'yes' : 'no',
                data.anthropic_api_key_set ? 'on' : 'warn');
            setStateRow('state-bind',
                data.public_bind_enabled ? 'PUBLIC (warn!)' : 'localhost',
                data.public_bind_enabled ? 'warn' : 'on');
        } catch (e) {
            appendSystem(
                'Cannot reach Lantern server. Is python lantern/server.py running?'
            );
        }
    }

    async function loadState() {
        try {
            const r = await fetch('/api/lantern/state');
            const data = await r.json();
            const git = data.git || {};
            if (git.available) {
                setStateRow('state-branch', git.branch, 'on');
                const commitText = git.commit +
                    (git.uncommitted_changes ? ' (dirty)' : '');
                setStateRow('state-commit', commitText,
                    git.uncommitted_changes ? 'warn' : 'on');
            } else {
                setStateRow('state-branch', 'git unavailable', 'off');
                setStateRow('state-commit', '—', 'off');
            }
            const list = document.getElementById('doc-list');
            list.innerHTML = '';
            const docs = data.doctrine_loaded || [];
            if (docs.length === 0) {
                const li = document.createElement('li');
                li.textContent = '(none found yet)';
                list.appendChild(li);
            } else {
                docs.forEach(function (path) {
                    const li = document.createElement('li');
                    li.textContent = path;
                    list.appendChild(li);
                });
            }
            const memList = data.memory_loaded || [];
            if (memList.length > 0) {
                const li = document.createElement('li');
                li.style.color = '#00ff88';
                li.textContent = '+ ' + memList.length +
                    ' operator-curated memory file(s)';
                list.appendChild(li);
            }
        } catch (e) {
            // best-effort
        }
    }

    async function send() {
        const msg = inputEl.value.trim();
        if (!msg) return;
        appendMessage('user', msg);
        history.push({ role: 'user', content: msg });
        inputEl.value = '';
        sendBtn.disabled = true;
        const trimmedHistory = history.slice(-HISTORY_WINDOW, -1);
        try {
            const r = await fetch('/api/lantern/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: msg,
                    history: trimmedHistory,
                }),
            });
            const data = await r.json();
            if (data.status === 'ok') {
                appendMessage('lantern', data.reply || '(empty reply)');
                history.push({ role: 'assistant', content: data.reply || '' });
            } else if (data.status === 'no_substrate') {
                appendMessage('lantern', data.reply);
                appendSystem(
                    'Set ANTHROPIC_API_KEY in the env and restart the server.'
                );
            } else {
                appendSystem('Lantern error: ' + (data.error || 'unknown'));
            }
        } catch (e) {
            appendSystem('Chat request failed: ' + e.message);
        } finally {
            sendBtn.disabled = false;
            inputEl.focus();
        }
    }

    sendBtn.addEventListener('click', send);
    inputEl.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            send();
        }
    });

    appendSystem(
        'Lantern slice 2: Anthropic substrate wired. Doctrine + memory ' +
        'loaded fresh per call. Conversation history is client-side; you own ' +
        'it. The role is singular: Lantern Keystone Wish.'
    );
    loadHealth();
    loadState();
    // Refresh state every 10s so branch/commit changes are visible.
    setInterval(loadState, 10000);
})();
