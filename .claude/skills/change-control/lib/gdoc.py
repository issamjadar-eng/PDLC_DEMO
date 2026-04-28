"""High-level Google Docs operations on top of web-control's CDP primitives.

Owns the "what does internal review actually do to a gdoc" layer:

  - ensure folder hierarchy exists in Drive
  - create a new gdoc and paste md content (markdown auto-format)
  - read open comments + suggestions + body content
  - post a reply + resolve a comment
  - accept / reject a suggestion
  - replace doc body wholesale
  - apply archive treatment on freeze (banner + rename + close comments)

Consumers: change-control's review-* and freeze actions.

Note on web-control coupling: this module imports from web-control's lib
package. web-control must be installed in the same project (the build
relies on the symlink installed by web-control setup).
"""
from __future__ import annotations

import importlib.util
import sys
import time
from dataclasses import dataclass
from pathlib import Path

# Locate web-control's lib via the project's skill folder
_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_WEB_CONTROL_DIR = _PROJECT_ROOT / ".claude" / "skills" / "web-control"
_WEB_CONTROL_LIB = _WEB_CONTROL_DIR / "lib"

# Web-control's lib package and change-control's lib package both happen to
# be named `lib`. To avoid the sys.modules collision, we load web-control's
# lib explicitly via importlib under a unique module name (`web_control_lib`).
# Submodule search locations make web-control's relative imports resolve
# correctly inside that namespace.
_WC_CACHE: dict | None = None


def _wc() -> dict:
    global _WC_CACHE
    if _WC_CACHE is not None:
        return _WC_CACHE

    pkg_name = "web_control_lib"
    if pkg_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            pkg_name,
            _WEB_CONTROL_LIB / "__init__.py",
            submodule_search_locations=[str(_WEB_CONTROL_LIB)],
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"could not locate web-control lib at {_WEB_CONTROL_LIB}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[pkg_name] = module
        spec.loader.exec_module(module)
    wc = sys.modules[pkg_name]

    _WC_CACHE = {
        "connect_to_chrome": wc.connect_to_chrome,
        "Modifiers": wc.Modifiers,
        "keyboard_shortcut": wc.keyboard_shortcut,
        "type_text": wc.type_text,
        "click_at": wc.click_at,
        "send_key": wc.send_key,
        "get_a11y_text": wc.get_a11y_text,
        "is_signed_in": wc.is_signed_in,
        "WebControlError": wc.WebControlError,
        "SignInRequired": wc.SignInRequired,
    }
    return _WC_CACHE


# ----------------------------------------------------------------------------
# Data shapes returned by status reads
# ----------------------------------------------------------------------------


@dataclass
class GdocComment:
    id: str  # gdoc-internal comment id
    author: str
    anchor_text: str
    text: str
    created: str  # ISO-ish; gdoc surfaces "11:44 AM Today" etc — captured verbatim


@dataclass
class GdocSuggestion:
    id: str
    author: str
    anchor_text: str
    before: str
    after: str


@dataclass
class GdocBody:
    text: str  # full doc body via a11y tree (SR mode required)
    sr_mode_was_off: bool  # if we had to enable it


# ----------------------------------------------------------------------------
# Connection
# ----------------------------------------------------------------------------


def open_gdoc_tab(gdoc_url: str):
    """Connect to web-control's debug Chrome and ensure the tab is on the
    given gdoc URL. Returns the connected Chrome handle and the tab.

    Raises if web-control isn't running or the user isn't signed in.
    """
    wc = _wc()
    chrome = wc["connect_to_chrome"]()  # raises ChromeNotRunning if not up
    # Find an existing tab on this gdoc, or create one
    target = chrome.find_tab(lambda t: gdoc_url in t.url)
    if target is None:
        target = chrome.new_tab(gdoc_url)
        time.sleep(2)  # let the doc load
    return chrome, target


# ----------------------------------------------------------------------------
# Folder hierarchy + new doc creation
# ----------------------------------------------------------------------------


