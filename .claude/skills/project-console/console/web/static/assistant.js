/* ===================================================================== */
/* Generic Assistant drawer                                                */
/*                                                                         */
/* Mount via `_assistant_drawer.html`. The <aside data-*> attributes       */
/* configure: scope (localStorage thread key), endpoint, default agent,    */
/* allowed-agents list, grounding source mode, and grounding label.        */
/*                                                                         */
/* Grounding source modes (drawer resolves text at send time):             */
/*   static:<inline>   — pre-rendered text in #pc-assistant-config.staticGrounding */
/*   url:<relative>    — GET that URL; response is text/plain OR {text}    */
/*   element:<sel>     — read .textContent of the matching element        */
/*   handler           — call window.pcAssistantGetGrounding()             */
/*   ""                — no grounding                                      */
/*                                                                         */
/* Thread history lives in localStorage under `pc-chats-<scope>` and       */
/* `pc-chats-<scope>-active`. The server is stateless; every request       */
/* sends full history.                                                     */
/* ===================================================================== */
(function () {
  const drawer = document.getElementById('pc-assistant');
  if (!drawer) return;

  const cfgEl = document.getElementById('pc-assistant-config');
  const pageCfg = cfgEl ? JSON.parse(cfgEl.textContent || '{}') : {};

  const scope          = drawer.dataset.scope || 'default';
  const endpoint       = drawer.dataset.endpoint || '/assistant/chat/stream';
  const defaultAgent   = drawer.dataset.defaultAgent || '';
  const allowedAgents  = (drawer.dataset.allowedAgents || '')
                           .split(',').map(s => s.trim()).filter(Boolean);
  const groundingLabel = drawer.dataset.groundingLabel || '';
  const groundingSrc   = drawer.dataset.groundingSource || '';
  const storageKey     = `pc-chats-${scope}`;
  const activeKey      = `pc-chats-${scope}-active`;
  const widthKey       = 'pc-assistant-width';
  const openBtn        = document.getElementById(pageCfg.openButtonId || 'pc-assistant-open');

  const backdrop    = document.getElementById('pc-assistant-backdrop');
  const closeBtn    = document.getElementById('pc-assistant-close');
  const resizeEl    = document.getElementById('pc-assistant-resize');
  const threadSel   = document.getElementById('pc-thread-select');
  const newBtn      = document.getElementById('pc-thread-new');
  const clearBtn    = document.getElementById('pc-thread-clear');
  const messagesEl  = document.getElementById('pc-messages');

  // Jump-to-latest pill — shown when the user has scrolled up during a
  // streaming response (sticky-scroll is disabled at that point so we
  // don't yank them back). Click returns to the tail and hides the pill;
  // manually scrolling back to near-bottom also hides it.
  const jumpToLatestBtn = (function mountJumpToLatest() {
    if (!messagesEl || !messagesEl.parentElement) return null;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'pc-jump-latest';
    btn.textContent = '↓ Jump to latest';
    btn.addEventListener('click', () => {
      messagesEl.scrollTop = messagesEl.scrollHeight;
      btn.classList.remove('visible');
    });
    messagesEl.parentElement.appendChild(btn);
    messagesEl.addEventListener('scroll', () => {
      const nearBottom =
        messagesEl.scrollHeight - messagesEl.scrollTop - messagesEl.clientHeight < 60;
      if (nearBottom) btn.classList.remove('visible');
    });
    return btn;
  })();
  const form        = document.getElementById('pc-input-form');
  const input       = document.getElementById('pc-input');
  const sendBtn     = document.getElementById('pc-send');
  const agentSel    = document.getElementById('pc-assistant-agent');
  const subtitleEl  = document.getElementById('pc-assistant-subtitle');

  // -------- minimal markdown renderer (assistant bubbles only) -----------
  function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function splitRow(row) {
    return row.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim());
  }
  function renderMarkdown(src) {
    let t = escapeHtml(src || '');
    const codeBlocks = [];
    t = t.replace(/```([\s\S]*?)```/g, (_, code) => {
      codeBlocks.push(code.replace(/^\n/, '').replace(/\n$/, ''));
      return `\u0000CB${codeBlocks.length - 1}\u0000`;
    });
    const inlineCode = [];
    t = t.replace(/`([^`\n]+)`/g, (_, code) => {
      inlineCode.push(code);
      return `\u0000IC${inlineCode.length - 1}\u0000`;
    });
    t = t.replace(/\*\*([^*\n]+?)\*\*/g, '<strong>$1</strong>');
    t = t.replace(/(^|[\s(])\*([^*\n]+?)\*(?=[\s).,;:!?]|$)/g, '$1<em>$2</em>');
    t = t.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

    const lines = t.split('\n');
    const out = [];
    const isTableDivider = s => /^\s*\|?\s*:?[-]{2,}[-:\s|]*$/.test(s);
    const isUnordered = s => /^\s*[-*]\s+/.test(s);
    const isOrdered   = s => /^\s*\d+\.\s+/.test(s);
    const isHeader    = s => /^#{1,6}\s+/.test(s);
    let i = 0;
    while (i < lines.length) {
      const line = lines[i];
      const h = /^(#{1,6})\s+(.+)$/.exec(line);
      if (h) {
        const lvl = Math.min(4, h[1].length);
        out.push(`<h${lvl}>${h[2]}</h${lvl}>`);
        i++; continue;
      }
      if (line.trimStart().startsWith('|') && i + 1 < lines.length && isTableDivider(lines[i + 1])) {
        const headers = splitRow(line);
        i += 2;
        const rows = [];
        while (i < lines.length && lines[i].trimStart().startsWith('|')) {
          rows.push(splitRow(lines[i])); i++;
        }
        const th = headers.map(c => `<th>${c}</th>`).join('');
        const tb = rows.map(r => '<tr>' + r.map(c => `<td>${c}</td>`).join('') + '</tr>').join('');
        out.push(`<table class="pc-md-table"><thead><tr>${th}</tr></thead><tbody>${tb}</tbody></table>`);
        continue;
      }
      if (isUnordered(line)) {
        const items = [];
        while (i < lines.length && isUnordered(lines[i])) {
          items.push(lines[i].replace(/^\s*[-*]\s+/, '')); i++;
        }
        out.push('<ul>' + items.map(x => `<li>${x}</li>`).join('') + '</ul>');
        continue;
      }
      if (isOrdered(line)) {
        const items = [];
        while (i < lines.length && isOrdered(lines[i])) {
          items.push(lines[i].replace(/^\s*\d+\.\s+/, '')); i++;
        }
        out.push('<ol>' + items.map(x => `<li>${x}</li>`).join('') + '</ol>');
        continue;
      }
      if (line.trim() === '') { i++; continue; }
      const pLines = [];
      while (
        i < lines.length &&
        lines[i].trim() !== '' &&
        !isHeader(lines[i]) &&
        !isUnordered(lines[i]) &&
        !isOrdered(lines[i]) &&
        !(lines[i].trimStart().startsWith('|') && i + 1 < lines.length && isTableDivider(lines[i + 1]))
      ) {
        pLines.push(lines[i]); i++;
      }
      if (pLines.length) out.push('<p>' + pLines.join('<br>') + '</p>');
    }
    let html = out.join('\n');
    html = html.replace(/\u0000CB(\d+)\u0000/g, (_, j) => `<pre><code>${codeBlocks[+j]}</code></pre>`);
    html = html.replace(/\u0000IC(\d+)\u0000/g, (_, j) => `<code>${inlineCode[+j]}</code>`);
    return html;
  }

  // -------- grounding resolution ---------------------------------------

  async function resolveGrounding() {
    if (!groundingSrc) return '';
    if (groundingSrc.startsWith('static:')) {
      // Static text was injected server-side into pageCfg.staticGrounding.
      return pageCfg.staticGrounding || groundingSrc.slice('static:'.length);
    }
    if (groundingSrc.startsWith('element:')) {
      const sel = groundingSrc.slice('element:'.length);
      const el = document.querySelector(sel);
      return el ? (el.textContent || '') : '';
    }
    if (groundingSrc.startsWith('url:')) {
      const url = groundingSrc.slice('url:'.length);
      try {
        const r = await fetch(url);
        if (!r.ok) return '';
        const ct = r.headers.get('content-type') || '';
        if (ct.includes('application/json')) {
          const j = await r.json();
          return j.text || j.body || JSON.stringify(j);
        }
        return await r.text();
      } catch (e) {
        return '';
      }
    }
    if (groundingSrc === 'handler') {
      if (typeof window.pcAssistantGetGrounding === 'function') {
        const v = await window.pcAssistantGetGrounding();
        return v || '';
      }
      return '';
    }
    return '';
  }

  // -------- agent picker -----------------------------------------------

  let selectedAgent = defaultAgent;

  async function loadAgents() {
    try {
      const r = await fetch('/assistant/api/agents');
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      const all = data.agents || [];
      const allowed = allowedAgents.length
        ? all.filter(a => allowedAgents.includes(a.name))
        : all;
      agentSel.innerHTML = '';
      if (allowed.length === 0) {
        const opt = document.createElement('option');
        opt.value = ''; opt.textContent = '(no agents available)';
        agentSel.appendChild(opt);
        return;
      }
      // Group by group name in the dropdown.
      const byGroup = {};
      allowed.forEach(a => {
        const g = a.group || 'Other';
        (byGroup[g] = byGroup[g] || []).push(a);
      });
      Object.keys(byGroup).sort().forEach(g => {
        const og = document.createElement('optgroup');
        og.label = g;
        byGroup[g].forEach(a => {
          const opt = document.createElement('option');
          opt.value = a.name; opt.textContent = a.title;
          if (a.name === defaultAgent) opt.selected = true;
          og.appendChild(opt);
        });
        agentSel.appendChild(og);
      });
      if (!agentSel.value) agentSel.value = allowed[0].name;
      selectedAgent = agentSel.value;
    } catch (e) {
      agentSel.innerHTML = `<option value="">Error: ${e.message}</option>`;
    }
  }

  agentSel.addEventListener('change', () => {
    selectedAgent = agentSel.value;
  });

  // -------- thread persistence -----------------------------------------

  function loadAll() {
    try {
      const raw = localStorage.getItem(storageKey);
      return raw ? JSON.parse(raw) : [];
    } catch (e) { return []; }
  }
  function saveAll(threads) {
    localStorage.setItem(storageKey, JSON.stringify(threads));
  }
  function getActiveId() { return localStorage.getItem(activeKey); }
  function setActiveId(id) { localStorage.setItem(activeKey, id); }

  function newThread() {
    const id = 't-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
    return { id, title: 'New conversation', messages: [], updatedAt: Date.now() };
  }

  function ensureThreads() {
    let all = loadAll();
    if (all.length === 0) {
      const t = newThread(); all = [t]; saveAll(all); setActiveId(t.id);
    }
    if (!getActiveId() || !all.find(t => t.id === getActiveId())) {
      setActiveId(all[0].id);
    }
    return all;
  }

  function currentThread() {
    const all = loadAll();
    return all.find(t => t.id === getActiveId()) || null;
  }

  function updateThread(mutator) {
    const all = loadAll();
    const idx = all.findIndex(t => t.id === getActiveId());
    if (idx < 0) return;
    mutator(all[idx]);
    all[idx].updatedAt = Date.now();
    saveAll(all);
  }

  // -------- rendering --------------------------------------------------

  function renderThreadDropdown() {
    const all = loadAll().slice().sort((a, b) => b.updatedAt - a.updatedAt);
    const activeId = getActiveId();
    threadSel.innerHTML = '';
    all.forEach(t => {
      const opt = document.createElement('option');
      opt.value = t.id;
      const when = new Date(t.updatedAt).toLocaleString();
      opt.textContent = `${t.title || 'Untitled'} — ${when}`;
      if (t.id === activeId) opt.selected = true;
      threadSel.appendChild(opt);
    });
  }

  function renderMessages() {
    const t = currentThread();
    messagesEl.innerHTML = '';
    if (!t || t.messages.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'pc-message-empty muted small';
      empty.innerHTML = pageCfg.emptyHint || 'Ask a question to get started.';
      messagesEl.appendChild(empty);
      return;
    }
    t.messages.forEach(m => appendMessageEl(m.role, m.content));
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  // -------- citation post-processing (task 099 v1.7.1) ---------------------
  //
  // The assistant is instructed (via the discovery rubric) to emit numbered
  // footnote-style citations: "[1]", "[2]" inline + a final block of
  // "[N]: docs/path/to/doc.md[#anchor]" definitions. We extract those
  // definitions from the raw markdown, strip them from the body, then
  // transform inline "[N]" tokens into clickable <sup> links that open the
  // Documents viewer at the cited path (optionally scrolling to a heading
  // anchor). Whatever's left goes into a collapsed Sources <details> block.
  //
  // Tolerant by design: if the agent emits a bad anchor or a missing
  // footnote, we degrade to a plain superscript + best-effort link.

  // Parses trailing footnote definitions like "[1]: docs/path/...md#anchor".
  // Returns {body, citations: Map<string, {path, anchor}>}.
  function extractCitations(src) {
    const citations = new Map();
    const lines = src.split('\n');
    // Scan from the end; footnote defs typically live in a trailing block.
    // Stop at the first non-footnote, non-blank line.
    const footnoteRe = /^\s*\[(\d+)\]:\s+(\S[^\s#]*?\.md)(#[^\s]+)?\s*$/;
    let keepUntil = lines.length;
    for (let i = lines.length - 1; i >= 0; i--) {
      const line = lines[i];
      if (line.trim() === '') continue;
      const m = footnoteRe.exec(line);
      if (m) {
        const num = m[1];
        const path = m[2];
        const anchor = m[3] || '';
        citations.set(num, { path, anchor });
        keepUntil = i;
        continue;
      }
      break;
    }
    return {
      body: lines.slice(0, keepUntil).join('\n').replace(/\s+$/, ''),
      citations,
    };
  }

  // After markdown → HTML render, wrap any "[N]" inline references in a
  // clickable <sup><a>.
  function wrapInlineCitations(html, citations) {
    if (citations.size === 0) return html;
    return html.replace(/\[(\d+)\](?!\(|:)/g, (m, num) => {
      const cite = citations.get(num);
      if (!cite) return m;
      const href = `/documents#path=${encodeURIComponent(cite.path)}${cite.anchor}`;
      const title = cite.path + (cite.anchor ? ' · ' + cite.anchor.slice(1) : '');
      return `<sup class="pc-cite-sup"><a class="pc-cite" href="${href}" target="_blank" rel="noopener" title="${title}">[${num}]</a></sup>`;
    });
  }

  // Build the trailing "Sources" <details> block from the citation map.
  function renderSourcesBlock(citations) {
    if (citations.size === 0) return '';
    const rows = Array.from(citations.entries())
      .sort((a, b) => parseInt(a[0], 10) - parseInt(b[0], 10))
      .map(([num, { path, anchor }]) => {
        const href = `/documents#path=${encodeURIComponent(path)}${anchor}`;
        const label = path + (anchor ? ' · ' + anchor.slice(1) : '');
        return `<li>[${num}] <a class="pc-cite" href="${href}" target="_blank" rel="noopener">${label}</a></li>`;
      })
      .join('');
    return `<details class="pc-sources"><summary>Sources (${citations.size})</summary><ol class="pc-cite-list">${rows}</ol></details>`;
  }

  function setMessageContent(el, role, content) {
    if (role === 'assistant') {
      const { body, citations } = extractCitations(content);
      const html = renderMarkdown(body);
      el.innerHTML = wrapInlineCitations(html, citations) + renderSourcesBlock(citations);
    } else {
      // User-authored content. Render as markdown too so prompts that paste
      // markdown (proposal bodies, code blocks, lists, headings, etc.)
      // display formatted instead of as raw text. Safe-ish: the user is
      // typing their own input — at worst they HTML-inject themselves.
      el.innerHTML = renderMarkdown(content);
    }
  }

  function appendMessageEl(role, content, { streaming = false } = {}) {
    const el = document.createElement('div');
    el.className = `pc-msg pc-msg-${role}${streaming ? ' is-streaming' : ''}`;
    setMessageContent(el, role, content);
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    if (jumpToLatestBtn) jumpToLatestBtn.classList.remove('visible');
    return el;
  }

  // -------- streaming send ---------------------------------------------

  async function send(userText) {
    if (!userText.trim()) return;
    if (!selectedAgent) {
      appendMessageEl('assistant', 'No agent selected.').classList.add('pc-msg-error');
      return;
    }

    const groundingText = await resolveGrounding();

    const t = currentThread();
    const history = (t?.messages || []).map(m => ({ role: m.role, content: m.content }));

    updateThread(th => {
      th.messages.push({ role: 'user', content: userText });
      if (th.messages.length === 1 || th.title === 'New conversation') {
        th.title = userText.slice(0, 48).replace(/\s+/g, ' ').trim() || 'Untitled';
      }
    });
    renderThreadDropdown();
    appendMessageEl('user', userText);
    const assistantEl = appendMessageEl('assistant', '', { streaming: true });
    sendBtn.disabled = true;

    try {
      const resp = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_name: selectedAgent,
          history,
          message: userText,
          grounding_text: groundingText || null,
          grounding_label: groundingLabel || null,
        }),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buf = '';
      let full = '';
      const pendingWarnings = [];
      let warningsFlushed = false;

      function flushWarnings() {
        if (warningsFlushed || pendingWarnings.length === 0) return;
        warningsFlushed = true;
        const details = document.createElement('details');
        details.className = 'pc-msg pc-msg-warning-details';
        const summary = document.createElement('summary');
        summary.textContent = '⚠ Source budget notice (' + pendingWarnings.length + ')';
        details.appendChild(summary);
        pendingWarnings.forEach(msg => {
          const p = document.createElement('p');
          p.textContent = msg;
          details.appendChild(p);
        });
        messagesEl.insertBefore(details, assistantEl);
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        let idx;
        while ((idx = buf.indexOf('\n\n')) >= 0) {
          const frame = buf.slice(0, idx);
          buf = buf.slice(idx + 2);
          frame.split('\n').forEach(line => {
            if (!line.startsWith('data: ')) return;
            const payload = line.slice(6).trim();
            if (!payload) return;
            try {
              const evt = JSON.parse(payload);
              if (evt.type === 'token') {
                flushWarnings();
                full += evt.text;
                // Sticky auto-scroll: only auto-follow if the user was
                // already near the bottom. If they've scrolled up to
                // re-read earlier text while the answer is still
                // streaming, respect their position.
                const nearBottom =
                  messagesEl.scrollHeight - messagesEl.scrollTop - messagesEl.clientHeight < 60;
                setMessageContent(assistantEl, 'assistant', full);
                if (nearBottom) {
                  messagesEl.scrollTop = messagesEl.scrollHeight;
                } else if (jumpToLatestBtn) {
                  jumpToLatestBtn.classList.add('visible');
                }
              } else if (evt.type === 'error') {
                assistantEl.classList.remove('is-streaming');
                assistantEl.classList.add('pc-msg-error');
                assistantEl.textContent = 'Error: ' + evt.message;
              } else if (evt.type === 'warning') {
                pendingWarnings.push(evt.message);
              } else if (evt.type === 'info') {
                // Grounding preflight info (Phase 2 task 099): Core/Index
                // sizing. Rendered above the response as a small muted line.
                const i = document.createElement('div');
                i.className = 'pc-msg pc-msg-info muted small';
                i.textContent = 'ℹ ' + evt.message;
                messagesEl.insertBefore(i, assistantEl);
              } else if (evt.type === 'done') {
                flushWarnings();
                assistantEl.classList.remove('is-streaming');
              }
            } catch (e) { /* skip malformed frame */ }
          });
        }
      }

      assistantEl.classList.remove('is-streaming');
      updateThread(th => {
        th.messages.push({ role: 'assistant', content: full });
      });
    } catch (e) {
      assistantEl.classList.remove('is-streaming');
      assistantEl.classList.add('pc-msg-error');
      assistantEl.textContent = 'Error: ' + e.message;
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  }

  // -------- wiring -----------------------------------------------------

  function openDrawer() {
    ensureThreads();
    renderThreadDropdown();
    renderMessages();
    drawer.classList.add('is-open');
    drawer.setAttribute('aria-hidden', 'false');
    backdrop.hidden = false;
    requestAnimationFrame(() => backdrop.classList.add('is-open'));
    setTimeout(() => input.focus(), 220);
  }
  function closeDrawer() {
    drawer.classList.remove('is-open');
    drawer.setAttribute('aria-hidden', 'true');
    backdrop.classList.remove('is-open');
    setTimeout(() => { backdrop.hidden = true; }, 200);
  }

  // Expose open/close for dynamic callers (e.g. Documents page opens the
  // drawer from a floating action button instead of a static header button).
  window.pcAssistantOpen = openDrawer;
  window.pcAssistantClose = closeDrawer;
  // Allow pages to update the subtitle live (e.g. selected file path).
  window.pcAssistantSetSubtitle = (text) => {
    if (subtitleEl) subtitleEl.textContent = text || '';
  };

  if (openBtn) openBtn.addEventListener('click', openDrawer);
  closeBtn.addEventListener('click', closeDrawer);
  backdrop.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && drawer.classList.contains('is-open')) closeDrawer();
  });

  // Resize handle.
  const savedWidth = parseInt(localStorage.getItem(widthKey) || '0', 10);
  if (savedWidth >= 360) drawer.style.width = savedWidth + 'px';
  let dragging = false, startX = 0, startWidth = 0;
  resizeEl.addEventListener('mousedown', (e) => {
    dragging = true; startX = e.clientX;
    startWidth = drawer.getBoundingClientRect().width;
    drawer.classList.add('is-resizing');
    e.preventDefault();
  });
  window.addEventListener('mousemove', (e) => {
    if (!dragging) return;
    const delta = startX - e.clientX;
    const minW = 360;
    const maxW = Math.floor(window.innerWidth * 0.85);
    const next = Math.max(minW, Math.min(maxW, startWidth + delta));
    drawer.style.width = next + 'px';
  });
  window.addEventListener('mouseup', () => {
    if (!dragging) return;
    dragging = false;
    drawer.classList.remove('is-resizing');
    const w = Math.round(drawer.getBoundingClientRect().width);
    localStorage.setItem(widthKey, String(w));
  });

  threadSel.addEventListener('change', () => {
    setActiveId(threadSel.value);
    renderMessages();
  });
  newBtn.addEventListener('click', () => {
    const all = loadAll();
    const t = newThread();
    all.push(t); saveAll(all); setActiveId(t.id);
    renderThreadDropdown();
    renderMessages();
    input.focus();
  });
  clearBtn.addEventListener('click', () => {
    if (!confirm(`Clear all ${loadAll().length} conversation(s) for this scope?`)) return;
    localStorage.removeItem(storageKey);
    localStorage.removeItem(activeKey);
    ensureThreads();
    renderThreadDropdown();
    renderMessages();
  });
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const txt = input.value;
    input.value = '';
    send(txt);
  });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });

  // Load the agent list now so the picker is populated when the drawer opens.
  loadAgents();
})();
