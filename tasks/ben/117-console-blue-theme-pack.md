# 117 — Console Blue Theme Pack

**ID**: 117
**Created**: 2026-08-10
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
   - **when you tick a Todo off (or add/restructure Todos), fill/refresh the matching `## Economics` entry in the same edit** — the by-hand person-hours that unit would have taken, ranged + persona-tagged, per the rubric (if `## Economics` is present / usage-metrics is installed). **Checking the box is the estimate trigger** — don't defer it to a later checkpoint.
2. **Phase-end batching is OK; drift-batching is not.** Planned phases (e.g., "finish Phase 2, then log the whole phase at once") are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask. By then a crash or context-trim has lost the state. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.
6. **Estimation provenance (if `## Economics` is present).** This doc's `## Economics` block is the by-hand person-hour estimate, built per the effort-estimation rubric at `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (owned by the `usage-metrics` skill). To **add or refresh** an estimate on resume — even without loading the task skill — read that rubric first for the anchors, personas, and JSON schema; the block also carries a `method_ref` naming it. Skip silently if `usage-metrics` isn't installed. Point to the rubric, never copy it into this doc.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

Give the project console a blue palette delivered **as a new theme pack**, with the existing `globallogic-dark` pack left untouched and still the configured default until an explicit switch is approved. User constraint: **nothing may break** — so the work is additive first, with a one-line reversible switch as the only adoption step.

Approved plan: `/Users/benxavier/.claude/plans/snappy-percolating-octopus.md`

### Why

The current look reads as generic "AI product". The cause is specific and verifiable, not a matter of taste: the base `dark` pack is **unmodified Tailwind slate** (`#0f172a` / `#1e293b` / `#334155` / `#475569`) and the project pack sets `primary` to **Tailwind purple-500** (`#a855f7`) with a **sky-400** accent (`#38bdf8`). Stock slate + purple-500 has been the default palette of most AI products since 2023 — viewers are recognising defaults. The risk to avoid is swapping to generic blues and landing on sky-on-navy, the other half of the same cliché.

### How theming works here (verified against the code, not assumed)

| Fact | Evidence |
|---|---|
| Theme resolves **per request** — editing a pack's `theme.yaml` takes effect on page reload, no restart | `console/app.py:115-122` |
| `console.yaml` is **process-cached** — *switching* packs needs a restart | `console/config.py:233` `@lru_cache(maxsize=1)` |
| Project packs beat skill packs; `extends:` is recursive with cycle detection | `console/themes.py:93-143` |
| Unknown keys ignored; missing pack degrades to `light`; missing parent degrades to child-only | `console/themes.py:34-80,146-168` |
| **Assets are NOT inherited** — `pack_dir` is the *child's* dir, so a pack without `logo.png` / `favicon.ico` / `footer.html.j2` silently loses its logo, favicon and footer | `themes.py:141`, `app.py:180-185`, `Theme.has_footer` |
| Fonts come from the shared static mount, not the pack — no copying needed | `console.css:1-6` → `/static/fonts/manrope-latin.woff2` |

### Scope correction — the hardcoded-colour problem is ~33 lines, not ~90

An initial count of ~90 hardcoded colours was too pessimistic. Categorised:

| Category | Count | Action |
|---|---|---|
| Semantic status colours (commercial/submission/gap-analysis `--c`: green=answered, amber=draft, red=stale, severity bands) | ~55 | **Leave alone** — they encode meaning, not brand, and are correctly theme-independent. Contrast-check only. |
| Duplicated dark palette in `tracker_interactive.css` (`#0f172a`/`#1e293b`/`#334155`/`#e2e8f0`/`#38bdf8`) | 13 | **Must tokenise** — this file follows *no* theme, so Tracker would stay slate while everything else moved |
| Light-theme leftovers + YAML syntax colours in `console.css` | ~20 | **Must tokenise** — already visibly wrong on dark today |

## Findings (pre-existing bugs, independent of the palette work)

**F1 — YAML files in the Documents tab are unreadable on the dark theme.** `.lang-yaml` is applied live by `console/web/static/explorer.js:572-576` for `.yml` / `.yaml` / `.json`. Its colours are dark-on-light values sitting on `.docs-text`'s `var(--gl-gray-lighter)` → `--body-bg` → `#0f172a`. Measured contrast:

| Token | Colour | Contrast on `#0f172a` | WCAG AA (4.5:1) |
|---|---|---|---|
| base text `.docs-text.lang-yaml` | `#1f2344` | **1.17:1** | FAIL — effectively invisible |
| `.yml-string` | `#0b6a3c` | 2.67:1 | FAIL |
| `.yml-number` | `#9c3e00` | 2.64:1 | FAIL |
| `.yml-bool` | `#b00057` | 2.54:1 | FAIL |
| `.yml-key` (`--gl-purple-dark`) | `#7a00df` | 2.46:1 | FAIL |
| `.yml-punct` | `#6b7280` | 3.69:1 | FAIL |
| `.yml-comment` | `#8a94b4` | 5.93:1 | ok |

