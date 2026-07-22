/* Interactive data tables for the Commercial section (data view + answer Data tab):
   sort (numeric-aware), per-column filters (select for low-cardinality, text otherwise),
   global search, clear, and pagination (50 rows/page) — large snapshots stay navigable.
   Initializes every .cm-dt-panel on the page. The console displays rows verbatim. */
(function () {
  var PAGE = 50;

  function initPanel(panel) {
    if (panel.dataset.dtInit) return;
    panel.dataset.dtInit = '1';
    var dataEl = panel.querySelector('.cm-dt-data');
    var table = panel.querySelector('.cm-dt');
    if (!dataEl || !table) return;
    var rows = JSON.parse(dataEl.textContent);
    var cols = Array.prototype.map.call(table.querySelectorAll('thead tr:first-child th'),
      function (th) { return th.getAttribute('data-col'); });
    var tbody = table.querySelector('tbody');
    var state = { sortCol: null, sortDir: 1, filters: {}, search: '', page: 0 };

    panel.querySelectorAll('.cm-dt-filters th').forEach(function (th) {
      var col = th.getAttribute('data-col');
      var uniq = {}; rows.forEach(function (r) { uniq[r[col] || ''] = 1; });
      var keys = Object.keys(uniq);
      var el;
      if (keys.length <= 14) {
        el = document.createElement('select');
        el.innerHTML = '<option value="">all</option>' + keys.sort().map(function (k) {
          return '<option>' + String(k).replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</option>';
        }).join('');
        el.addEventListener('change', function () { state.filters[col] = el.value; state.page = 0; render(); });
      } else {
        el = document.createElement('input');
        el.type = 'search'; el.placeholder = 'filter…';
        el.addEventListener('input', function () { state.filters[col] = el.value; state.page = 0; render(); });
      }
      el.className = 'cm-dt-filter';
      th.appendChild(el);
    });

    table.querySelectorAll('thead tr:first-child th').forEach(function (th) {
      th.addEventListener('click', function () {
        var col = th.getAttribute('data-col');
        state.sortDir = state.sortCol === col ? -state.sortDir : 1;
        state.sortCol = col;
        table.querySelectorAll('.cm-dt-arrow').forEach(function (a) { a.textContent = ''; });
        th.querySelector('.cm-dt-arrow').textContent = state.sortDir > 0 ? ' ▲' : ' ▼';
        render();
      });
    });

    var search = panel.querySelector('.cm-dt-search');
    search && search.addEventListener('input', function (e) { state.search = e.target.value; state.page = 0; render(); });
    var clear = panel.querySelector('.cm-dt-clear');
    clear && clear.addEventListener('click', function () {
      state.filters = {}; state.search = ''; state.sortCol = null; state.page = 0;
      if (search) search.value = '';
      panel.querySelectorAll('.cm-dt-filter').forEach(function (el) { el.value = ''; });
      table.querySelectorAll('.cm-dt-arrow').forEach(function (a) { a.textContent = ''; });
      render();
    });
    var prev = panel.querySelector('.cm-dt-prev'), next = panel.querySelector('.cm-dt-next');
    prev && prev.addEventListener('click', function () { if (state.page > 0) { state.page--; render(); } });
    next && next.addEventListener('click', function () { state.page++; render(); });

    function numeric(v) { var n = parseFloat(v); return (v !== '' && !isNaN(n) && /^-?[\d.,%]+$/.test(String(v).trim())) ? n : null; }

    function render() {
      var out = rows.filter(function (r) {
        for (var c in state.filters) {
          var f = state.filters[c]; if (!f) continue;
          var v = String(r[c] || '');
          var sel = panel.querySelector('.cm-dt-filters th[data-col="' + CSS.escape(c) + '"] select');
          if (sel) { if (v !== f) return false; }
          else if (v.toLowerCase().indexOf(f.toLowerCase()) < 0) return false;
        }
        if (state.search) {
          var s = state.search.toLowerCase();
          if (!cols.some(function (c) { return String(r[c] || '').toLowerCase().indexOf(s) >= 0; })) return false;
        }
        return true;
      });
      if (state.sortCol) {
        var c = state.sortCol, d = state.sortDir;
        out.sort(function (a, b) {
          var na = numeric(a[c]), nb = numeric(b[c]);
          if (na !== null && nb !== null) return (na - nb) * d;
          return String(a[c] || '').localeCompare(String(b[c] || '')) * d;
        });
      }
      var pages = Math.max(1, Math.ceil(out.length / PAGE));
      if (state.page >= pages) state.page = pages - 1;
      var slice = out.slice(state.page * PAGE, (state.page + 1) * PAGE);
      tbody.innerHTML = slice.map(function (r) {
        return '<tr>' + cols.map(function (c) {
          return '<td>' + String(r[c] === undefined ? '' : r[c]).replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</td>';
        }).join('') + '</tr>';
      }).join('');
      var count = panel.querySelector('.cm-dt-count');
      if (count) count.textContent = 'showing ' + slice.length + ' of ' + out.length + ' filtered (' + rows.length + ' total)';
      var pager = panel.querySelector('.cm-dt-page');
      if (pager) pager.textContent = 'page ' + (state.page + 1) + ' / ' + pages;
      if (prev) prev.disabled = state.page === 0;
      if (next) next.disabled = state.page >= pages - 1;
    }
    render();
  }

  function initAll() { document.querySelectorAll('.cm-dt-panel').forEach(initPanel); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initAll);
  else initAll();
  window.cmInitDataTables = initAll;
})();