def ensure_drive_folder_hierarchy(folder_components: list[str]) -> str:
    """Ensure each level of the folder path exists in Drive. Returns a
    drive folder URL the caller can navigate to.

    NOTE: v0.1 implementation — drives the Drive web UI to create folders
    if they don't exist. Idempotent; if the folders are already there,
    just returns the URL of the deepest one.

    For v0.1 simplicity this returns the Drive home URL — the calling
    code should navigate manually + walk into AI_PDLC/<project>/<user>/.
    Auto-folder-creation is deferred; the user creates these once
    manually on first push (matches the manual-share-via-Drive pattern of Q5).
    """
    # v0.1: we trust the user has created the AI_PDLC/<project>/<task_folder>/
    # folder hierarchy on first use. Auto-creation = v0.2.
    # Return the my-drive URL as the launching point.
    return "https://drive.google.com/drive/my-drive"


def create_new_gdoc(name: str, folder_url: str) -> str:
    """Open Drive at folder_url, create a new Google Doc, rename it,
    return the new gdoc URL.

    v0.1 implementation: navigates to docs.google.com/document/u/0/create
    (which creates a new gdoc in My Drive root by default), then renames
    the title via the title-edit affordance, then if a folder was
    requested, moves the doc via "Move to" menu. For v0.1, the move step
    is deferred — user manually moves on first push if they want a
    specific folder. New gdocs land in My Drive root.

    Returns the gdoc edit URL.
    """
    wc = _wc()
    chrome = wc["connect_to_chrome"]()
    tab = chrome.new_tab("https://docs.google.com/document/u/0/create")

    # Wait for the new doc to land. Drive sometimes rate-limits rapid
    # creates; we give it a generous window and report clearly on failure.
    deadline = time.time() + 60
    with chrome.with_page(tab) as page:
        last_url = ""
        while time.time() < deadline:
            url = page.eval("location.href") or ""
            last_url = url
            if "/document/d/" in url:
                time.sleep(2)  # let the editor settle
                break
            time.sleep(1)
        else:
            raise RuntimeError(
                f"new gdoc did not load within 60s (last URL: {last_url}). "
                f"Drive may be rate-limiting after rapid creates; wait a "
                f"minute and retry."
            )

        # Rename the doc (Ctrl+S would save, but the title is editable via the
        # title bar at the top — Alt+Shift+T then Ctrl+A then type works in some
        # builds. Simpler: drive to the title via the "Untitled document" element.
        # Use the Docs File menu → Rename (Ctrl+Alt+R, then type, then Enter).
        wc["keyboard_shortcut"](page, "Ctrl+Alt+r")  # may not always work; fallback below
        time.sleep(0.5)
        # Type the name
        wc["type_text"](page, name)
        time.sleep(0.3)
        # Press Enter to commit
        wc["send_key"](page, "Enter", "Enter", 13)
        time.sleep(1)

        # Capture the URL with the doc id
        url = page.eval("location.href") or ""
    return url