Six of seven fail; the base text is at the visual-noise floor. Fixed in Phase 2.

**F2 — light-theme leftovers in `console.css` already wrong on dark.** Pale purple `#c9b8dc` (L1194), `#e0cdf5` (L1360), `#d8c4f0` (L1485) and a light-pink error panel `#fdecea` / `#7a1f1a` (L1947).

**F3 — the web font is served from the *active theme pack*, so a new pack must carry it.** The approved plan said fonts needed no copying, citing `console.css:1-6` → `/static/fonts/manrope-latin.woff2`. **That was wrong, and it would have broken the blue theme silently.** That URL returns **404** — there is no `fonts/` directory under the skill's static mount. `console.overrides.css:5-18` deliberately redeclares the `@font-face` pointing at `/theme/assets/fonts/manrope-latin.woff2`, which resolves through `pack_dir`. So Manrope loads *from whichever pack is active*. A pack without `fonts/manrope-latin.woff2` falls back to the system UI font — the console would have looked **more** generic after a change made to reduce genericness, and nothing would have errored. Caught by testing both URLs (`404` vs `200`) instead of trusting the CSS declaration. The new pack now carries all four assets and asset parity against `globallogic-dark` is asserted.

<!-- LESSONS LEARNED: console, theming, verification -->
**Lesson — "inherits X" is a claim about a specific mechanism; check which mechanism.** The theme system inherits **tokens** through `extends:` but not **assets**, because `console/themes.py:141` returns the child's `pack_dir` and `/theme/assets/*` is served from it. I had that right in the plan for logo/favicon/footer and still got fonts wrong — because I reasoned about the font from a CSS `src:` URL rather than from a request. The declaration said `/static/fonts/…`; the reality was a 404 plus an override file redirecting to the pack. **How to apply:** when an asset's availability is load-bearing, `curl` the URL. A CSS/HTML reference proves what the author intended, not what the server returns — and a font that fails to load produces no error anywhere, just a silent fallback.
<!-- /LESSONS -->

**F5 — `tracker_interactive.css` runs in a different CSS-variable namespace than the plan assumed.** The plan said to map its hardcoded slate values onto console tokens (`--body-bg`, `--brand-primary`, …). **That would have broken it silently.** The overlay is injected by `/workflows/tracker/embed` into the standalone tracker dashboard, which `workflow_tracker.html` loads in an **iframe** — and an iframe inherits no custom properties from its parent, so every console token would have been undefined and resolved to nothing (transparent popover, no border, invisible text). The variables that exist in that document are the dashboard's own, emitted by `.claude/skills/tracker/scripts/render.py` `_CSS_BASE_INNER`: `--bg --surface --surface2 --border --text --text-muted --brand --accent --green --yellow --red …`. Mapped to those instead, and asserted: all 9 tokens used by the overlay resolve against the generated dashboard document. Also found 4 sky-400 values in `rgba(56, 189, 248, …)` form that the hex-only count had missed.

**F6 — the tracker dashboard will NOT follow a console theme change (scope finding, needs a decision).** `render.py` already reads the active theme pack (`_read_theme_yaml`, resolves `extends:`) but lifts exactly **two** tokens — `primary` → `--brand` and `font_body` → `--font` (`render.py:1109-1113`). Everything else in the dashboard's `:root` is hardcoded Tailwind slate (`--bg:#0f172a --surface:#1e293b --surface2:#334155 --border:#475569 --text:#e2e8f0 --accent:#38bdf8`). Consequences: (a) switching the console to blue leaves the Tracker dashboard slate-and-sky, so that one tab visibly disagrees; (b) `--brand` *would* update, but only after the dashboard is **re-rendered** — it is a generated, committed artifact at `docs/project/submissions/submission-tracker.html`. Fixing it means extending `gen_theme_css()` in the **`tracker` skill** to lift the full palette, then regenerating. That is a different skill and a committed-artifact regeneration, so it is **not** being done unilaterally — raised for Ben's decision at the Phase 3 gate.

**F7 — `_read_theme_yaml()` could not parse any key containing a digit.** Its regex was `^([a-z_]+):`, so **`surface_2` never matched** and was silently dropped. Symptom once the full palette was being lifted: the dashboard's `--surface` followed the theme while `--surface2` stayed Tailwind slate — a half-themed dashboard that looks like a rendering bug rather than a parsing one. Fixed to `^([a-z0-9_]+):`. Found by asserting the lifted token count (10/11) rather than eyeballing the render.

