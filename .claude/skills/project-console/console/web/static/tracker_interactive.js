/* B4 Tracker Status Update — interactive overlay JS. Injected by the
   /workflows/tracker/embed route into the tracker dashboard iframe. The
   parent page hosts the sidebar pending-changes panel; iframe edits
   notify the parent via postMessage. */

(function () {
  'use strict';

  // 7-state lifecycle vocabulary (locked 2026-05-03). Must match
  // tracker_writer.VALID_STATUSES + render.py VALID_STATUSES.
  const STATUSES = [
    'Approved', 'In Review', 'Drafted', 'Drafting',
    'Needs Revision', 'Not Started', 'N/A',
  ];

  // Lower index = "more complete". Used to detect downgrades and surface
  // the rationale hint per D2.
  const COMPLETENESS_RANK = {
    'Approved': 0,
    'In Review': 1,
    'Drafted': 2,
    'Needs Revision': 3,
    'Drafting': 4,
    'Not Started': 5,
    'N/A': 0,          // not-applicable; downgrade hint not relevant
  };

  function isDowngrade(oldStatus, newStatus) {
    const o = COMPLETENESS_RANK[oldStatus];
    const n = COMPLETENESS_RANK[newStatus];
    return typeof o === 'number' && typeof n === 'number' && n > o;
  }

  function notifyParent(type, payload) {
    try {
      window.parent.postMessage({ tracker: { type, payload } }, '*');
    } catch (e) { /* parent may not be listening; safe ignore */ }
  }

  function showToast(message, kind) {
    const t = document.createElement('div');
    t.className = 'tracker-toast' + (kind ? ' ' + kind : '');
    t.textContent = message;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 4500);
  }

  function closeAnyPopover() {
    document.querySelectorAll('.status-edit-popover').forEach(p => p.remove());
  }

  function openPopover(badge) {
    closeAnyPopover();
    const rowId = badge.getAttribute('data-row-id');
    const oldStatus = badge.getAttribute('data-status') || badge.textContent.trim();
    const rect = badge.getBoundingClientRect();
    const pop = document.createElement('div');
    pop.className = 'status-edit-popover';
    pop.style.left = (window.scrollX + rect.left) + 'px';
    pop.style.top = (window.scrollY + rect.bottom + 4) + 'px';
    pop.innerHTML =
      '<label>Row</label>' +
      '<div style="font-family:monospace;color:#94a3b8;margin-bottom:6px;">' + rowId + '</div>' +
      '<label>New Status</label>' +
      '<select class="new-status">' +
      STATUSES.map(s =>
        '<option value="' + s + '"' + (s === oldStatus ? ' selected' : '') + '>' + s + '</option>'
      ).join('') +
      '</select>' +
      '<div class="downgrade-hint" hidden></div>' +
      '<label>Rationale (optional)</label>' +
      '<textarea class="rationale" rows="2" placeholder="Why is this changing?"></textarea>' +
      '<div class="actions">' +
      '<button class="cancel">Cancel</button>' +
      '<button class="primary apply">Apply</button>' +
      '</div>';
    document.body.appendChild(pop);

    const sel = pop.querySelector('.new-status');
    const hint = pop.querySelector('.downgrade-hint');
    const updateHint = () => {
      const newS = sel.value;
      if (isDowngrade(oldStatus, newS)) {
        hint.hidden = false;
        hint.textContent = 'Downgrading status — consider noting why in the rationale.';
      } else {
        hint.hidden = true;
        hint.textContent = '';
      }
    };
    sel.addEventListener('change', updateHint);
    updateHint();

    pop.querySelector('.cancel').addEventListener('click', closeAnyPopover);
    pop.querySelector('.apply').addEventListener('click', async () => {
      const newStatus = sel.value;
      const rationale = pop.querySelector('.rationale').value.trim() || null;
      if (newStatus === oldStatus) { closeAnyPopover(); return; }
      pop.querySelector('.apply').disabled = true;
      try {
        const r = await fetch('/workflows/tracker/status/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ row_id: rowId, new_status: newStatus, rationale }),
        });
        if (!r.ok) {
          const detail = await r.text();
          showToast('Apply failed: ' + detail.slice(0, 200), 'error');
          pop.querySelector('.apply').disabled = false;
          return;
        }
        // Optimistically update the badge text + class + data
        badge.textContent = newStatus;
        badge.setAttribute('data-status', newStatus);
        badge.classList.add('pending');
        // Reset class list to base + new slug
        badge.className = 'status-badge ' + slugifyStatus(newStatus) + ' pending';
        showToast('Applied: ' + rowId + ' → ' + newStatus, 'success');
        closeAnyPopover();
        notifyParent('apply', { row_id: rowId, old_status: oldStatus, new_status: newStatus, rationale });
      } catch (e) {
        showToast('Network error: ' + e.message, 'error');
        pop.querySelector('.apply').disabled = false;
      }
    });
  }

  function slugifyStatus(s) {
    return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  }

  function wireBadges() {
    document.querySelectorAll('.status-badge[data-row-id]').forEach(badge => {
      if (badge.dataset.wired) return;
      badge.dataset.wired = '1';
      badge.addEventListener('click', (e) => {
        e.stopPropagation();
        openPopover(badge);
      });
    });
  }

  // Highlight rows that are already pending (badge state differs from md
  // baseline). On first load there's no diff; the parent panel will tell
  // us via postMessage which row IDs are pending.
  window.addEventListener('message', (e) => {
    if (!e.data || !e.data.tracker) return;
    const { type, payload } = e.data.tracker;
    if (type === 'mark-pending' && Array.isArray(payload.row_ids)) {
      payload.row_ids.forEach(rid => {
        const b = document.querySelector('.status-badge[data-row-id="' + cssEscape(rid) + '"]');
        if (b) b.classList.add('pending');
      });
    }
  });

  function cssEscape(s) {
    return (window.CSS && CSS.escape) ? CSS.escape(s) : s.replace(/"/g, '\\"');
  }

  // Close popover on outside click / escape
  document.addEventListener('click', (e) => {
    if (e.target.closest && e.target.closest('.status-edit-popover')) return;
    if (e.target.classList && e.target.classList.contains('status-badge')) return;
    closeAnyPopover();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeAnyPopover();
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wireBadges);
  } else {
    wireBadges();
  }
  // Wire any badges added dynamically.
  const obs = new MutationObserver(wireBadges);
  obs.observe(document.documentElement, { childList: true, subtree: true });

  // Notify parent on load so it can poll session state.
  notifyParent('ready', {});
})();