def enable_markdown_preference(chrome) -> bool:
    """One-time per profile: turn on Tools → Preferences → Markdown.

    Idempotent. Returns True if the preference is on (whether it was
    already on or we just turned it on). Returns False on failure.

    v0.2 implementation: drives the menu via DOM. Approach:
      1. Find a doc tab (creates none — caller ensures one exists).
      2. Click the Tools menu (id 'docs-tools-menu' or aria-label 'Tools').
      3. Click "Preferences" item.
      4. Find the "Automatically detect Markdown" / "Enable Markdown"
         checkbox in the dialog and ensure it's checked.
      5. Click OK.

    The dialog selector + checkbox label varies across Google Docs UI
    builds; we try several known patterns. If none match, returns False
    and prints what was tried (the user can do this manually once).
    """
    wc = _wc()
    tab = chrome.find_tab(lambda t: "/document/d/" in t.url)
    if tab is None:
        return False

    with chrome.with_page(tab) as page:
        # Click Tools menu
        clicked = page.eval(
            """
            (() => {
                const menus = Array.from(document.querySelectorAll('[role="menubar"] [role="menuitem"], [aria-label="Tools"]'));
                const tools = menus.find(m => /^Tools$/i.test(m.getAttribute('aria-label')||m.textContent||''));
                if (!tools) return false;
                const r = tools.getBoundingClientRect();
                const opts = {bubbles: true, cancelable: true, view: window,
                              clientX: r.left + r.width/2, clientY: r.top + r.height/2};
                tools.dispatchEvent(new MouseEvent('mousedown', opts));
                tools.dispatchEvent(new MouseEvent('mouseup', opts));
                tools.dispatchEvent(new MouseEvent('click', opts));
                return true;
            })()
            """
        )
        if not clicked:
            print("  enable_markdown_preference: Tools menu not found")
            return False
        time.sleep(0.7)

        # Click Preferences item in the dropdown
        clicked = page.eval(
            """
            (() => {
                const items = Array.from(document.querySelectorAll('[role="menuitem"]'));
                const pref = items.find(i => i.offsetParent !== null &&
                    /preferences/i.test(i.getAttribute('aria-label')||i.textContent||''));
                if (!pref) return false;
                const r = pref.getBoundingClientRect();
                const opts = {bubbles: true, cancelable: true, view: window,
                              clientX: r.left + r.width/2, clientY: r.top + r.height/2};
                pref.dispatchEvent(new MouseEvent('mousedown', opts));
                pref.dispatchEvent(new MouseEvent('mouseup', opts));
                pref.dispatchEvent(new MouseEvent('click', opts));
                return true;
            })()
            """
        )
        if not clicked:
            # Close the menu
            wc["send_key"](page, "Escape", "Escape", 27)
            print("  enable_markdown_preference: Preferences item not found")
            return False
        time.sleep(1.5)

        # Ensure Markdown checkbox is checked
        toggled = page.eval(
            """
            (() => {
                const labels = Array.from(document.querySelectorAll('label, [role="checkbox"], .docs-material-button-content'));
                const md = labels.find(l => l.offsetParent !== null &&
                    /markdown/i.test(l.textContent||l.getAttribute('aria-label')||''));
                if (!md) return 'not-found';
                // Find the actual checkbox: either the label has a sibling input,
                // or it's the labelled element itself
                const cb = md.querySelector('input[type="checkbox"]')
                        || md.previousElementSibling
                        || md;
                const isChecked = cb.getAttribute('aria-checked') === 'true' || cb.checked === true;
                if (isChecked) return 'already-on';
                const r = md.getBoundingClientRect();
                const opts = {bubbles: true, cancelable: true, view: window,
                              clientX: r.left + r.width/2, clientY: r.top + r.height/2};
                md.dispatchEvent(new MouseEvent('mousedown', opts));
                md.dispatchEvent(new MouseEvent('mouseup', opts));
                md.dispatchEvent(new MouseEvent('click', opts));
                return 'toggled';
            })()
            """
        )
        time.sleep(0.5)

        # Click OK to dismiss dialog
        page.eval(
            """
            (() => {
                const btns = Array.from(document.querySelectorAll('[role="button"], button'));
                const ok = btns.find(b => b.offsetParent !== null &&
                    /^OK$/i.test((b.getAttribute('aria-label')||b.textContent||'').trim()));
                if (!ok) return false;
                const r = ok.getBoundingClientRect();
                const opts = {bubbles: true, cancelable: true, view: window,
                              clientX: r.left + r.width/2, clientY: r.top + r.height/2};
                ok.dispatchEvent(new MouseEvent('mousedown', opts));
                ok.dispatchEvent(new MouseEvent('mouseup', opts));
                ok.dispatchEvent(new MouseEvent('click', opts));
                return true;
            })()
            """
        )
        time.sleep(0.5)

        if toggled in ("already-on", "toggled"):
            print(f"  enable_markdown_preference: {toggled}")
            return True
        print(f"  enable_markdown_preference: checkbox not found ({toggled})")
        return False