**F8 — `--eng` (Engineering Prereqs violet `#a78bfa`) is now the only unthemed element on the dashboard, and that is a judgement call.** It was left alone deliberately: it is a *category* marker distinguishing engineering prereqs from the regulatory phases, and the phase badges already cycle through `--accent / --accent2 / --green / --orange / --text-muted`, so any in-palette replacement risks colliding with a phase colour. Against blue + brass it now reads as a leftover rather than a category. **Open for Ben** — leave as a deliberate category hue, or pick a distinct in-palette value.

**F9 — the theme-yaml comment stripper truncated any comma-separated hex list.** `_read_theme_yaml` stripped inline comments with `re.sub(r'\s+#.*$', …)`. A list like `"#5fa8dd, #4fb3a6, #9fb765, …"` has whitespace-preceded `#` all the way along, so it was cut to `#5fa8dd,` — the value still parsed, just short, and the ramp silently degraded to one colour. The original comment even warned about the inverse case (don't eat a *leading* hex) without covering this one. Fixed with a negative lookahead that only treats `#` as a comment when it does **not** begin a 3/4/6/8-digit hex token, with regression cases including a comment whose first word is itself hex-ish (`# added for contrast`).

**F10 — a CSS class may not start with a digit, and one milestone had never been coloured.** `slug('510k+PCCP')` → `510k-pccp`, emitted as both a class and a selector. A CSS identifier cannot begin with a digit, so browsers **discard the whole rule** — no error, no warning. Verified live in the iframe before fixing: the 510k+PCCP badge computed to inherited `--text` on a transparent background while `lmr1` and `qsub` both resolved their cycle colours. It read as a deliberate "no colour for this one" rather than a dropped rule. Fixed with a `css_token(prefix, value)` helper (`ph-`, `sc-`) that makes digit-leading classes unrepresentable for any discovered value; safe because filtering keys off `data-scope` / `data-phase`, not these classes.

**F11 — the bundled `light` / `dark` packs carry no assets, and the selector made that reachable in one click.** They are palettes only: no `logo.png`, no `favicon.ico`, no `fonts/`. Since `/theme/assets/*` serves from the *active* pack (see F3), selecting one returned 404 for all three — the logo hidden by its `onerror`, and **Manrope silently gone**, because a failed `@font-face` just falls back to the system stack with no error. Fixed by making asset lookup a fallback chain — selected pack, then the project default — on the principle that **colours are per-pack but identity assets belong to the project**. Traversal is still refused outright rather than falling through. Verified: logo / favicon / font all 200 under every one of the five packs.

**F12 — `--card-bg` and `--fg` are referenced in the metrics view but defined nowhere, so light mode was unreadable.** Reported by Ben while testing a light pack. `metrics_view.html` styled its cards with `var(--card-bg,#181b22)` and `var(--fg,#e6e9ef)` — neither token exists anywhere in the console (the real names are `--surface` and `--body-text`), so the **dark fallback always won**. On a light pack that produced dark cards on a light page, and — because the card text inherits `--body-text`, which *does* follow the theme — **dark text on a dark card**: the headline figures were effectively invisible. A CSS var with a plausible-looking fallback fails silently and looks deliberate.

Swept the whole console for the bug class rather than fixing the one file: **36 referenced-but-undefined tokens**, of which most were legitimately component-scoped (`--dp-*`, `--ga-*`, `--c`) or belonged to the dashboard iframe. The genuinely broken ones:

| Token | Where | Real name |
|---|---|---|
| `--card-bg`, `--fg` | `metrics_view.html` | `--surface`, `--body-text` |
| `--surface2`, `--text-muted` | `dashboard_view.html`, `workflow_tracker_draft.html` | `--surface-2`, `--body-text-muted` — these are **console** documents using the **dashboard's** token names, the mirror image of F5 |
| `--font-mono` | 5 files | undefined everywhere; now a real `:root` token |

Post-fix sweep: **0 undefined token references** across every template and stylesheet.

**F13 — a light pack that omits `surface` renders a dark dashboard.** `light` and `globallogic` declared only `body_bg` / `text` / `border`, relying on console.css `:root` defaults for the surfaces. That works *in the console* — and breaks in any consumer with its own defaults, because the tracker dashboard mirrors the pack into a `:root` whose baked surface values are **dark slate**. Result: light page, dark cards. Both light packs now declare `surface` / `surface_2` / `surface_muted` / `code_bg` / `code_text` explicitly — a no-op for the console, a fix for every external consumer. **A pack that wants to own a surface has to say so.**

**F14 — the footer rendered "© now", and every pack had a year problem.** Spotted by Ben under the bundled light pack. The template contained `{{ "now"|e }}` — a **quoted string literal** run through the escape filter, so it rendered the word `now`. The cause is upstream of the typo: `_render_theme_footer()` passed only `theme` into the template context, Jinja has no `now` global, and the function's `except Exception: return ""` swallows template errors into an empty footer — so an undefined variable would have silently deleted the footer entirely, and a string literal was the only thing that visibly "worked". Surveying all five packs found the same gap three more ways:

| Pack | Was | Now |
|---|---|---|
| `light` (bundled) | `&copy; {{ "now"\|e }} …` → literal "now" | `&copy; {{ year }} …` |
| `dark` (bundled) | `&copy; Project Console …` — **no year at all** | `&copy; {{ year }} …` |
| `globallogic`, `-dark`, `-blue` | `&copy; 2026 …` hardcoded — correct today, wrong every January | `&copy; {{ year }} …` |

Fixed by giving the footer context a real `year` (`datetime.now().year`) — the thing the templates needed and could not reach — and pointing all five at it. Verified per pack: default/`globallogic*` → "© 2026 Copyright GlobalLogic Inc.", `light`/`dark` → "© 2026 Project Console — generic … theme."; zero `&copy; now` occurrences.

**Resolved by Ben — option (c): delete the bundled footers.** Deletion alone would have removed the footer rather than inherited one (`_render_theme_footer` returned `""` for a pack without a template, and `_base.html` omits the element when empty), so it needed the fallback too. Both landed:

- `.claude/skills/project-console/themes/{light,dark}/footer.html.j2` **deleted** — those packs now ship only `theme.yaml`.
- `_render_theme_footer(theme, default_theme)` walks the same chain as `/theme/assets`: active pack, then project default. Each template renders with **its own** pack's theme, so a fallback footer carries the project's tagline rather than mixing two packs.

Verified across all six selections: every one now shows *"© 2026 Copyright GlobalLogic Inc."* with the GlobalLogic tagline. Degenerate case checked directly — no footer in either pack returns `''`, so `_base.html` omits the element rather than rendering an empty bar. 36/36 (6 routes × 6 packs) 200.

The general rule is now written into project-console SKILL.md: **`theme.yaml` carries the palette; `logo.png` / `favicon.ico` / `fonts/` / `footer.html.j2` carry project identity, and identity falls back to the project default pack.** The bundled packs ship neither assets nor a footer by design.

## Per-browser theme selection (Phase 3d)

**Cookie, not localStorage — deliberately.** Both are browser-local and neither is committed, which is what was asked. The cookie is chosen because the **server** must see the choice: the active pack decides which `logo.png`, `favicon.ico`, web font and `footer.html.j2` `/theme/assets/*` serves, not just the CSS variables. A client-only mechanism would swap the colours and leave the branding on the project default — a pack rendered half-applied, with no error.

| | |
|---|---|
| storage | `pc_theme` cookie, `path=/`, `SameSite=Lax`, 1 year. No `Secure` flag — the console is plain http on localhost, where a Secure cookie is silently dropped |
| unset | falls back to `console.yaml` `theme:` — the project default, unchanged |
| validation | `themes.safe_theme_name()` matches the value against installed packs before it can reach a filesystem path. `../../etc`, `../dark`, unknown names → `None` → default. **Never trust a cookie that feeds a path** |
| write path | none. The selector never touches `console.yaml` or `project.yml`; confirmed by diffing config after switching |

New API in `console/themes.py`: `list_packs(cfg)` (discovers project + builtin packs, project wins on name collision, returns resolved tokens for the swatch) and `resolve(cfg, name=None)` (name overrides the default). Setup gains an `appearance` block and an **Appearance** section whose swatch is a miniature of the console — topnav strip, panel, numeral, brand/accent/category chips — rather than a row of disconnected colour squares, because a palette is judged by how the colours sit together.

**Known limitation:** the tracker dashboard is a *generated artifact*, so its palette is baked at render time from whatever pack was active then. A per-browser selection does not re-render it — the dashboard keeps the project default's colours until `/tracker render` runs again. Correct behaviour (a committed artifact cannot vary per viewer), but worth knowing.

## Category palette (Phase 3c)

The pack now ships an ordered ramp; the **consumer** assigns meaning. That split is what makes it a general theme capability rather than a tracker setting.

| | value |
|---|---|
| ramp (globallogic-blue) | `#5fa8dd` azure → `#4fb3a6` teal → `#9fb765` sage → `#d9a441` brass → `#d98757` coral |
| reserved (non-sequential) | `#9a8fd4` lavender |

Milestones are **ordinal** (QSub → 510k+PCCP → LMR1 → LMR2), so a sequential cool→warm ramp lets progression be read from colour alone — something an arbitrary categorical set cannot do. The reserved entry is the one lavender in a blue-to-warm ramp, so "outside the sequence" is visible at a glance; the tracker gives it to Engineering Prereqs. Each milestone's summary card, phase badge and progress-row label share one colour; progress-bar **segments** stay status-coloured.

Also removed `PHASE_COLOR_CYCLE`, which had mixed `--accent`, `--green` and `--orange` — borrowing two **status** colours for a category dimension, so a milestone badge could read as "done" at a glance.

## Palette design (Phase 1)

Direction: move off **both** clichés — stock Tailwind slate, and the sky-on-navy that a naive "make it blue" lands on.

| | Tailwind slate/sky (current) | globallogic-blue |
|---|---|---|
| body | `#0f172a` h222 s47% l11% | `#0a1620` h207 s52% l8% |
| surface | `#1e293b` h217 s33% l17% | `#172c3c` h206 s45% l16% |
| surface-2 | `#334155` h215 s25% l27% | `#223c50` h206 s40% l22% |
| border | `#475569` h215 s19% l35% | `#2f4a5e` h206 s33% l28% |
| primary | `#38bdf8` h198 **s93%** | `#5fa8dd` h205 **s65%** |
| accent | `#818cf8` h234 (cool indigo) | `#d9a441` h39 (warm brass) |

The saturation drop on primary carries more perceptual difference than the hue shift; a hue-only move would still have read as sky. The single warm accent against an all-cool field is what stops the ramp reading as generated — it is used sparingly by design (info badges, citation links, folder glyphs).

**All 17 real usage pairs meet WCAG AA 4.5:1** (text/muted/primary/accent on each surface, code, footer, badge, warning banner); borders clear 1.5:1 on both body and surface. Several sit close to the floor — re-run the contrast check before changing any value.

## Todos

- [x] Phase 0 — baseline: 13 full-page screenshots on the current theme at `tasks/ben/_scratch/theme-baseline/` (gitignored, 9.1 MB); all 13 routes verified 200 first; F1 quantified by contrast arithmetic
- [x] Phase 1 — new pack `tools/project-console/themes/globallogic-blue/` (theme.yaml + copied logo/favicon/footer **+ fonts/**, see F3). **Zero existing files touched — verified.**
- [x] Phase 2 — tokenised `tracker_interactive.css` (13 hex + 4 rgba, into the **dashboard** namespace — see F5) and `console.css` (25 → 0 accidental); fixes F1 + F2. **Pixel-diff on the current theme: 0 of 11.0M px changed across home/setup/documents.**
- [x] Phase 3 — switched (`console.yaml` → `globallogic-blue`, backup at `tasks/ben/_scratch/console.yaml.before-blue`), restarted, verified. **Awaiting Ben's verdict.**
- [x] Phase 3b — **tracker dashboard fixed (F6 closed)**, per Ben. `tracker` skill `render.py`: `load_brand_theme()` now lifts the full chrome palette via a declarative `_THEME_TOKEN_MAP` (11 tokens) instead of 2; `_read_theme_yaml()` key regex fixed (F7); ~20 hardcoded brand literals in `_CSS_BASE_INNER` + both badge colour cycles converted to `color-mix` on their own tokens; `.help-mode-banner.purple` renamed `.alt`. Dashboard regenerated — data byte-identical, zero old brand literals.
- [x] Phase 3d — **Appearance section in Settings**: per-browser theme selector with a live swatch per pack. Selection stored in a `pc_theme` cookie (never in project config); unset = the `console.yaml` default. Untrusted name validated against installed packs before it reaches a path; asset lookup falls back to the default pack (F11).
- [ ] Phase 4 — adopt or revert; on adopt: SKILL.md theme docs + README changelog + VERSION (both skills), then push
- [x] Phase 3c — **`category_colors` capability added to the theme-pack contract** and applied to all milestones (closes F8). Sequential cool→warm ramp + reserved final entry; added to `dark`, `light` and `globallogic-blue` packs; consumed by the tracker for summary cards, phase badges and progress-row labels. Fixed F9 (parser truncated the hex list) and F10 (digit-leading CSS class silently dropped, so 510k+PCCP had never been coloured). on the dashboard
- [ ] Phase 5 — `/sync-skills push --merge` the CSS fixes upstream as a **separate** reviewable PR (per Ben: these are real bugs every project on the `dark` theme has)

## Open Questions

- Palette not yet chosen. Ben's answer: I propose one for review rather than working from supplied brand hexes. Direction agreed: a neutral ramp **off-axis from Tailwind slate** (blue-grey carrying some warmth), **one** restrained accent that is neither purple-500 nor sky-400, contrast and hairlines doing the work instead of glow/gradient. Manrope stays.
- **Brand question, unresolved and worth raising before Phase 4 adoption:** GlobalLogic's brand colour is purple (`#7a00df` in the light pack). If the console is brand-facing, moving to blue is a brand decision rather than a taste one.

## Resume

### In-flight artifacts

- **Uncommitted**: nothing yet — Phase 0 produced only gitignored screenshots.
- Console running on http://127.0.0.1:8765, theme `globallogic-dark` (unchanged).
- Baselines: `tasks/ben/_scratch/theme-baseline/00-home.png` … `12-documents.png` (gitignored; regenerate by re-running Phase 0 if lost).

### First action on resume

1. Phase 1 — create the pack. Remember to copy `logo.png`, `favicon.ico`, `footer.html.j2`; assets are **not** inherited through `extends:`.
2. Do **not** edit `tools/project-console/themes/globallogic-dark/` or `console.yaml` before the Phase 3 review gate.
3. Activation: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 117`

## Economics

_By-hand person-hour estimate, **filled at checkpoint** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated; an empty `todos` list is ignored by the aggregator._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": null,
    "todos": [
      {
        "todo": "Theming-contract investigation + plan (resolution order, extends, per-request vs cached, asset-inheritance gotcha, hardcoded-colour triage) + Phase 0 baseline",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 3, "max": 5},
        "confidence": "med",
        "basis": "reading a theme resolver, config cache and 5 CSS files closely enough to distinguish semantic status colours from brand leftovers, plus 13 baseline captures; the asset-inheritance trap is the kind of thing normally found by breaking it"
      }
    ]
  }
}
```

## Changelog

- 2026-08-11: **Phase 3g — bundled footers deleted; identity now falls back to the project pack (Ben chose option c).** Deleting alone would have left no footer at all, so the fallback shipped with it: `_render_theme_footer(theme, default_theme)` now walks active-pack → project-default, mirroring `/theme/assets`, with each template rendered under its own pack's theme so a fallback footer isn't a hybrid of two packs. `themes/{light,dark}/footer.html.j2` removed — those packs are now `theme.yaml` only. All six selections show the GlobalLogic copyright + tagline; the no-footer-anywhere case returns `''` so `_base.html` omits the element instead of drawing an empty bar; 36/36 (6 routes × 6 packs) 200. Documented the general rule in project-console SKILL.md: **`theme.yaml` is the palette; logo / favicon / fonts / footer are project identity and fall back to the default pack** — a personal palette choice is not a branding change.
- 2026-08-11: **Phase 3f — footer year fixed across all five packs (F14), reported by Ben.** The bundled light pack rendered "© now" because its template held `{{ "now"|e }}` — a quoted string through the escape filter. Root cause was upstream: `_render_theme_footer()` passed only `theme`, Jinja has no `now` global, and the function swallows template errors into an *empty* footer, so an undefined variable would have silently removed the footer and a string literal was the only visibly-working option. The survey found the same gap three more ways — the bundled dark pack had **no year at all**, and all three project packs **hardcoded 2026**, correct today and wrong every January. Fixed by adding a real `year` to the footer render context and pointing all five templates at it. Verified per pack; zero `&copy; now`; 30/30 (5 routes × 6 packs) 200. **Raised, not decided:** selecting a bundled pack replaces the GlobalLogic copyright with the pack's placeholder footer — the same half-applied-identity problem the asset fallback solved for the logo, but whether a personal theme may change a company copyright notice is a branding call for Ben.
- 2026-08-11: **Phase 3e — light mode fixed on Metrics and Dashboards (F12, F13), reported by Ben.** Root cause was not "these pages ignore the theme" but **references to tokens that do not exist**: `var(--card-bg,#181b22)` / `var(--fg,#e6e9ef)` in `metrics_view.html` (real names `--surface` / `--body-text`), so the dark fallback always won — and since the card *text* does follow the theme, light mode gave dark-on-dark figures. Swept the whole console instead of patching one file: 36 undefined references found, most legitimately component-scoped; the real ones were those two plus `--surface2` / `--text-muted` in `dashboard_view.html` and `workflow_tracker_draft.html` (console documents using the **dashboard's** token names — the mirror image of F5) and `--font-mono`, referenced in five files and defined in none. **Post-fix: 0 undefined token references console-wide.** Metrics also had dark-only literals — `#11141a` wells → `--code-bg`, and the Input/Cache-read/Cache-write/Output series → the **category ramp**, so the series is contrast-checked per pack rather than carrying dark-tuned values; `themes.py` now emits `--cat-1…N` / `--cat-alt` for console surfaces and console.css carries light defaults. **F13**: `light` and `globallogic` declared no `surface`, relying on console.css defaults — fine in the console, but the tracker dashboard mirrors packs into a `:root` with **dark** baked surfaces, so a light pack rendered dark cards; both packs now declare their surfaces explicitly. Also threaded the per-browser selection into the **inline** dashboard render (`render(…, theme_name)` / `render_embed_fragment(…, theme_name)`), so the Dashboards tab follows a personal theme — the committed standalone `.html` still bakes the project default, which is correct for an artifact that cannot vary per viewer. Verified: **90/90** (15 routes × 6 packs) 200; no dark literals in a light render; Metrics and the inline dashboard visually confirmed under a light pack.
- 2026-08-11: **Phase 3d — Appearance section: per-browser theme selector.** New Settings section listing all installed packs with a live swatch built from each pack's **resolved** tokens (so an inheriting pack previews correctly). Selection stored in a `pc_theme` cookie — browser-local, never written to project config, verified by diffing `console.yaml` / `project.yml` after switching. Cookie chosen over localStorage because the server must see the choice: `/theme/assets/*` serves the logo, favicon, web font and footer from the *active* pack, so a client-only swap would change the colours and leave the branding behind. New `themes.list_packs()` / `themes.safe_theme_name()` / `resolve(cfg, name)`; the cookie feeds a filesystem path so it is validated against installed packs first (`../../etc`, `../dark`, unknown → project default, verified). **F11 fixed**: the bundled `light`/`dark` packs ship no assets at all, so selecting one 404'd logo/favicon/font — Manrope disappearing silently, since a failed `@font-face` has no error path. Asset lookup is now a fallback chain (selected → project default), on the principle that colours are per-pack but identity assets belong to the project; traversal still refused outright. End-to-end in-browser test: switch → cookie set, palette + active-card marker move, logo and Manrope still load; clear → returns to `globallogic-blue`. 16 routes 200 on the default and 6 spot-checked under the `light` pack; light pack visually verified. Discovered 5 installed packs, not 1.
- 2026-08-11: **Phase 3c — `category_colors` is now a theme-pack capability, applied to every milestone (F8 closed).** Per Ben: rather than special-casing Engineering Prereqs, theme packs gained an ordered categorical ramp and the tracker assigns it across the whole milestone dimension. Contract split so it stays generic — **the pack supplies the palette, the consumer assigns meaning**: sequential entries cool→warm for ordinal categories (assigned in **document order**, since milestones are a sequence), the **last entry reserved** for a category outside the ordering. Added to `dark` (stock, reserved = violet-400 rather than indigo-400, which would have collided with its own `accent`), `light` (dark hue ends — the dark pack's mid-tones sit at 3.4–4.1:1 on white and fail AA) and `globallogic-blue`. Consumed by `render.py` for summary cards, phase badges and progress-row labels — one colour per milestone so the three read as a group; progress-bar **segments** stay status-coloured. `PHASE_COLOR_CYCLE` deleted: it mixed `--accent` with `--green`/`--orange`, borrowing two **status** colours for a category dimension, so a milestone badge could read as "done". Baked `--cat-1…5` added to the standalone `:root` so a console-less render is still coloured. Also fixed **F9** (comment stripper truncated any comma-separated hex list to its first entry — silent, the value still parsed) and **F10** (a digit-leading CSS class is invalid, so browsers had been discarding the 510k+PCCP badge rule entirely — that milestone had never been coloured; verified live in the iframe before and after). Docs: `category_colors` contract in project-console SKILL.md, consumption + assignment rules in tracker SKILL.md. Regenerated: 196 rows and every status count byte-identical; 0 invalid selectors; theme ramp and baked fallback both present.
- 2026-08-10: **Phase 3b — tracker dashboard now follows the theme (F6 closed).** Changes in the **`tracker` skill** (`scripts/render.py`): (1) `load_brand_theme()` rewritten around a declarative `_THEME_TOKEN_MAP` lifting **11** tokens instead of 2 — `body_bg→--bg`, `surface→--surface`, `surface_2→--surface2`, `surface_muted→--help-bg`, `border`, `text`, `text_muted`, `primary→--brand` **and** `--accent` (the baked default is literally `--brand:var(--accent)`, i.e. one role), `accent→--accent2`, `font_body→--font`. Status/category colours (`--green/--yellow/--red/--orange/--cyan/--pink`) deliberately **not** mapped — a "blocked" row that turns brand-coloured stops communicating. (2) **F7 fixed**: the theme-yaml key regex could not match digits, silently dropping `surface_2`. (3) ~20 hardcoded brand literals in `_CSS_BASE_INNER` converted to `color-mix` on their own tokens — the help affordances (`#a855f7`/`#c084fc`/`rgba(168,85,247)`), the info affordances (`rgba(56,189,248)`), and the in-review/ai-status badges (`rgba(129,140,248)`) whose text already used `var(--accent2)` while their background did not. (4) Both `SCOPE_COLOR_CYCLE` / `PHASE_COLOR_CYCLE` entries now derive each tint from its own paired token instead of an rgba literal of that token's default — otherwise a themed token drifts from its hardcoded tint. (5) `.help-mode-banner.purple` renamed `.alt` (one CSS pair + one emitter; no JS references) since a colour-named class is wrong under every pack but the old one. Dashboard regenerated with PyYAML present (the SKILL.md overlay gotcha): **196 rows and every status count byte-identical**; zero `#a855f7` / `#c084fc` / purple-, sky- or indigo-rgba literals remain; blue override present and ordered after the baked defaults, so the standalone file still opens correctly with no console. 17 endpoints 200 including `/workflows/tracker/dashboard.css` (the inline-render path sharing `_CSS_BASE_INNER`). **F8 raised** — `--eng` violet is now the only unthemed element; left as a category hue pending Ben's call.
- 2026-08-10: **Phase 3 — blue is live, pending Ben's verdict.** `console.yaml` `theme: globallogic-dark` → `globallogic-blue` (one line; backup at `tasks/ben/_scratch/console.yaml.before-blue`), console restarted. Verified on the wire: `--body-bg #0a1620`, `--surface #172c3c`, `--brand-primary #5fa8dd`, `--brand-accent #d9a441`; **no `#0f172a` / `#1e293b` / `#334155` / `#475569` / `#a855f7` / `#38bdf8` anywhere in the served theme block**; all three pack assets 200 (`logo.png`, `favicon.ico`, `fonts/manrope-latin.woff2`) and the footer renders — the F3 failure mode did not occur; 14 routes 200 including the tracker overlay page and embed. **F6 confirmed visually**: the Tracker Status Update dashboard renders slate surfaces with a purple `--brand` inside blue console chrome — the generated artifact was rendered under the old theme and its palette is baked in regardless. **Rollback: restore the one line and restart.**
- 2026-08-10: **Phase 2 complete — tokenised, and a proven no-op on the current theme.** `tracker_interactive.css` rewritten against the **dashboard's** variable namespace (F5) — all 9 tokens asserted to resolve in the generated dashboard document; 13 hex + 4 previously-missed `rgba(56,189,248,…)` values removed. `console.css` accidental hardcodes 25 → **0** (the 15 remaining matches are 3 inside comments, 6 intentional semantic hue anchors, 5 white-on-brand-fill, 1 documented PDF-viewer grey). **F1 fixed and measured live**: the YAML pane now sits on `--code-bg` with base text at **15.19:1, up from 1.17:1**; the resolved `color-mix` values (`#85c8a8` / `#e1b790` / `#e19cbb`) match the pre-computed predictions exactly. Key insight: no fixed colour can clear AA on both a near-white and a near-black code background — the syntax tones are therefore *mixed toward* `--code-text`, so hue survives while lightness follows the pack (7.7–10.4:1 across light, dark and blue) with **zero new theme keys**. **Regression: 0 of 11.0M pixels changed** across home / setup / documents on the current theme; all 13 routes 200; tracker overlay page + embed both 200. **F6 raised** — the tracker dashboard has its own baked palette and will not follow the theme; deliberately not fixed unilaterally (different skill + committed artifact).
- 2026-08-10: **Phase 1 complete — new pack, provably inert.** `tools/project-console/themes/globallogic-blue/` created: `theme.yaml` (`extends: globallogic-dark`, 20 colour overrides) plus copied `logo.png`, `favicon.ico`, `footer.html.j2` and `fonts/manrope-latin.woff2`; asset parity against the source pack asserted. Verified: both packs resolve to 28 emitted tokens; inheritance carries `brand_name` / `font_body` / `logo_filter`; `has_footer` true for both; `themes.resolve(cfg)` still returns `globallogic-dark` and the blue palette does not appear in the served CSS (`--brand-primary: #a855f7` still on the wire); all 13 routes 200; `git status` shows **zero modified files** from this phase. **F3 found and corrected against the approved plan** — the plan's claim that fonts need no copying was wrong; `/static/fonts/manrope-latin.woff2` 404s and the font actually resolves through the active pack, so omitting it would have silently dropped Manrope.
- 2026-08-10: Task created; plan approved (`snappy-percolating-octopus.md`). **Phase 0 complete** — 13 routes verified 200, 13 full-page baselines captured to the gitignored scratch sandbox. Theming contract verified against source rather than assumed (per-request resolve, `lru_cache`d config, non-inherited pack assets). Hardcoded-colour scope corrected from ~90 to ~33 actionable lines. **F1 found and quantified**: 6 of 7 YAML syntax colours fail WCAG AA on the dark theme, base text at 1.17:1 — Documents-tab YAML is effectively invisible today.
