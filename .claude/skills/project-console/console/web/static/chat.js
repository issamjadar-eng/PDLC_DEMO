const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const transcript = document.getElementById("transcript");
const renameBtn = document.getElementById("rename-thread");
const deleteBtn = document.getElementById("delete-thread");
const newThreadBtn = document.getElementById("new-thread");
const threadListEl = document.getElementById("thread-list");
const section = document.querySelector("section.chat");
const agentName = section.dataset.agent;

const STORAGE_KEY = `project-console:threads:v1:${agentName}`;
const LEGACY_KEY = `project-console:chat:${agentName}`;

let store = { threads: {}, order: [], activeId: null };

function uid() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

function nowISO() {
  return new Date().toISOString();
}

function relativeTime(iso) {
  const then = new Date(iso).getTime();
  const diffSec = Math.floor((Date.now() - then) / 1000);
  if (diffSec < 60) return "just now";
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  return `${Math.floor(diffSec / 86400)}d ago`;
}

function deriveTitle(messages) {
  const firstUser = messages.find((m) => m.role === "user");
  if (!firstUser) return "New thread";
  const t = firstUser.content.replace(/\s+/g, " ").trim();
  return t.length > 48 ? t.slice(0, 48) + "…" : t;
}

function newThread() {
  const id = uid();
  const t = {
    id,
    title: "New thread",
    created: nowISO(),
    updated: nowISO(),
    messages: [],
  };
  store.threads[id] = t;
  store.order.unshift(id);
  store.activeId = id;
  return t;
}

function activeThread() {
  if (!store.activeId || !store.threads[store.activeId]) {
    return newThread();
  }
  return store.threads[store.activeId];
}

function persist() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  } catch (e) {
    console.warn("Failed to persist thread store:", e);
  }
}

function migrateLegacy() {
  try {
    const raw = localStorage.getItem(LEGACY_KEY);
    if (!raw) return;
    const messages = JSON.parse(raw);
    if (!Array.isArray(messages) || messages.length === 0) {
      localStorage.removeItem(LEGACY_KEY);
      return;
    }
    const id = uid();
    store.threads[id] = {
      id,
      title: deriveTitle(messages),
      created: nowISO(),
      updated: nowISO(),
      messages,
    };
    store.order.unshift(id);
    store.activeId = id;
    localStorage.removeItem(LEGACY_KEY);
    persist();
  } catch (e) {
    console.warn("Legacy migration failed:", e);
  }
}

function loadStore() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const saved = JSON.parse(raw);
      if (saved && typeof saved === "object" && saved.threads && saved.order) {
        store = saved;
        return;
      }
    }
  } catch (e) {
    console.warn("Failed to load thread store:", e);
  }
  store = { threads: {}, order: [], activeId: null };
}

function renderThreadList() {
  threadListEl.innerHTML = "";
  if (store.order.length === 0) {
    const empty = document.createElement("li");
    empty.className = "thread-empty muted small";
    empty.textContent = "No threads yet.";
    threadListEl.appendChild(empty);
    return;
  }
  for (const id of store.order) {
    const t = store.threads[id];
    if (!t) continue;
    const li = document.createElement("li");
    li.className = "thread-item" + (id === store.activeId ? " active" : "");
    li.dataset.id = id;
    const title = document.createElement("div");
    title.className = "thread-title";
    title.textContent = t.title;
    const meta = document.createElement("div");
    meta.className = "thread-meta muted small";
    meta.textContent = `${t.messages.length} msg · ${relativeTime(t.updated)}`;
    li.appendChild(title);
    li.appendChild(meta);
    li.addEventListener("click", () => {
      if (store.activeId === id) return;
      store.activeId = id;
      persist();
      renderThreadList();
      rerenderTranscript();
    });
    threadListEl.appendChild(li);
  }
}

function rerenderTranscript() {
  transcript.innerHTML = "";
  const t = activeThread();
  for (const m of t.messages) {
    if (m.role === "user") {
      const el = addMessage("user");
      el.textContent = m.content;
    } else if (m.role === "assistant") {
      const speakerMatch = /^([^:]+):\s/.exec(m.content);
      const speaker = speakerMatch ? speakerMatch[1] : null;
      const text = speakerMatch ? m.content.slice(speakerMatch[0].length) : m.content;
      const el = addMessage("assistant", speaker);
      el.innerHTML = window.renderMarkdown(text);
    }
  }
}

function addMessage(role, speaker) {
  const el = document.createElement("div");
  el.className = `msg msg-${role}`;
  if (speaker) {
    const label = document.createElement("div");
    label.className = "speaker";
    label.textContent = speaker;
    el.appendChild(label);
  }
  const content = document.createElement("div");
  content.className = role === "assistant" ? "content md-content" : "content";
  el.appendChild(content);
  transcript.appendChild(el);
  transcript.scrollTop = transcript.scrollHeight;
  return content;
}