def wait_for_text_in_a11y(gdoc_url: str, expected_text: str, timeout: float = 15.0, poll: float = 1.0) -> bool:
    """Wait until expected_text appears in the gdoc's a11y-tree text.
    Used after wholesale-paste body-replace to confirm the new content
    is reflected before the caller continues."""
    wc = _wc()
    chrome = wc["connect_to_chrome"]()
    tab = chrome.find_tab(lambda t: gdoc_url in t.url)
    if tab is None:
        return False
    deadline = time.time() + timeout
    with chrome.with_page(tab) as page:
        # Ensure SR mode is on (body-text via a11y tree requires it)
        sr_on = bool(page.eval(
            "/Screen reader support enabled/i.test(document.body.innerText)"
        ))
        if not sr_on:
            wc["keyboard_shortcut"](page, "Ctrl+Alt+z")
            time.sleep(1.5)
        page.cmd("Accessibility.enable")
        while time.time() < deadline:
            tree = page.cmd("Accessibility.getFullAXTree")
            for n in tree.get("nodes", []):
                name = (n.get("name") or {}).get("value", "")
                if expected_text in name:
                    return True
            time.sleep(poll)
    return False


def paste_markdown_into_doc(gdoc_url: str, md_content: str, replace_body: bool = True) -> None:
    """Paste md content into the active gdoc. Assumes Tools → Preferences
    → Markdown is on (otherwise the paste lands as plain text).

    If replace_body=True, selects all and clears before pasting.
    """
    wc = _wc()
    chrome = wc["connect_to_chrome"]()
    tab = chrome.find_tab(lambda t: gdoc_url in t.url)
    if tab is None:
        raise RuntimeError(f"no tab found for {gdoc_url}")
    with chrome.with_page(tab) as page:
        page.wait_ready()
        # Click into the doc body to focus
        rect = page.eval(
            "(() => { const p = document.querySelector('.kix-page-paginated, .kix-page'); "
            "if (!p) return null; const r = p.getBoundingClientRect(); "
            "return JSON.stringify({cx: r.left + r.width/2, cy: r.top + 200}); })()"
        )
        if rect:
            import json as _json
            pos = _json.loads(rect)
            wc["click_at"](page, pos["cx"], pos["cy"])
            time.sleep(0.5)

        if replace_body:
            wc["keyboard_shortcut"](page, "Ctrl+A")
            time.sleep(0.3)
            wc["send_key"](page, "Delete", "Delete", 46)
            time.sleep(0.5)

        # Paste content — Input.insertText is the reliable path
        wc["type_text"](page, md_content)
        time.sleep(1.5)


# ----------------------------------------------------------------------------
# Read state
# ----------------------------------------------------------------------------


def list_open_comments(gdoc_url: str) -> list[GdocComment]:
    """Read open comment threads from the gdoc DOM. Validated pattern in
    task ben/116 probes."""
    wc = _wc()
    chrome = wc["connect_to_chrome"]()
    tab = chrome.find_tab(lambda t: gdoc_url in t.url)
    if tab is None:
        return []
    with chrome.with_page(tab) as page:
        raw = page.eval(
            "(() => { "
            "const threads = Array.from(document.querySelectorAll('.docos-docoview-rootreply, [data-anchor-id]')).slice(0, 100); "
            "return JSON.stringify(threads.map(t => ({ "
            "id: t.getAttribute('data-anchor-id') || t.getAttribute('id') || '', "
            "text: (t.innerText || '').slice(0, 1000) "
            "}))); })()"
        )
    if not raw:
        return []
    import json as _json
    out: list[GdocComment] = []
    for i, entry in enumerate(_json.loads(raw)):
        text = entry.get("text", "").strip()
        if not text:
            continue
        # Heuristic parse: "Author\nTimestamp\nComment body..."
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        author = lines[0] if lines else ""
        created = lines[1] if len(lines) > 1 else ""
        body = "\n".join(lines[2:]) if len(lines) > 2 else ""
        out.append(GdocComment(
            id=entry.get("id") or f"comment-{i+1}",
            author=author,
            anchor_text="",  # anchor extraction is fragile; deferred
            text=body,
            created=created,
        ))
    return out


