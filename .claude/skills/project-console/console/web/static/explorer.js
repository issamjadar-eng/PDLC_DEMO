const treeEl = document.getElementById("docs-tree");
const metaEl = document.getElementById("docs-meta");
const contentEl = document.getElementById("docs-content");
const collapseAllBtn = document.getElementById("docs-collapse-all");

const STATE_KEY = "project-console:docs-explorer:v1";
const WIDTH_KEY = "project-console:docs-explorer:tree-width";
const MIN_TREE_W = 180;
const MAX_TREE_W = 720;
let state = { expanded: {}, selectedPath: null };
// Cache children for lazy-loaded dirs so collapsing + re-expanding doesn't refetch.
const childrenCache = {};

function loadState() {
  try {
    const raw = localStorage.getItem(STATE_KEY);
    if (raw) {
      const saved = JSON.parse(raw);
      if (saved && typeof saved === "object") {
        state = { expanded: saved.expanded || {}, selectedPath: saved.selectedPath || null };
      }
    }
  } catch (e) {
    console.warn("Failed to load explorer state:", e);
  }
}

function persistState() {
  try {
    localStorage.setItem(STATE_KEY, JSON.stringify(state));
  } catch (e) {
    console.warn("Failed to persist explorer state:", e);
  }
}

function formatSize(bytes) {
  if (bytes === null || bytes === undefined) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function renderTree(nodes) {
  const ul = document.createElement("ul");
  ul.className = "tree-list tree-root";
  for (const node of nodes) {
    ul.appendChild(renderNode(node));
  }
  return ul;
}

function renderNode(node) {
  const li = document.createElement("li");
  li.className = "tree-node" + (node.is_dir ? " is-dir" : " is-file");
  li.dataset.path = node.path;

  const row = document.createElement("div");
  row.className = "tree-row";

  if (node.is_dir) {
    const toggle = document.createElement("span");
    toggle.className = "tree-toggle";
    toggle.textContent = state.expanded[node.path] ? "▾" : "▸";
    row.appendChild(toggle);
  } else {
    const spacer = document.createElement("span");
    spacer.className = "tree-toggle tree-toggle-empty";
    row.appendChild(spacer);
  }

  const icon = document.createElement("span");
  icon.className = "tree-icon";
  icon.textContent = node.is_dir ? "📁" : fileIcon(node.name);
  row.appendChild(icon);

  const label = document.createElement("span");
  label.className = "tree-label";
  label.textContent = node.name;
  row.appendChild(label);

  if (!node.is_dir && node.size !== null && node.size !== undefined) {
    const meta = document.createElement("span");
    meta.className = "tree-meta";
    meta.textContent = formatSize(node.size);
    row.appendChild(meta);
  }

  if (state.selectedPath === node.path) {
    row.classList.add("selected");
  }

  row.addEventListener("click", (e) => {
    e.stopPropagation();
    if (node.is_dir) {
      toggleDir(li, node);
      selectFolder(node);
    } else {
      selectFile(node);
    }
  });

  li.appendChild(row);

  if (node.is_dir) {
    const childUl = document.createElement("ul");
    childUl.className = "tree-list";
    if (Array.isArray(node.children)) {
      for (const child of node.children) {
        childUl.appendChild(renderNode(child));
      }
      childrenCache[node.path] = node.children;
    }
    childUl.style.display = state.expanded[node.path] ? "" : "none";
    li.appendChild(childUl);
  }

  return li;
}

function fileIcon(name) {
  const lower = name.toLowerCase();
  if (lower.endsWith(".md")) return "📝";
  if (lower.endsWith(".yml") || lower.endsWith(".yaml")) return "⚙";
  if (lower.endsWith(".json")) return "⚙";
  if (lower.endsWith(".pdf")) return "📕";
  if (lower.endsWith(".png") || lower.endsWith(".jpg") || lower.endsWith(".jpeg") || lower.endsWith(".svg") || lower.endsWith(".gif") || lower.endsWith(".webp")) return "🖼";
  if (lower.endsWith(".py")) return "🐍";
  return "📄";
}

async function toggleDir(li, node) {
  const toggle = li.querySelector(":scope > .tree-row > .tree-toggle");
  const childUl = li.querySelector(":scope > ul.tree-list");
  const isOpen = state.expanded[node.path];
  if (isOpen) {
    state.expanded[node.path] = false;
    toggle.textContent = "▸";
    childUl.style.display = "none";
    persistState();
    return;
  }
  // Lazy-load if empty and the node says it has children.
  if (childUl.children.length === 0 && node.has_children) {
    toggle.textContent = "…";
    const cached = childrenCache[node.path];
    let children = cached;
    if (!children) {
      try {
        const r = await fetch(`/documents/api/children?path=${encodeURIComponent(node.path)}`);
        const data = await r.json();
        children = data.children || [];
        childrenCache[node.path] = children;
      } catch (e) {
        toggle.textContent = "▸";
        return;
      }
    }
    for (const child of children) {
      childUl.appendChild(renderNode(child));
    }
  }
  state.expanded[node.path] = true;
  toggle.textContent = "▾";
  childUl.style.display = "";
  persistState();
}

function highlightRow(path) {
  treeEl.querySelectorAll(".tree-row.selected").forEach((el) => el.classList.remove("selected"));
  const li = treeEl.querySelector(`li[data-path="${cssEscape(path)}"]`);
  if (li) {
    const row = li.querySelector(":scope > .tree-row");
    if (row) row.classList.add("selected");
  }
}

async function selectFile(node) {
  state.selectedPath = node.path;
  persistState();
  highlightRow(node.path);
  await loadFile(node.path);
}

async function selectFolder(node) {
  state.selectedPath = node.path;
  persistState();
  highlightRow(node.path);
  let data;
  try {
    const r = await fetch(`/documents/api/folder?path=${encodeURIComponent(node.path)}`);
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    data = await r.json();
  } catch (e) {
    clearPanes(`Error: ${e.message}`);
    return;
  }
  if (data.readme) {
    renderMeta(data.readme);
    renderContent(data.readme);
  } else {
    clearPanes(`No README in ${node.name}.`);
  }
}

function clearPanes(message) {
  metaEl.innerHTML = `<div class="docs-placeholder muted">${message || ""}</div>`;
  contentEl.innerHTML = "";
}

function cssEscape(s) {
  return s.replace(/"/g, '\\"');
}

async function loadFile(path) {
  metaEl.innerHTML = '<div class="docs-placeholder muted">Loading…</div>';
  contentEl.innerHTML = '<div class="docs-placeholder muted">Loading…</div>';
  let data;
  try {
    const r = await fetch(`/documents/api/file?path=${encodeURIComponent(path)}`);
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    data = await r.json();
  } catch (e) {
    metaEl.innerHTML = `<div class="docs-placeholder error">Error: ${e.message}</div>`;
    contentEl.innerHTML = "";
    return;
  }
  renderMeta(data);
  renderContent(data);
}

function renderMeta(data) {
  metaEl.innerHTML = "";
  const head = document.createElement("div");
  head.className = "docs-meta-head";
  const h2 = document.createElement("h2");
  h2.textContent = data.filename;
  head.appendChild(h2);
  const path = document.createElement("p");
  path.className = "muted small mono";
  path.textContent = data.path;
  head.appendChild(path);

  const chips = document.createElement("div");
  chips.className = "docs-chips";
  chips.appendChild(chip(data.kind));
  chips.appendChild(chip(formatSize(data.size)));
  if (data.extension) chips.appendChild(chip(data.extension));
  head.appendChild(chips);

  const actions = document.createElement("div");
  actions.className = "docs-meta-actions";
  const downloadLink = document.createElement("a");
  downloadLink.href = data.download_url || data.raw_url;
  downloadLink.className = "link-button";
  downloadLink.textContent = "Download";
  actions.appendChild(downloadLink);
  const openRawLink = document.createElement("a");
  openRawLink.href = data.raw_url;
  openRawLink.target = "_blank";
  openRawLink.rel = "noopener";
  openRawLink.className = "link-button";
  openRawLink.textContent = "Open in new tab";
  actions.appendChild(openRawLink);
  head.appendChild(actions);

  metaEl.appendChild(head);

  if (data.frontmatter && Object.keys(data.frontmatter).length > 0) {
    const fm = document.createElement("details");
    fm.className = "docs-frontmatter";
    fm.open = true;
    const sum = document.createElement("summary");
    sum.textContent = "Frontmatter";
    fm.appendChild(sum);
    const pre = document.createElement("pre");
    pre.className = "mono small";
    pre.textContent = JSON.stringify(data.frontmatter, null, 2);
    fm.appendChild(pre);
    metaEl.appendChild(fm);
  }

  const summaryBox = document.createElement("div");
  summaryBox.className = "docs-summary";
  const summaryHead = document.createElement("div");
  summaryHead.className = "docs-summary-head";
  const summaryTitle = document.createElement("strong");
  summaryTitle.textContent = "AI summary";
  summaryHead.appendChild(summaryTitle);
  if (data.summarizable) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn-small";
    btn.textContent = "Summarize";
    btn.addEventListener("click", () => streamSummary(data.path, btn, summaryBody));
    summaryHead.appendChild(btn);
  }
  summaryBox.appendChild(summaryHead);
  const summaryBody = document.createElement("div");
  summaryBody.className = "docs-summary-body md-content";
  summaryBody.innerHTML = data.summarizable
    ? '<p class="muted small">Click Summarize to generate a short AI summary of this file.</p>'
    : '<p class="muted small">Summaries are only available for text-based files (markdown, HTML, text).</p>';
  summaryBox.appendChild(summaryBody);
  metaEl.appendChild(summaryBox);
}

function chip(text) {
  const span = document.createElement("span");
  span.className = "docs-chip";
  span.textContent = text;
  return span;
}

async function streamSummary(path, btn, body) {
  btn.disabled = true;
  btn.textContent = "Summarizing…";
  body.innerHTML = "";
  let buffer = "";
  try {
    const resp = await fetch(`/documents/summary/${encodeURIComponent(path)}`, { method: "POST" });
    if (!resp.ok || !resp.body) throw new Error(`${resp.status} ${resp.statusText}`);
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
        if (evt.type === "token") {
          buffer += evt.text;
          body.innerHTML = window.renderMarkdown(buffer);
        } else if (evt.type === "error") {
          body.innerHTML = `<p class="error">Error: ${evt.message}</p>`;
        }
      }
    }
  } catch (e) {
    body.innerHTML = `<p class="error">Error: ${e.message}</p>`;
  } finally {
    btn.disabled = false;
    btn.textContent = "Regenerate";
  }
}

