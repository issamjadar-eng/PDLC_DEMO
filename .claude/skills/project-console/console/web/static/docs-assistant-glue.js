/* Glue between the Documents explorer and the generic Assistant drawer.
 *
 * - Enables the floating "Ask about this doc" button when a file is selected.
 * - Provides `window.pcAssistantGetGrounding()` so the drawer can fetch the
 *   selected file's body text at send time (picks up the latest selection).
 * - Updates the drawer subtitle with the selected path.
 *
 * The explorer stores its selected-path in localStorage under
 * `project-console:docs-explorer:v1`. We poll that + the `.selected` class
 * in the tree, which is the source of truth the user sees.
 */
(function () {
  const fab = document.getElementById('docs-assistant-fab');
  if (!fab) return;

  const EXPLORER_STATE_KEY = 'project-console:docs-explorer:v1';

  function getSelectedPath() {
    try {
      const raw = localStorage.getItem(EXPLORER_STATE_KEY);
      if (!raw) return null;
      const s = JSON.parse(raw);
      return s && s.selectedPath ? s.selectedPath : null;
    } catch (e) { return null; }
  }

  async function fetchFileText(path) {
    try {
      const r = await fetch(`/documents/api/file?path=${encodeURIComponent(path)}`);
      if (!r.ok) return '';
      const data = await r.json();
      // Prefer the body_text (markdown/text/html text); fall back to frontmatter stringified.
      const fm = data.frontmatter
        ? '---\n' + JSON.stringify(data.frontmatter, null, 2) + '\n---\n\n'
        : '';
      const body = data.body_text || data.body_html || '';
      return `# ${data.filename} (${data.path})\n\n${fm}${body}`;
    } catch (e) {
      return '';
    }
  }

  // Drawer calls this at send time. Live — picks up the latest selection.
  window.pcAssistantGetGrounding = async function () {
    const p = getSelectedPath();
    if (!p) return '';
    return await fetchFileText(p);
  };

  function refreshFab() {
    const p = getSelectedPath();
    fab.disabled = !p;
    if (p) {
      fab.title = `Ask about ${p}`;
      if (window.pcAssistantSetSubtitle) window.pcAssistantSetSubtitle(p);
    } else {
      fab.title = 'Select a file first';
      if (window.pcAssistantSetSubtitle) window.pcAssistantSetSubtitle('');
    }
  }

  // Initial state + periodic sync. The explorer writes to localStorage
  // synchronously on selection so a short poll is sufficient.
  refreshFab();
  window.addEventListener('storage', (e) => {
    if (e.key === EXPLORER_STATE_KEY) refreshFab();
  });
  // Same-tab writes don't fire 'storage', so poll lightly.
  setInterval(refreshFab, 500);
})();