def list_open_suggestions(gdoc_url: str) -> list[GdocSuggestion]:
    """Read open suggestions from the gdoc DOM.

    v0.1 implementation: simple — look for nodes with `kix-suggestion-`
    class. Suggestion-mode UI is more complex than comments; v0.1
    returns a flat list with limited metadata. Caller code can fall
    back to "user resolves manually in gdoc UI" if details are needed.
    """
    wc = _wc()
    chrome = wc["connect_to_chrome"]()
    tab = chrome.find_tab(lambda t: gdoc_url in t.url)
    if tab is None:
        return []
    with chrome.with_page(tab) as page:
        raw = page.eval(
            "(() => { "
            "const sels = ['.docos-suggestion', '.kix-suggestion', '[data-suggestion-id]']; "
            "let nodes = []; "
            "for (const s of sels) { nodes = nodes.concat(Array.from(document.querySelectorAll(s))); } "
            "return JSON.stringify(nodes.slice(0, 50).map(n => ({ "
            "id: n.getAttribute('data-suggestion-id') || n.getAttribute('id') || '', "
            "text: (n.innerText || '').slice(0, 500) "
            "}))); })()"
        )
    import json as _json
    out: list[GdocSuggestion] = []
    if not raw:
        return out
    for i, entry in enumerate(_json.loads(raw)):
        out.append(GdocSuggestion(
            id=entry.get("id") or f"suggestion-{i+1}",
            author="",
            anchor_text="",
            before="",
            after=entry.get("text", "").strip(),
        ))
    return out


def read_body_text(gdoc_url: str) -> GdocBody:
    """Read the full body text via Screen Reader Mode + a11y tree.

    Pattern validated in task ben/116: enable SR mode (Ctrl+Alt+Z) →
    Accessibility.getFullAXTree → filter StaticText nodes → join.
    """
    wc = _wc()
    chrome = wc["connect_to_chrome"]()
    tab = chrome.find_tab(lambda t: gdoc_url in t.url)
    if tab is None:
        return GdocBody(text="", sr_mode_was_off=True)
    with chrome.with_page(tab) as page:
        # Detect current SR mode state
        sr_on = bool(page.eval(
            "/Screen reader support enabled/i.test(document.body.innerText)"
        ))
        if not sr_on:
            wc["keyboard_shortcut"](page, "Ctrl+Alt+z")
            time.sleep(1.5)
        # Pull a11y tree, filter StaticText nodes, join
        text_nodes = wc["get_a11y_text"](page, role_filter=("StaticText",))
        # Filter out UI chrome via simple heuristics
        body_lines = [
            t for t in text_nodes
            if t and not t.startswith(("Banner ", "Screen reader support", "On page", "Controls hidden", "Document tabs"))
            and not t.isdigit()
        ]
        return GdocBody(text="\n".join(body_lines), sr_mode_was_off=not sr_on)


# ----------------------------------------------------------------------------
# Mutation operations
# ----------------------------------------------------------------------------