// ---------------- Lightweight YAML / JSON highlighter ----------------
//
// Regex-based, line-oriented. Not a real parser — it recognises the tokens
// that matter for readability: comments, keys, strings, numbers, booleans,
// nulls, list markers, and anchors/aliases. Enough to make YAML + JSON
// readable without vendoring a syntax highlighter.

function escapeHtml(s) {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// ---- Relative-link rewriting -----------------------------------------------
// Markdown source files use standard relative paths (e.g. `[x](../foo.md)`)
// so they stay portable — VS Code, GitHub, and git tools all resolve those
// natively against the source file's location. The browser can't: by default
// it resolves the href against the current URL (`/documents#path=...`), which
// is not where the source file lives. This helper rewrites each <a href>
// inside the rendered markdown body so clicking navigates the viewer to the
// correctly-resolved virtual path. Mirrors what VS Code's markdown preview
// does invisibly.

function resolveRelativeVirtualPath(basePath, href) {
  // Strip hash + query; preserve hash for re-attach after resolution.
  const hashIdx = href.indexOf("#");
  const hash = hashIdx >= 0 ? href.slice(hashIdx) : "";
  let target = hashIdx >= 0 ? href.slice(0, hashIdx) : href;
  // Empty target (pure anchor) → stay on same doc; the hash scrolls natively
  if (!target) return { path: basePath, hash };

  // Absolute path (leading /) — treat as repo-rooted virtual path
  if (target.startsWith("/")) {
    return { path: target.replace(/^\/+/, ""), hash };
  }

  // Relative path — resolve against the SOURCE file's directory, not the
  // browser URL. Split the base virtual path, drop the filename, then walk.
  const baseParts = basePath.split("/");
  baseParts.pop(); // drop filename
  const segments = [...baseParts, ...target.split("/")];
  const resolved = [];
  for (const seg of segments) {
    if (seg === "" || seg === ".") continue;
    if (seg === "..") {
      resolved.pop();
    } else {
      resolved.push(seg);
    }
  }
  return { path: resolved.join("/"), hash };
}

function rewriteRelativeLinks(div, basePath) {
  if (!basePath) return;
  div.querySelectorAll("a[href]").forEach((a) => {
    const raw = a.getAttribute("href");
    if (!raw) return;
    // Leave external and non-navigable schemes alone
    if (/^(https?|mailto|tel|javascript|data):/i.test(raw)) return;
    if (raw.startsWith("//")) return;
    // Pure anchor (#section) — let the browser scroll within current view
    if (raw.startsWith("#")) return;

    const { path: targetPath, hash } = resolveRelativeVirtualPath(basePath, raw);
    if (!targetPath) return;

    // Set a real href so copy-link / open-in-new-tab works out of the box
    const encoded = targetPath.split("/").map(encodeURIComponent).join("/");
    a.setAttribute("href", `/documents#path=${encoded}${hash}`);
    // In-viewer click navigates without a full reload
    a.addEventListener("click", (ev) => {
      if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.button !== 0) return;
      ev.preventDefault();
      if (typeof revealAndSelect === "function") {
        revealAndSelect(targetPath).then(() => {
          if (hash) {
            // Scroll to heading anchor after the new doc renders
            setTimeout(() => {
              const el = document.getElementById(hash.slice(1));
              if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
            }, 100);
          }
        });
      } else {
        window.location.hash = `path=${encoded}${hash}`;
      }
    });
  });
}

