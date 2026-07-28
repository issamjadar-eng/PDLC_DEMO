#!/usr/bin/env node
/*
 * cdp_print.js — render an HTML file to PDF via Chrome DevTools Protocol.
 *
 * Why CDP instead of `chrome --print-to-pdf`: the CLI shortcut (a) truncates to
 * one page under --headless=new and (b) stamps a date/title/URL header+footer
 * that cannot be suppressed or customized. CDP Page.printToPDF gives correct
 * pagination plus full control of displayHeaderFooter / headerTemplate /
 * footerTemplate / margins. Uses node's built-in global WebSocket + fetch
 * (node >= 22) — no npm install.
 *
 * Usage:
 *   node cdp_print.js --html <file> --out <pdf> --chrome <bin>
 *       [--logo <png>] [--footer "<left text>"]
 *       [--mt 1.0] [--mb 0.85] [--ml 0.9] [--mr 0.9]
 */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

function arg(name, def) {
  const i = process.argv.indexOf(name);
  return i >= 0 && i + 1 < process.argv.length ? process.argv[i + 1] : def;
}
const HTML = arg('--html');
const OUT = arg('--out');
const CHROME = arg('--chrome');
const LOGO = arg('--logo', '');
const FOOTER_LEFT = arg('--footer', '');
const MT = parseFloat(arg('--mt', '1.0'));
const MB = parseFloat(arg('--mb', '0.85'));
const ML = parseFloat(arg('--ml', '0.9'));
const MR = parseFloat(arg('--mr', '0.9'));
if (!HTML || !OUT || !CHROME) {
  console.error('cdp_print: --html, --out and --chrome are required');
  process.exit(2);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Header/footer templates render in the page margin. They need explicit sizing;
// the special spans (pageNumber/totalPages) are filled by Chrome.
function headerTemplate() {
  if (!LOGO || !fs.existsSync(LOGO)) return '<div></div>';
  const b64 = fs.readFileSync(LOGO).toString('base64');
  const ext = path.extname(LOGO).slice(1).toLowerCase() || 'png';
  const mime = ext === 'svg' ? 'image/svg+xml' : `image/${ext}`;
  return `<div style="width:100%; padding:0 ${ML}in; box-sizing:border-box; -webkit-print-color-adjust:exact;">
    <img src="data:${mime};base64,${b64}" style="height:15px;">
  </div>`;
}
function footerTemplate() {
  const left = FOOTER_LEFT
    ? `<span>${FOOTER_LEFT.replace(/&/g, '&amp;').replace(/</g, '&lt;')}</span>`
    : '<span></span>';
  return `<div style="width:100%; padding:0 ${ML}in; box-sizing:border-box;
      font-size:8px; color:#8a8a8a; font-family: Helvetica, Arial, sans-serif;
      display:flex; justify-content:space-between; align-items:center;">
    ${left}
    <span class="pageNumber" style="font-variant-numeric:tabular-nums;"></span>
  </div>`;
}

async function cdpSend(ws, pending, method, params) {
  const id = pending.nextId++;
  return new Promise((resolve, reject) => {
    pending.map.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params: params || {} }));
  });
}

async function main() {
  const udd = fs.mkdtempSync(path.join(os.tmpdir(), 'pubdoc-chrome-'));
  const chrome = spawn(CHROME, [
    '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
    '--no-first-run', '--no-default-browser-check',
    `--user-data-dir=${udd}`, '--remote-debugging-port=0',
    `file://${path.resolve(HTML)}`,
  ], { stdio: ['ignore', 'ignore', 'pipe'] });

  // Chrome writes the chosen port to <udd>/DevToolsActivePort (line 1 = port).
  const portFile = path.join(udd, 'DevToolsActivePort');
  let port = null;
  for (let i = 0; i < 100; i++) {
    if (fs.existsSync(portFile)) {
      const t = fs.readFileSync(portFile, 'utf8').split('\n')[0].trim();
      if (t) { port = t; break; }
    }
    await sleep(100);
  }
  if (!port) { chrome.kill(); throw new Error('Chrome did not expose a debugging port'); }

  // Find the page target's WebSocket (connect page-level → no session needed).
  let wsUrl = null;
  for (let i = 0; i < 50; i++) {
    try {
      const targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
      const page = targets.find((t) => t.type === 'page' && t.webSocketDebuggerUrl);
      if (page) { wsUrl = page.webSocketDebuggerUrl; break; }
    } catch (_) { /* retry */ }
    await sleep(100);
  }
  if (!wsUrl) { chrome.kill(); throw new Error('No page target found'); }

  const ws = new WebSocket(wsUrl);
  const pending = { nextId: 1, map: new Map() };
  let loaded = false;
  ws.addEventListener('message', (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.map.has(msg.id)) {
      const { resolve, reject } = pending.map.get(msg.id);
      pending.map.delete(msg.id);
      msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
    } else if (msg.method === 'Page.loadEventFired') {
      loaded = true;
    }
  });
  await new Promise((res, rej) => {
    ws.addEventListener('open', res, { once: true });
    ws.addEventListener('error', rej, { once: true });
  });

  await cdpSend(ws, pending, 'Page.enable');
  // The file may already be loading; give it a moment for load + web fonts/layout.
  for (let i = 0; i < 30 && !loaded; i++) await sleep(100);
  await sleep(400); // settle fonts/reflow

  const result = await cdpSend(ws, pending, 'Page.printToPDF', {
    printBackground: true,
    preferCSSPageSize: false,
    paperWidth: 8.5,
    paperHeight: 11,
    marginTop: MT, marginBottom: MB, marginLeft: ML, marginRight: MR,
    displayHeaderFooter: true,
    headerTemplate: headerTemplate(),
    footerTemplate: footerTemplate(),
  });
  fs.writeFileSync(OUT, Buffer.from(result.data, 'base64'));

  ws.close();
  chrome.kill();
  try { fs.rmSync(udd, { recursive: true, force: true }); } catch (_) {}
  console.log(`cdp_print: wrote ${OUT}`);
}

main().catch((e) => { console.error('cdp_print error:', e.message); process.exit(1); });
