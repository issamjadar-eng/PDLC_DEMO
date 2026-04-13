const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const transcript = document.getElementById("transcript");
const clearBtn = document.getElementById("clear-chat");
const section = document.querySelector("section.chat");
const agentName = section.dataset.agent;

const STORAGE_KEY = `project-console:chat:${agentName}`;
let history = [];

function saveHistory() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  } catch (e) {
    console.warn("Failed to persist chat history:", e);
  }
}

function loadHistory() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const saved = JSON.parse(raw);
    if (!Array.isArray(saved)) return;
    history = saved;
  } catch (e) {
    console.warn("Failed to load chat history:", e);
  }
}

function rerenderFromHistory() {
  transcript.innerHTML = "";
  for (const m of history) {
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

async function send(message) {
  const userEl = addMessage("user");
  userEl.textContent = message;
  const priorHistory = history.slice();
  history.push({ role: "user", content: message });
  saveHistory();

  let currentBubble = null;
  let currentSpeakerTitle = null;
  let assistantBuffer = "";
  let pendingEl = addPendingIndicator("Waiting for response…");

  const flushAssistant = () => {
    if (currentBubble && assistantBuffer) {
      const label = currentSpeakerTitle ? `${currentSpeakerTitle}: ` : "";
      history.push({ role: "assistant", content: label + assistantBuffer });
      saveHistory();
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
      if (evt.type === "speaker") {
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

clearBtn.addEventListener("click", () => {
  if (history.length === 0) return;
  if (!confirm("Clear this conversation? This cannot be undone.")) return;
  history = [];
  saveHistory();
  transcript.innerHTML = "";
  chatInput.focus();
});

loadHistory();
rerenderFromHistory();
