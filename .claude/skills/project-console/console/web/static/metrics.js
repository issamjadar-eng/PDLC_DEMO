/* metrics.js — render the team usage dashboard from window.USAGE
 * (tools/usage-metrics/usage.json, schema usage-metrics/team/v1, anonymized).
 * Generic consumer of the usage-metrics skill; no names, no project specifics. */
(function () {
  "use strict";
  var U = window.USAGE || {};
  var DATA = U.months || {};
  var DAILY_COST = U.daily_cost || {};
  var RATE = U.rate_card || {};
  var TOK = ["input", "cache_read", "cache_creation", "output"];
  var fmt = function (n) { return (n || 0).toLocaleString(); };
  var usd = function (n) { return "$" + (n || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };
  // Token quantities normalized to MILLIONS of tokens (MTok) to match $/MTok rates.
  var tokM = function (n) { return ((n || 0) / 1e6).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + "M"; };
  var $ = function (id) { return document.getElementById(id); };
  function months() { return Object.keys(DATA).sort(); }

  function rowsFor(sel) {
    var acc = {}, ms = sel === "all" ? months() : [sel];
    ms.forEach(function (m) {
      Object.keys(DATA[m] || {}).forEach(function (lbl) {
        var rec = DATA[m][lbl];
        if (!acc[lbl]) acc[lbl] = { name: rec.name || lbl, input: 0, cache_read: 0, cache_creation: 0, output: 0, messages: 0, cost: 0, sessions: 0 };
        acc[lbl].sessions += rec.sessions || 0;
        acc[lbl].messages += (rec.totals && rec.totals.messages) || 0;
        acc[lbl].cost += rec.cost || 0;
        TOK.forEach(function (t) { acc[lbl][t] += (rec.totals && rec.totals[t]) || 0; });
      });
    });
    var rows = Object.keys(acc).map(function (k) { return acc[k]; });
    rows.forEach(function (r) { r.total_in = r.input + r.cache_read + r.cache_creation; });
    rows.sort(function (a, b) { return b.total_in - a.total_in; });
    return rows;
  }

  function render() {
    var sel = $("um-month").value;
    var rows = rowsFor(sel);
    var tot = { sessions: 0, input: 0, output: 0, cache_read: 0, cache_creation: 0, messages: 0, total_in: 0, cost: 0 };
    rows.forEach(function (r) { Object.keys(tot).forEach(function (k) { tot[k] += r[k] || 0; }); });

    // cards
    $("um-cards").innerHTML = [
      ["Members", fmt(rows.length)], ["Sessions", fmt(tot.sessions)],
      ["Total input", tokM(tot.total_in)], ["Output", tokM(tot.output)],
      ["Cache read", tokM(tot.cache_read)], ["Messages", fmt(tot.messages)],
      ["Est. cost", usd(tot.cost), "um-cost"]
    ].map(function (c) {
      return '<div class="um-card"><div class="k">' + c[0] + '</div><div class="v um-mono ' + (c[2] || "") + '">' + c[1] + "</div></div>";
    }).join("");

    // daily stacked composition
    var daily = {}, ms = sel === "all" ? months() : [sel];
    ms.forEach(function (m) {
      Object.keys(DATA[m] || {}).forEach(function (lbl) {
        var bd = DATA[m][lbl].by_day || {};
        Object.keys(bd).forEach(function (day) {
          if (!daily[day]) daily[day] = { input: 0, cache_read: 0, cache_creation: 0, output: 0 };
          TOK.forEach(function (t) { daily[day][t] += bd[day][t] || 0; });
        });
      });
    });
    var days = Object.keys(daily).sort();
    var dmax = Math.max.apply(null, [1].concat(days.map(function (d) {
      var v = daily[d]; return v.input + v.cache_read + v.cache_creation + v.output;
    })));
    var H = function (v) { return (v / dmax * 100).toFixed(2); };
    $("um-daily").innerHTML = days.map(function (d) {
      var v = daily[d];
      return '<div class="um-col" title="' + d + ': total input ' + tokM(v.input + v.cache_read + v.cache_creation) + ', output ' + tokM(v.output) + '">' +
        '<div class="um-b-out" style="height:' + H(v.output) + '%"></div>' +
        '<div class="um-b-cw" style="height:' + H(v.cache_creation) + '%"></div>' +
        '<div class="um-b-cr" style="height:' + H(v.cache_read) + '%"></div>' +
        '<div class="um-b-in" style="height:' + H(v.input) + '%"></div>' +
        '<div class="um-lbl">' + d.slice(5) + "</div></div>";
    }).join("") || '<div class="um-empty">No daily data.</div>';

    // by-member stacked composition (anonymized)
    var mmax = Math.max.apply(null, [1].concat(rows.map(function (r) { return r.total_in + r.output; })));
    var W = function (v) { return (v / mmax * 100).toFixed(2); };
    $("um-bymember").innerHTML = rows.map(function (r) {
      return '<div class="um-barrow" title="' + r.name + ' — total input ' + tokM(r.total_in) + ', output ' + tokM(r.output) + ', est. cost ' + usd(r.cost) + '">' +
        '<div class="lbl">' + r.name + "</div>" +
        '<div class="um-track">' +
        '<div class="um-seg-in" style="width:' + W(r.input) + '%"></div>' +
        '<div class="um-seg-cr" style="width:' + W(r.cache_read) + '%"></div>' +
        '<div class="um-seg-cw" style="width:' + W(r.cache_creation) + '%"></div>' +
        '<div class="um-seg-out" style="width:' + W(r.output) + '%"></div></div>' +
        '<div class="um-barval um-mono">' + tokM(r.total_in) + ' in · <span class="um-cost">' + usd(r.cost) + "</span></div></div>";
    }).join("") || '<div class="um-empty">No data.</div>';

    // by-model
    var bm = {};
    ms.forEach(function (m) {
      Object.keys(DATA[m] || {}).forEach(function (lbl) {
        var bym = DATA[m][lbl].by_model || {};
        Object.keys(bym).forEach(function (mod) {
          var s = bym[mod];
          if (!bm[mod]) bm[mod] = { model: mod, input: 0, cache_read: 0, cache_creation: 0, output: 0, messages: 0, cost: 0 };
          TOK.forEach(function (t) { bm[mod][t] += s[t] || 0; });
          bm[mod].messages += s.messages || 0;
          bm[mod].cost += s.cost || 0;
        });
      });
    });
    var mrows = Object.keys(bm).map(function (k) { return bm[k]; }).sort(function (a, b) { return b.cost - a.cost; });
    document.querySelector("#um-bymodel tbody").innerHTML = mrows.map(function (r) {
      var ti = r.input + r.cache_read + r.cache_creation;
      return "<tr><td><code>" + r.model + "</code></td><td class='um-mono'>" + tokM(ti) +
        "</td><td class='um-mono'>" + tokM(r.output) + "</td><td class='um-mono'>" + fmt(r.messages) +
        "</td><td class='um-mono um-cost'>" + usd(r.cost) + "</td></tr>";
    }).join("") || '<tr><td colspan="5" class="um-empty">No data.</td></tr>';
  }

  function renderProjection() {
    var ents = Object.keys(DAILY_COST).sort().map(function (d) { return [d, DAILY_COST[d]]; });
    var pc = $("um-projcards");
    if (!ents.length) { pc.innerHTML = '<div class="um-empty">No cost data to project.</div>'; return; }
    var first = ents[0][0], last = ents[ents.length - 1][0];
    var total = ents.reduce(function (a, e) { return a + e[1]; }, 0);
    var spanDays = Math.max(1, Math.round((new Date(last) - new Date(first)) / 86400000) + 1);
    var perDayAll = total / spanDays;
    var cut = new Date(last); cut.setDate(cut.getDate() - 6);
    var perDay7 = ents.filter(function (e) { return new Date(e[0]) >= cut; }).reduce(function (a, e) { return a + e[1]; }, 0) / 7;
    pc.innerHTML = [
      ["Projected 30-day", usd(perDay7 * 30), "um-cost"],
      ["Recent pace ($/day, 7d)", usd(perDay7)],
      ["Avg pace ($/day, all)", usd(perDayAll)],
      ["Proj. 30-day (avg pace)", usd(perDayAll * 30)],
      ["Data window", spanDays + " days"]
    ].map(function (c) {
      return '<div class="um-card"><div class="k">' + c[0] + '</div><div class="v um-mono ' + (c[2] || "") + '">' + c[1] + "</div></div>";
    }).join("");
    var cmax = Math.max.apply(null, [0.01, perDay7].concat(ents.map(function (e) { return e[1]; })));
    var html = ents.map(function (e) {
      return '<div class="um-col" title="' + e[0] + ": " + usd(e[1]) + ' actual"><div class="um-b-cost" style="height:' +
        (e[1] / cmax * 100).toFixed(1) + '%"></div><div class="um-lbl">' + e[0].slice(5) + "</div></div>";
    }).join("");
    for (var i = 1; i <= 30; i++) {
      var dt = new Date(last); dt.setDate(dt.getDate() + i);
      var ds = dt.toISOString().slice(0, 10);
      html += '<div class="um-col" title="' + ds + " (projected): " + usd(perDay7) + '"><div class="um-b-proj" style="height:' +
        (perDay7 / cmax * 100).toFixed(1) + '%"></div><div class="um-lbl">' + (i % 5 === 0 ? ds.slice(5) : "") + "</div></div>";
    }
    $("um-costts").innerHTML = html;
    $("um-projnote").textContent = "Projection = recent 7-day run-rate (" + usd(perDay7) +
      "/day) × 30. Linear; assumes usage continues at the same pace. Solid = actual, faded = projected. " +
      "Based on " + spanDays + " days (" + first + " to " + last + "). Indicative API-equivalent cost, not subscription billing.";
  }

  function renderRateCard() {
    var models = RATE.models || {}, fams = RATE.families || {};
    var keys = Object.keys(models).length ? models : fams;
    var m2 = function (n) { return "$" + (n == null ? "—" : Number(n).toFixed(2)); };
    document.querySelector("#um-rate tbody").innerHTML = Object.keys(keys).map(function (k) {
      var r = keys[k];
      return "<tr><td><code>" + k + "</code></td><td class='um-mono'>" + m2(r.input) + "</td><td class='um-mono'>" +
        m2(r.cache_write_1h) + "</td><td class='um-mono'>" +
        m2(r.cache_read) + "</td><td class='um-mono'>" + m2(r.output) + "</td></tr>";
    }).join("") || '<tr><td colspan="6" class="um-empty">No rate card.</td></tr>';
    $("um-ratesrc").textContent = "Rates in $/MTok. Source: " + (RATE._source || "pricing.json") +
      " (retrieved " + (RATE._retrieved || "?") + "). \"Write\" = 1-hour cache-write rate (what Claude Code uses); " +
      "cost prices each write at its actual 5m/1h rate. Edit tools/usage-metrics/pricing.json to update.";
    if ($("um-costnote")) $("um-costnote").textContent = U.cost_note || "";
  }

  function init() {
    var sel = $("um-month");
    if (!sel) return;
    sel.innerHTML = '<option value="all">All months</option>' +
      months().map(function (m) { return '<option value="' + m + '">' + m + "</option>"; }).join("");
    sel.value = "all";
    sel.addEventListener("change", render);
    render();
    renderProjection();
    renderRateCard();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
