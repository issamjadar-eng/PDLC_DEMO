(function () {
  const panel = document.querySelector(".summary-panel");
  if (!panel) return;
  const body = document.getElementById("summary-body");
  const path = panel.dataset.path;

  async function run() {
    let resp;
    try {
      resp = await fetch(`/documents/summary/${path}`, { method: "POST" });
    } catch (e) {
      body.innerHTML = `<span class="muted">Summary failed: ${e.message}</span>`;
      return;
    }
    if (!resp.ok || !resp.body) {
      body.innerHTML = `<span class="muted">Summary failed: ${resp.status} ${resp.statusText}</span>`;
      return;
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";
    let text = "";
    let first = true;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const parts = buf.split("\n\n");
      buf = parts.pop();
      for (const part of parts) {
        if (!part.startsWith("data: ")) continue;
        let evt;
        try {
          evt = JSON.parse(part.slice(6));
        } catch {
          continue;
        }
        if (evt.type === "token") {
          if (first) {
            body.innerHTML = "";
            first = false;
          }
          text += evt.text;
          body.innerHTML = window.renderMarkdown(text);
        } else if (evt.type === "error") {
          body.innerHTML = `<span class="muted">Error: ${evt.message}</span>`;
          return;
        }
      }
    }
    if (!first) {
      body.innerHTML = window.renderMarkdown(text);
    }
  }

  run();
})();