def post_reply_and_resolve(gdoc_url: str, comment_id: str, reply_text: str) -> bool:
    """Post a reply on the comment and mark it resolved.

    v0.2 implementation: drives the DOM. Steps:
      1. Find the comment thread by ORDER (the Nth thread in DOM order
         corresponds to #c-N in the task doc — caller passes comment_id
         like "c-1" / "c-2"; we use the trailing number as 1-indexed).
      2. Click the thread to activate it (reveals the reply input).
      3. Focus the reply textarea, type the reply text.
      4. Submit via Ctrl+Enter (Google Docs requires this — click on the
         submit button does not fire the right event).
      5. Click the "Mark as resolved and hide discussion" button.

    Limitation: comment_id-to-thread mapping is by DOM order, not by
    server-side comment id. If threads get re-ordered between
    review-status and review-update (e.g., a reviewer adds a new
    comment), the addressed item could land on a different thread.
    Mitigation: review-update should run shortly after the user marks
    items addressed, and any concurrent comment activity is rare.
    """
    wc = _wc()
    chrome = wc["connect_to_chrome"]()
    tab = chrome.find_tab(lambda t: gdoc_url in t.url)
    if tab is None:
        print(f"  ERROR: tab for {gdoc_url} not found")
        return False

    # Parse the trailing index from comment_id (e.g., "c-1" -> 0)
    try:
        idx = int(comment_id.rsplit("-", 1)[-1]) - 1
    except (ValueError, IndexError):
        print(f"  ERROR: cannot parse comment_id {comment_id!r}")
        return False
    if idx < 0:
        idx = 0

    with chrome.with_page(tab) as page:
        # 1. Find the thread by index, click to activate
        thread_clicked = page.eval(
            f"(() => {{ "
            f"const threads = document.querySelectorAll('.docos-docoview-rootreply'); "
            f"if (threads.length <= {idx}) return false; "
            f"const t = threads[{idx}]; "
            f"t.scrollIntoView({{block: 'center'}}); "
            f"t.click(); "
            f"return true; }})()"
        )
        if not thread_clicked:
            print(f"  ERROR: comment thread #{idx + 1} not found in DOM")
            return False
        time.sleep(1.0)

        # 2. Find the reply input + focus it
        focused = page.eval(
            "(() => { const ta = document.querySelector('.docos-input-textarea[aria-label=\"Reply\"]'); "
            "if (!ta) return false; ta.focus(); return true; })()"
        )
        if not focused:
            print(f"  ERROR: reply input not found after clicking thread")
            return False
        time.sleep(0.3)

        # 3. Type the reply
        wc["type_text"](page, reply_text)
        time.sleep(0.5)

        # 4. Submit via Ctrl+Enter (Google Docs commits comments with this)
        wc["send_key"](page, "Enter", "Enter", 13, modifiers=wc["Modifiers"].CTRL)
        time.sleep(2)

        # 5. Click "Mark as resolved and hide discussion".
        # Closure-button (goog-inline-block jfk-button) needs a full
        # mouse-event sequence — .click() alone doesn't fire the handler.
        resolved = page.eval(
            """
            (() => {
                const btn = document.querySelector('[aria-label="Mark as resolved and hide discussion"]');
                if (!btn || btn.offsetParent === null) return false;
                const r = btn.getBoundingClientRect();
                const opts = {bubbles: true, cancelable: true, view: window,
                              clientX: r.left + r.width/2, clientY: r.top + r.height/2,
                              button: 0, buttons: 1};
                btn.dispatchEvent(new MouseEvent('mouseover', opts));
                btn.dispatchEvent(new MouseEvent('mousedown', opts));
                btn.dispatchEvent(new MouseEvent('mouseup', opts));
                btn.dispatchEvent(new MouseEvent('click', opts));
                return true;
            })()
            """
        )
        if not resolved:
            print(f"  WARN: resolve button not found after reply")
            return False
        time.sleep(1.5)

    print(f"  ✓ posted reply + resolved comment {comment_id}")
    return True


def accept_suggestion(gdoc_url: str, suggestion_id: str) -> bool:
    """Accept a suggestion in the gdoc.

    v0.2 implementation: drives the DOM. Suggestions appear with an
    accept-button labeled like "Accept suggestion" in the suggestion
    overlay. Best-effort match by ORDER (suggestion_id like "s-1" maps
    to the 1st visible suggestion in DOM order).
    """
    wc = _wc()
    chrome = wc["connect_to_chrome"]()
    tab = chrome.find_tab(lambda t: gdoc_url in t.url)
    if tab is None:
        return False

    try:
        idx = int(suggestion_id.rsplit("-", 1)[-1]) - 1
    except (ValueError, IndexError):
        idx = 0
    if idx < 0:
        idx = 0

    with chrome.with_page(tab) as page:
        ok = page.eval(
            f"(() => {{ "
            f"const btns = Array.from(document.querySelectorAll('[role=\"button\"], button')); "
            f"const accepts = btns.filter(b => b.offsetParent !== null && "
            f"  /^Accept|Accept suggestion/i.test(b.getAttribute('aria-label')||b.textContent||'')); "
            f"if (accepts.length <= {idx}) return false; "
            f"accepts[{idx}].click(); return true; }})()"
        )
    if ok:
        print(f"  ✓ accepted suggestion {suggestion_id}")
    else:
        print(f"  WARN: could not find Accept button for suggestion {suggestion_id} (may need manual handling)")
    return bool(ok)


