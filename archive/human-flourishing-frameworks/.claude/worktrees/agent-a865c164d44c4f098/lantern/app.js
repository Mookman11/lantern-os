// Lantern frontend - local-first shell.
//
// Renders the chat composer and the right-pane state surface. The state panel
// is live/read-only for local repo, doctrine, last-test evidence, and optional
// local LLM context packet metadata.

(function () {
    'use strict';

    const messagesEl = document.getElementById('messages');
    const inputEl = document.getElementById('input');
    const sendBtn = document.getElementById('send');

    function setText(id, text) {
        const el = document.getElementById(id);
        if (el) el.textContent = text || '—';
    }

    function setClass(id, className) {
        const el = document.getElementById(id);
        if (el) el.className = className;
    }

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

    function renderList(id, items, emptyText) {
        const list = document.getElementById(id);
        if (!list) return;
        list.innerHTML = '';
        if (!items || items.length === 0) {
            const li = document.createElement('li');
            li.textContent = emptyText;
            list.appendChild(li);
            return;
        }
        items.forEach(function (item) {
            const li = document.createElement('li');
            li.textContent = item;
            list.appendChild(li);
        });
    }

    async function loadHealth() {
        try {
            const r = await fetch('/api/lantern/health');
            const data = await r.json();
            setText('state-role', data.role || '—');

            setText('state-wired', data.substrate_wired ? 'yes' : 'no');
            setClass('state-wired', 'v ' + (data.substrate_wired ? 'on' : 'off'));

            setText('state-key', data.anthropic_api_key_set ? 'yes' : 'no');
            setClass('state-key', 'v ' + (data.anthropic_api_key_set ? 'on' : 'off'));

            setText('state-bind', data.public_bind_enabled ? 'PUBLIC (warn!)' : 'localhost');
            setClass('state-bind', 'v ' + (data.public_bind_enabled ? 'warn' : 'on'));

            const banner = document.getElementById('substrate-banner');
            if (banner) banner.hidden = Boolean(data.substrate_wired);
        } catch (e) {
            appendSystem('Cannot reach Lantern server. Is python lantern/server.py running?');
        }
    }

    async function loadState() {
        try {
            const r = await fetch('/api/lantern/state');
            const data = await r.json();
            const repo = data.repo || {};
            const lastTest = data.last_test || {};
            const localMemory = data.local_llm_context || {};
            const panelStatus = data.state_status || data.status || '—';

            setText('state-branch', repo.branch || '—');
            setText('state-commit', repo.commit_short || repo.commit || '—');

            setText('state-test', lastTest.status || 'missing');
            setClass('state-test', 'v ' + (lastTest.status === 'pass' ? 'on' : 'warn'));

            setText('memory-status', localMemory.status || 'missing');
            setClass('memory-status', 'v ' + (localMemory.status === 'present' ? 'on' : 'warn'));
            setText('memory-path', localMemory.path || '~/.lantern/state/llm-context.local.md');
            setText('memory-local', localMemory.local_only ? 'yes' : 'no');
            setClass('memory-local', 'v ' + (localMemory.local_only ? 'on' : 'warn'));
            setText('memory-proof', localMemory.memory_is_proof ? 'true' : 'false');
            setClass('memory-proof', 'v ' + (localMemory.memory_is_proof ? 'warn' : 'on'));

            renderList('doc-list', data.loaded_doctrine || [], '(none found yet)');
        } catch (e) {
            appendSystem('State request failed: ' + e.message);
        }
    }

    async function send() {
        const msg = inputEl.value.trim();
        if (!msg) return;
        appendMessage('user', msg);
        inputEl.value = '';
        sendBtn.disabled = true;
        try {
            const r = await fetch('/api/lantern/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg }),
            });
            const data = await r.json();
            appendMessage('lantern', data.reply || '(no reply)');
            if (data.status === 'degraded') {
                appendSystem('Reply was degraded. The dashboard is visible; the LLM substrate is not wired.');
            }
        } catch (e) {
            appendSystem('Chat request failed: ' + e.message);
        } finally {
            sendBtn.disabled = false;
            inputEl.focus();
            loadHealth();
            loadState();
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
        'Lantern local shell loaded. Truth panel is read-only. The role is ' +
        'singular: Lantern Keystone Wish. Memory is not proof.'
    );
    loadHealth();
    loadState();
})();