function highlightYaml(text) {
  if (!text) return "";
  const lines = text.split("\n");
  const out = [];
  for (const raw of lines) {
    out.push(highlightYamlLine(raw));
  }
  return out.join("\n");
}

function highlightYamlLine(line) {
  // Strip off a trailing comment first (naïve: a `#` that isn't inside a quoted string).
  let commentIdx = -1;
  let inSingle = false;
  let inDouble = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === "'" && !inDouble) inSingle = !inSingle;
    else if (ch === '"' && !inSingle) inDouble = !inDouble;
    else if (ch === "#" && !inSingle && !inDouble) {
      if (i === 0 || /\s/.test(line[i - 1])) {
        commentIdx = i;
        break;
      }
    }
  }
  let body = line;
  let comment = "";
  if (commentIdx >= 0) {
    body = line.slice(0, commentIdx);
    comment = line.slice(commentIdx);
  }

  let html = highlightYamlBody(body);
  if (comment) html += `<span class="yml-comment">${escapeHtml(comment)}</span>`;
  return html;
}

function highlightYamlBody(body) {
  // Leading whitespace preserved verbatim.
  const leadMatch = body.match(/^(\s*)/);
  const lead = leadMatch ? leadMatch[1] : "";
  let rest = body.slice(lead.length);

  if (rest === "") return escapeHtml(lead);
  if (rest === "---" || rest === "...") {
    return escapeHtml(lead) + `<span class="yml-anchor">${escapeHtml(rest)}</span>`;
  }

  // List marker "- " at start.
  let listPrefix = "";
  if (rest.startsWith("- ") || rest === "-") {
    listPrefix = '<span class="yml-punct">-</span>';
    rest = rest.slice(1);
    if (rest.startsWith(" ")) {
      listPrefix += " ";
      rest = rest.slice(1);
    }
  }

  // Key detection: identifier (or quoted) followed by `:` then space/end.
  const keyMatch = rest.match(/^("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|[A-Za-z0-9_.\-]+)(\s*:)(\s*)(.*)$/);
  if (keyMatch) {
    const [, key, colon, space, value] = keyMatch;
    return (
      escapeHtml(lead) +
      listPrefix +
      `<span class="yml-key">${escapeHtml(key)}</span>` +
      `<span class="yml-punct">${escapeHtml(colon)}</span>` +
      escapeHtml(space) +
      highlightYamlScalar(value)
    );
  }

  return escapeHtml(lead) + listPrefix + highlightYamlScalar(rest);
}

function highlightYamlScalar(value) {
  if (value === "") return "";
  // Anchors / aliases: &foo, *bar
  if (/^[&*][A-Za-z0-9_.\-]+/.test(value)) {
    const m = value.match(/^([&*][A-Za-z0-9_.\-]+)(.*)$/);
    return `<span class="yml-anchor">${escapeHtml(m[1])}</span>${escapeHtml(m[2])}`;
  }
  // Quoted string (single or double).
  if (/^".*"$/.test(value) || /^'.*'$/.test(value)) {
    return `<span class="yml-string">${escapeHtml(value)}</span>`;
  }
  // Bool / null.
  if (/^(true|false|yes|no|on|off|null|~)$/i.test(value)) {
    return `<span class="yml-bool">${escapeHtml(value)}</span>`;
  }
  // Number (int, float, scientific).
  if (/^-?(\d+\.\d+|\d+)([eE][-+]?\d+)?$/.test(value)) {
    return `<span class="yml-number">${escapeHtml(value)}</span>`;
  }
  // Inline flow collections left as plain text; unquoted scalars styled as strings.
  if (value.startsWith("{") || value.startsWith("[")) {
    return escapeHtml(value);
  }
  return `<span class="yml-string">${escapeHtml(value)}</span>`;
}

function highlightJson(text) {
  // JSON reuses the yaml highlighter's scalar classes via a single pass regex.
  const escaped = escapeHtml(text || "");
  return escaped
    .replace(/("(?:\\.|[^"\\])*")(\s*:)/g, '<span class="yml-key">$1</span><span class="yml-punct">$2</span>')
    .replace(/("(?:\\.|[^"\\])*")(?!\s*:)/g, '<span class="yml-string">$1</span>')
    .replace(/\b(true|false|null)\b/g, '<span class="yml-bool">$1</span>')
    .replace(/(-?\b\d+(?:\.\d+)?(?:[eE][-+]?\d+)?\b)/g, '<span class="yml-number">$1</span>');
}

function renderContent(data) {
  contentEl.innerHTML = "";
  if (data.kind === "markdown") {
    const div = document.createElement("div");
    div.className = "md-content docs-rendered";
    div.innerHTML = data.body_html;
    rewriteRelativeLinks(div, data.path);
    contentEl.appendChild(div);
  } else if (data.kind === "text") {
    const ext = (data.extension || "").toLowerCase();
    const pre = document.createElement("pre");
    pre.className = "docs-text mono small";
    if (ext === ".yml" || ext === ".yaml" || data.filename === "project.yml") {
      pre.classList.add("lang-yaml");
      pre.innerHTML = highlightYaml(data.body_text);
    } else if (ext === ".json") {
      pre.classList.add("lang-yaml");
      pre.innerHTML = highlightJson(data.body_text);
    } else {
      pre.textContent = data.body_text;
    }
    contentEl.appendChild(pre);
  } else if (data.kind === "html") {
    const iframe = document.createElement("iframe");
    iframe.src = data.raw_url;
    iframe.className = "docs-iframe";
    contentEl.appendChild(iframe);
  } else if (data.kind === "pdf") {
    // <iframe> is the most reliable cross-browser way to show a PDF inline.
    // <object>/<embed> fall back to downloading in some browsers; iframe
    // triggers the built-in PDF viewer in Chrome, Safari, and Firefox.
    const iframe = document.createElement("iframe");
    iframe.src = data.raw_url;
    iframe.className = "docs-iframe docs-pdf";
    iframe.setAttribute("title", data.filename);
    contentEl.appendChild(iframe);
  } else if (data.kind === "image") {
    const img = document.createElement("img");
    img.src = data.raw_url;
    img.alt = data.filename;
    img.className = "docs-image";
    contentEl.appendChild(img);
  } else {
    const p = document.createElement("p");
    p.className = "muted";
    p.textContent = `Binary file (${data.extension || "unknown"}) — use Download raw to view.`;
    contentEl.appendChild(p);
  }
}

function autoExpandPrefetched(nodes) {
  // Mark every dir whose children arrived in the initial payload as expanded,
  // so the first three prefetched layers are visible on first load. Dirs past
  // the prefetch horizon lack a `children` key and stay collapsed until the
  // user clicks them (lazy-loaded via /documents/api/children).
  const walk = (node) => {
    if (!node.is_dir) return;
    if (Array.isArray(node.children)) {
      state.expanded[node.path] = true;
      for (const c of node.children) walk(c);
    }
  };
  for (const n of nodes) walk(n);
}

async function loadInitialTree() {
  try {
    const r = await fetch("/documents/api/tree");
    const data = await r.json();
    const nodes = data.nodes || [];
    // On fresh load (no persisted expansion state), auto-expand the three
    // prefetched layers. On return visits honor whatever the user had open.
    if (!state.expanded || Object.keys(state.expanded).length === 0) {
      autoExpandPrefetched(nodes);
      persistState();
    }
    treeEl.innerHTML = "";
    treeEl.appendChild(renderTree(nodes));
    // Honor deep-link via URL fragment ?path=... or #path=...
    const frag = window.location.hash;
    if (frag.startsWith("#path=")) {
      const targetPath = decodeURIComponent(frag.slice(6));
      await revealAndSelect(targetPath);
    } else if (state.selectedPath) {
      await loadFile(state.selectedPath);
    }
  } catch (e) {
    treeEl.innerHTML = `<p class="error">Failed to load tree: ${e.message}</p>`;
  }
}

async function revealAndSelect(path) {
  // Expand each ancestor directory in order, then select the leaf file.
  const parts = path.split("/");
  for (let i = 1; i < parts.length; i++) {
    const ancestor = parts.slice(0, i).join("/");
    if (!state.expanded[ancestor]) {
      const li = treeEl.querySelector(`li[data-path="${cssEscape(ancestor)}"]`);
      if (li) {
        const row = li.querySelector(":scope > .tree-row");
        if (row) row.click();
        // Give the click handler time to lazy-load + render.
        await new Promise((r) => setTimeout(r, 50));
      }
    }
  }
  const li = treeEl.querySelector(`li[data-path="${cssEscape(path)}"]`);
  if (li) {
    const row = li.querySelector(":scope > .tree-row");
    if (row) row.click();
    li.scrollIntoView({ block: "center" });
  } else {
    await loadFile(path);
  }
}

// ---------------- Resizer: drag to adjust tree pane width ----------------

function applyTreeWidth(width) {
  const clamped = Math.max(MIN_TREE_W, Math.min(MAX_TREE_W, width));
  document.documentElement.style.setProperty("--docs-tree-w", `${clamped}px`);
  return clamped;
}

function loadTreeWidth() {
  const saved = parseInt(localStorage.getItem(WIDTH_KEY) || "", 10);
  if (!Number.isNaN(saved)) applyTreeWidth(saved);
}

(function initResizer() {
  const resizer = document.getElementById("docs-resizer");
  if (!resizer) return;
  let dragging = false;
  const onMove = (e) => {
    if (!dragging) return;
    const layout = resizer.parentElement;
    const left = layout.getBoundingClientRect().left;
    const next = applyTreeWidth(e.clientX - left);
    localStorage.setItem(WIDTH_KEY, String(next));
  };
  const onUp = () => {
    if (!dragging) return;
    dragging = false;
    resizer.classList.remove("dragging");
    document.body.classList.remove("resizing");
    document.removeEventListener("mousemove", onMove);
    document.removeEventListener("mouseup", onUp);
  };
  resizer.addEventListener("mousedown", (e) => {
    e.preventDefault();
    dragging = true;
    resizer.classList.add("dragging");
    document.body.classList.add("resizing");
    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup", onUp);
  });
  resizer.addEventListener("dblclick", () => {
    applyTreeWidth(340);
    localStorage.setItem(WIDTH_KEY, "340");
  });
})();

collapseAllBtn.addEventListener("click", () => {
  state.expanded = {};
  persistState();
  treeEl.querySelectorAll("ul.tree-list:not(.tree-root)").forEach((ul) => {
    ul.style.display = "none";
  });
  treeEl.querySelectorAll(".tree-toggle").forEach((t) => {
    if (!t.classList.contains("tree-toggle-empty")) t.textContent = "▸";
  });
});

loadState();
loadTreeWidth();
loadInitialTree();