def reject_suggestion(gdoc_url: str, suggestion_id: str) -> bool:
    """Reject a suggestion in the gdoc.

    v0.2 implementation: same pattern as accept, looking for "Reject"
    button by order.
    """
    wc = _wc()
    chrome = wc["connect_to_chrome"]()
    tab = chrome.find_tab(lambda t: gdoc_url in t.url)
    if tab is None:
        return False

    try:
        idx = int(suggestion_id.rsplit("-", 1)[-1]) - 1
    except (ValueError, IndexError):
        idx = 0
    if idx < 0:
        idx = 0

    with chrome.with_page(tab) as page:
        ok = page.eval(
            f"(() => {{ "
            f"const btns = Array.from(document.querySelectorAll('[role=\"button\"], button')); "
            f"const rejects = btns.filter(b => b.offsetParent !== null && "
            f"  /^Reject|Reject suggestion/i.test(b.getAttribute('aria-label')||b.textContent||'')); "
            f"if (rejects.length <= {idx}) return false; "
            f"rejects[{idx}].click(); return true; }})()"
        )
    if ok:
        print(f"  ✓ rejected suggestion {suggestion_id}")
    else:
        print(f"  WARN: could not find Reject button for suggestion {suggestion_id}")
    return bool(ok)


def close_all_open_comments(gdoc_url: str, reply_text: str = "Internal review closed; see Confluence.") -> int:
    """Walk every open comment thread; reply with reply_text + resolve.

    Used by archive_gdoc on freeze. Returns number of threads closed.
    """
    wc = _wc()
    chrome = wc["connect_to_chrome"]()
    tab = chrome.find_tab(lambda t: gdoc_url in t.url)
    if tab is None:
        return 0

    closed = 0
    with chrome.with_page(tab) as page:
        # Loop: get the count, then close them one at a time. Each close
        # removes the thread from the active list, so we always operate on
        # index 0.
        max_iters = 50  # safety
        for _ in range(max_iters):
            count = page.eval("document.querySelectorAll('.docos-docoview-rootreply').length") or 0
            if not count:
                break
            page.eval(
                "(() => { const t = document.querySelectorAll('.docos-docoview-rootreply')[0]; "
                "if (t) { t.scrollIntoView({block: 'center'}); t.click(); } })()"
            )
            time.sleep(1)
            page.eval(
                "(() => { const ta = document.querySelector('.docos-input-textarea[aria-label=\"Reply\"]'); "
                "if (ta) ta.focus(); })()"
            )
            time.sleep(0.3)
            wc["type_text"](page, reply_text)
            time.sleep(0.4)
            wc["send_key"](page, "Enter", "Enter", 13, modifiers=wc["Modifiers"].CTRL)
            time.sleep(1.5)
            ok = page.eval(
                "(() => { const b = document.querySelector('[aria-label=\"Mark as resolved and hide discussion\"]'); "
                "if (!b || b.offsetParent === null) return false; b.click(); return true; })()"
            )
            if not ok:
                break
            closed += 1
            time.sleep(1)
    return closed