function addWarning(message) {
  const el = document.createElement("div");
  el.className = "msg msg-warning";
  el.textContent = `⚠ ${message}`;
  transcript.appendChild(el);
  transcript.scrollTop = transcript.scrollHeight;
}

function addPendingIndicator(label) {
  const el = document.createElement("div");
  el.className = "msg msg-assistant msg-pending";
  el.innerHTML =
    `<div class="speaker">${label}</div>` +
    `<div class="content"><span class="dots"><span>.</span><span>.</span><span>.</span></span> thinking</div>`;
  transcript.appendChild(el);
  transcript.scrollTop = transcript.scrollHeight;
  return el;
}

function touchActive() {
  const t = activeThread();
  t.updated = nowISO();
  if (t.title === "New thread") t.title = deriveTitle(t.messages);
  // Move to front of order
  store.order = [t.id, ...store.order.filter((id) => id !== t.id)];
  persist();
  renderThreadList();
}

async function send(message) {
  const t = activeThread();
  const userEl = addMessage("user");
  userEl.textContent = message;
  const priorHistory = t.messages.slice();
  t.messages.push({ role: "user", content: message });
  touchActive();

  let currentBubble = null;
  let currentSpeakerTitle = null;
  let assistantBuffer = "";
  let pendingEl = addPendingIndicator("Waiting for response…");

  const flushAssistant = () => {
    if (currentBubble && assistantBuffer) {
      const label = currentSpeakerTitle ? `${currentSpeakerTitle}: ` : "";
      t.messages.push({ role: "assistant", content: label + assistantBuffer });
      touchActive();
    }
    currentBubble = null;
    assistantBuffer = "";
    currentSpeakerTitle = null;
  };

  const clearPending = () => {
    if (pendingEl) {
      pendingEl.remove();
      pendingEl = null;
    }
  };

  let resp;
  try {
    resp = await fetch(`/agents/${agentName}/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ history: priorHistory, message }),
    });
  } catch (e) {
    clearPending();
    const err = addMessage("error");
    err.textContent = `Network error: ${e.message}`;
    return;
  }

  if (!resp.ok || !resp.body) {
    clearPending();
    const err = addMessage("error");
    err.textContent = `Error: ${resp.status} ${resp.statusText}`;
    return;
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const parts = buf.split("\n\n");
    buf = parts.pop();
    for (const part of parts) {
      if (!part.startsWith("data: ")) continue;
      let evt;
      try { evt = JSON.parse(part.slice(6)); } catch { continue; }
      if (evt.type === "warning") {
        addWarning(evt.message);
      } else if (evt.type === "speaker") {
        flushAssistant();
        currentSpeakerTitle = evt.title;
        if (pendingEl) {
          pendingEl.querySelector(".speaker").textContent = evt.title;
        } else {
          pendingEl = addPendingIndicator(evt.title);
        }
      } else if (evt.type === "token") {
        if (pendingEl && !currentBubble) {
          pendingEl.remove();
          pendingEl = null;
          currentBubble = addMessage("assistant", currentSpeakerTitle);
        }
        if (currentBubble) {
          assistantBuffer += evt.text;
          currentBubble.innerHTML = window.renderMarkdown(assistantBuffer);
          transcript.scrollTop = transcript.scrollHeight;
        }
      } else if (evt.type === "speaker_done") {
        flushAssistant();
        if (pendingEl) {
          pendingEl.remove();
          pendingEl = null;
        }
      } else if (evt.type === "error") {
        clearPending();
        const errEl = addMessage("error");
        errEl.textContent = `Error: ${evt.message}`;
      }
    }
  }
  clearPending();
  flushAssistant();
}

async function submitMessage() {
  const message = chatInput.value.trim();
  if (!message) return;
  chatInput.value = "";
  const btn = chatForm.querySelector("button");
  btn.disabled = true;
  chatInput.disabled = true;
  try {
    await send(message);
  } finally {
    btn.disabled = false;
    chatInput.disabled = false;
    chatInput.focus();
  }
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  submitMessage();
});

chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
    e.preventDefault();
    submitMessage();
  }
});

newThreadBtn.addEventListener("click", () => {
  newThread();
  persist();
  renderThreadList();
  rerenderTranscript();
  chatInput.focus();
});

renameBtn.addEventListener("click", () => {
  const t = activeThread();
  const next = prompt("Rename thread:", t.title);
  if (next && next.trim()) {
    t.title = next.trim().slice(0, 80);
    persist();
    renderThreadList();
  }
});

deleteBtn.addEventListener("click", () => {
  const t = activeThread();
  if (!confirm(`Delete thread "${t.title}"? This cannot be undone.`)) return;
  delete store.threads[t.id];
  store.order = store.order.filter((id) => id !== t.id);
  store.activeId = store.order[0] || null;
  persist();
  renderThreadList();
  rerenderTranscript();
});

loadStore();
migrateLegacy();
if (store.order.length === 0) {
  newThread();
  persist();
}
renderThreadList();
rerenderTranscript();