def rename_gdoc_title(gdoc_url: str, new_title: str) -> bool:
    """Rename the gdoc title via the title-input affordance.

    v0.2 implementation: focus the title element programmatically, clear
    contents, type new title, press Enter to commit.
    """
    wc = _wc()
    chrome = wc["connect_to_chrome"]()
    tab = chrome.find_tab(lambda t: gdoc_url in t.url)
    if tab is None:
        return False

    with chrome.with_page(tab) as page:
        # Focus the title input. Google Docs uses .docs-title-input (a
        # hidden HTML input that becomes visible/active when focused).
        focused = page.eval(
            "(() => { const t = document.querySelector('.docs-title-input'); "
            "if (!t) return false; t.focus(); t.click(); t.select(); return true; })()"
        )
        if not focused:
            print(f"  ERROR: title input not found")
            return False
        time.sleep(0.5)
        # Select all in the input + delete
        wc["keyboard_shortcut"](page, "Ctrl+a")
        time.sleep(0.2)
        wc["send_key"](page, "Delete", "Delete", 46)
        time.sleep(0.3)
        # Type new title
        wc["type_text"](page, new_title)
        time.sleep(0.5)
        # Commit with Enter
        wc["send_key"](page, "Enter", "Enter", 13)
        time.sleep(1.5)

    # Verify the page title reflects the change
    with chrome.with_page(tab) as page:
        actual = page.eval("document.title") or ""
    if new_title in actual:
        print(f"  ✓ title renamed to {new_title!r} (page title now {actual!r})")
        return True
    else:
        print(f"  WARN: title may not have committed (page title: {actual!r})")
        return False


# ----------------------------------------------------------------------------
# Archive on freeze (Q7)
# ----------------------------------------------------------------------------


def archive_gdoc(gdoc_url: str, freeze_date: str, confluence_link: str = "", original_title: str | None = None) -> dict:
    """Apply the freeze archive treatment to a gdoc.

    v0.2 implementation:
      1. Prepend the archived-banner to the body
      2. Resolve all remaining open comments with "internal review closed"
      3. Rename the file with [ARCHIVED YYYY-MM-DD] prefix

    Returns a dict summarizing what was done. Each step has its own
    success/failure flag so callers can see partial-completion status.

    Args:
      gdoc_url: the gdoc to archive
      freeze_date: YYYY-MM-DD
      confluence_link: appended to banner if provided
      original_title: if provided, used as the basis for the [ARCHIVED ...]
                       prefix. If None, attempts to read document.title and
                       strip the trailing " - Google Docs" suffix.
    """
    cf = f"\n\nSee Confluence page: {confluence_link}" if confluence_link else ""
    banner = (
        f"⚠️ This document moved to formal review on {freeze_date}. "
        f"Internal review has ended — comments here will not be reviewed further.{cf}\n\n"
        f"---\n\n"
    )

    result: dict = {
        "banner_prepended": False,
        "comments_closed": 0,
        "renamed": False,
        "errors": [],
    }

    # 1. Prepend banner
    try:
        current = read_body_text(gdoc_url).text
        paste_markdown_into_doc(gdoc_url, banner + current, replace_body=True)
        result["banner_prepended"] = True
    except Exception as exc:  # noqa: BLE001
        result["errors"].append(f"banner prepend: {exc}")

    # 2. Close all remaining open comments
    try:
        result["comments_closed"] = close_all_open_comments(gdoc_url, reply_text="Internal review closed; see Confluence.")
    except Exception as exc:  # noqa: BLE001
        result["errors"].append(f"close comments: {exc}")

    # 3. Rename title with [ARCHIVED YYYY-MM-DD] prefix
    try:
        wc = _wc()
        chrome = wc["connect_to_chrome"]()
        tab = chrome.find_tab(lambda t: gdoc_url in t.url)
        if tab is not None:
            with chrome.with_page(tab) as page:
                page_title = page.eval("document.title") or ""
            if original_title is None:
                # Strip trailing " - Google Docs" if present
                base = page_title.replace(" - Google Docs", "").strip()
                original_title = base or "document"
        new_title = f"[ARCHIVED {freeze_date}] {original_title}"
        result["renamed"] = rename_gdoc_title(gdoc_url, new_title)
        result["new_title"] = new_title
    except Exception as exc:  # noqa: BLE001
        result["errors"].append(f"rename: {exc}")

    return result
