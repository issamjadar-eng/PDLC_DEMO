---
name: frontend-slides
description: Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files — for any domain (product launches, board materials, investor pitches, town-halls, conference talks, internal training, regulated-industry briefings). Use when the user wants to build a presentation, convert a PPT/PPTX to web, or create slides for a talk / pitch / report. Helps non-designers discover their aesthetic through visual exploration rather than abstract choices.
version: 0.5.1
updated: 2026-08-03
---

# Frontend Slides

Create zero-dependency, animation-rich HTML presentations that run entirely in the browser.

## Origin & Modifications

This skill is a **fork** of the original [`frontend-slides`](https://github.com/zarazhangrui/frontend-slides) skill by **Zara Zhang** (Copyright © 2025), licensed under the MIT License. The original skill's full MIT terms are preserved verbatim in [`LICENSE`](LICENSE); the pinned upstream commit at fork time is recorded in [`.pinned-sha`](.pinned-sha).

The fork is maintained by the medtech-docs registry contributors and is licensed under the same MIT terms (see the "Modifications" block in `LICENSE`). Notable changes from upstream:

- **Cross-domain neutralization** — example READMEs and design-language references rotated across multiple domains (SaaS, finance, manufacturing, healthcare, education, …) so the skill teaches by pattern rather than by single-domain idiom
- **Vocabulary-pack architecture in the sibling `md-deck` skill** — domain-specific keyword routing moved out of trunk into opt-in packs
- **Registry integration** — added attribution surfaces, sync-skills compatibility, MIT modifications block

Substantive improvements should flow back upstream where compatible; project-specific embellishments do not.

## Used by `md-deck` (sibling skill)

`frontend-slides` is the **canonical source** of slide-rendering infrastructure for the project's two slide-authoring skills. The non-interactive markdown pipeline `md-deck` consumes the following files at build time:

| File | Consumed by md-deck |
|---|---|
| `viewport-base.css` | Prepended to every md-deck output — owns the `100vh` / `clamp()` viewport contract |
| `presets/<name>.css` | Resolved by md-deck `--style <name>`; bold-signal canonical lives here |
| `STYLE_PRESETS.md` | Reference index for available preset names |
| `scripts/export-pdf.sh` | md-deck has no PDF export of its own; it documents this script as the export path |
| `scripts/deploy.sh` | md-deck has no deploy of its own; documented for share workflows |

When adding a new preset or changing viewport rules, both skills inherit. When adding the interactive wizard, PPTX ingest, or in-browser editing — that is `frontend-slides` only and not exposed to md-deck.

## Core Principles

1. **Zero Dependencies** — Single HTML files with inline CSS/JS. No npm, no build tools.
2. **Show, Don't Tell** — Generate visual previews, not abstract choices. People discover what they want by seeing it.
3. **Distinctive Design** — No generic "AI slop." Every presentation must feel custom-crafted.
4. **Viewport Fitting (NON-NEGOTIABLE)** — Every slide MUST fit exactly within 100vh. No scrolling within slides, ever. Content overflows? Split into multiple slides.
5. **Structure Before Styling** — perceived complexity is usually a structure problem, not a styling problem. For any deck over ~10 slides or carrying dense technical content, read [deck-structure.md](deck-structure.md) during content discovery and run its structure-pass checklist before the geometry/visual passes: answer-first opening (BLUF), an orientation layer (exec-summary slide, section dividers with a you-are-here tracker, a "name the parts" beat before the first dense diagram), one altitude per diagram with names consistent across zoom levels, claim-sentence titles, and depth demoted to detail-on-demand rather than compressed. This is also the playbook when an existing deck draws "feels complicated" feedback — the orientation layer is purely additive, so the fix does not disturb finished slides.

## Design Aesthetics

You tend to converge toward generic, "on distribution" outputs. In frontend design, this creates what users call the "AI slop" aesthetic. Avoid this: make creative, distinctive frontends that surprise and delight.

Focus on:

- Typography: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics.
- Color & Theme: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes. Draw from IDE themes and cultural aesthetics for inspiration.
- Motion: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions.
- Backgrounds: Create atmosphere and depth rather than defaulting to solid colors. Layer CSS gradients, use geometric patterns, or add contextual effects that match the overall aesthetic.

Avoid generic AI-generated aesthetics:

- Overused font families (Inter, Roboto, Arial, system fonts)
- Cliched color schemes (particularly purple gradients on white backgrounds)
- Predictable layouts and component patterns
- Cookie-cutter design that lacks context-specific character

Interpret creatively and make unexpected choices that feel genuinely designed for the context. Vary between light and dark themes, different fonts, different aesthetics. You still tend to converge on common choices (Space Grotesk, for example) across generations. Avoid this: it is critical that you think outside the box!

## Viewport Fitting Rules

These invariants apply to EVERY slide in EVERY presentation:

- Every `.slide` must have `height: 100vh; height: 100dvh; overflow: hidden;`
- ALL font sizes and spacing must use `clamp(min, preferred, max)` — never fixed px/rem
- Content containers need `max-height` constraints
- Images: `max-height: min(50vh, 400px)`
- Breakpoints required for heights: 700px, 600px, 500px
- Include `prefers-reduced-motion` support
- Never negate CSS functions directly (`-clamp()`, `-min()`, `-max()` are silently ignored) — use `calc(-1 * clamp(...))` instead

**When generating, read `viewport-base.css` and include its full contents in every presentation.**

### Content Density Limits Per Slide

| Slide Type    | Maximum Content                                           |
| ------------- | --------------------------------------------------------- |
| Title slide   | 1 heading + 1 subtitle + optional tagline                 |
| Content slide | 1 heading + 4-6 bullet points OR 1 heading + 2 paragraphs |
| Feature grid  | 1 heading + 6 cards maximum (2x3 or 3x2)                  |
| Code slide    | 1 heading + 8-10 lines of code                            |
| Quote slide   | 1 quote (max 3 lines) + attribution                       |
| Image slide   | 1 heading + 1 image (max 60vh height)                     |

**Content exceeds limits? Split into multiple slides. Never cram, never scroll.**

---

## Phase 0: Detect Mode

Determine what the user wants:

- **Mode A: New Presentation** — Create from scratch. Go to Phase 1.
- **Mode B: PPT Conversion** — Convert a .pptx file. Go to Phase 4.
- **Mode C: Enhancement** — Improve an existing HTML presentation. Read it, understand it, enhance. **Follow Mode C modification rules below.**

### Mode C: Modification Rules

When enhancing existing presentations, viewport fitting is the biggest risk:

1. **Before adding content:** Count existing elements, check against density limits
2. **Adding images:** Must have `max-height: min(50vh, 400px)`. If slide already has max content, split into two slides
3. **Adding text:** Max 4-6 bullets per slide. Exceeds limits? Split into continuation slides
4. **After ANY modification, verify:** `.slide` has `overflow: hidden`, new elements use `clamp()`, images have viewport-relative max-height, content fits at 1280x720
5. **Proactively reorganize:** If modifications will cause overflow, automatically split content and inform the user. Don't wait to be asked

**When adding images to existing slides:** Move image to new slide or reduce other content first. Never add images without checking if existing content already fills the viewport.

---

## Phase 1: Content Discovery (New Presentations)

**Ask ALL questions in a single AskUserQuestion call** so the user fills everything out at once:

**Question 1 — Purpose** (header: "Purpose"):
What is this presentation for? Options: Pitch deck / Teaching-Tutorial / Conference talk / Internal presentation

**Question 2 — Length** (header: "Length"):
Approximately how many slides? Options: Short 5-10 / Medium 10-20 / Long 20+

**Question 3 — Content** (header: "Content"):
Do you have content ready? Options: All content ready / Rough notes / Topic only

**Question 4 — Inline Editing** (header: "Editing"):
Do you need to edit text directly in the browser after generation? Options:

- "Yes (Recommended)" — Can edit text in-browser, auto-save to localStorage, export file
- "No" — Presentation only, keeps file smaller

**Remember the user's editing choice — it determines whether edit-related code is included in Phase 3.**

If user has content, ask them to share it.

### Step 1.2: Image Evaluation (if images provided)

If user selected "No images" → skip to Phase 2.

If user provides an image folder:

1. **Scan** — List all image files (.png, .jpg, .svg, .webp, etc.)
2. **View each image** — Use the Read tool (Claude is multimodal)
3. **Evaluate** — For each: what it shows, USABLE or NOT USABLE (with reason), what concept it represents, dominant colors
4. **Co-design the outline** — Curated images inform slide structure alongside text. This is NOT "plan slides then add images" — design around both from the start (e.g., 3 screenshots → 3 feature slides, 1 logo → title/closing slide)
5. **Confirm via AskUserQuestion** (header: "Outline"): "Does this slide outline and image selection look right?" Options: Looks good / Adjust images / Adjust outline

**Logo in previews:** If a usable logo was identified, embed it (base64) into each style preview in Phase 2 — the user sees their brand styled three different ways.

---

## Phase 2: Style Discovery

**This is the "show, don't tell" phase.** Most people can't articulate design preferences in words.

### Step 2.0: Style Path

Ask how they want to choose (header: "Style"):

- "Show me options" (recommended) — Generate 3 previews based on mood
- "I know what I want" — Pick from preset list directly

**If direct selection:** Show preset picker and skip to Phase 3. Available presets are defined in [STYLE_PRESETS.md](STYLE_PRESETS.md).

### Step 2.1: Mood Selection (Guided Discovery)

Ask (header: "Vibe", multiSelect: true, max 2):
What feeling should the audience have? Options:

- Impressed/Confident — Professional, trustworthy
- Excited/Energized — Innovative, bold
- Calm/Focused — Clear, thoughtful
- Inspired/Moved — Emotional, memorable

### Step 2.2: Generate 3 Style Previews

Based on mood, generate 3 distinct single-slide HTML previews showing typography, colors, animation, and overall aesthetic. Read [STYLE_PRESETS.md](STYLE_PRESETS.md) for available presets and their specifications.

| Mood                | Suggested Presets                                  |
| ------------------- | -------------------------------------------------- |
| Impressed/Confident | Bold Signal, Electric Studio, Dark Botanical       |
| Excited/Energized   | Creative Voltage, Neon Cyber, Split Pastel         |
| Calm/Focused        | Notebook Tabs, Paper & Ink, Swiss Modern           |
| Inspired/Moved      | Dark Botanical, Vintage Editorial, Pastel Geometry |

Save previews to a per-build temp directory under the OS `/tmp/` — **never** to a project-root location like `.claude-design/`. Create the dir with `mktemp -d -t frontend-slides-previews` (or equivalent) and remember the path for the Phase 5 cleanup step. Files inside: `style-a.html`, `style-b.html`, `style-c.html`. Each should be self-contained, ~50–100 lines, showing one animated title slide.

**Why `/tmp/`, not the project tree:** previews are transient intermediates consumed within this single activity. Writing them to the project root pollutes the working tree and risks accidental commits if they aren't gitignored. Some consumer projects enforce this via a scratch-and-tmp rule (e.g., `.claude/rules/scratch-and-tmp.md` reserves `tasks/{person}/_scratch/` for personal sandboxes and the OS `/tmp/` for activity-scoped intermediates). Even in projects without that rule, the same principle applies — keep transient build artifacts outside the source tree.

Open each preview automatically for the user (the absolute `/tmp/...` path works fine with `open` on macOS / `xdg-open` on Linux).

### Step 2.3: User Picks

Ask (header: "Style"):
Which style preview do you prefer? Options: Style A: [Name] / Style B: [Name] / Style C: [Name] / Mix elements

If "Mix elements", ask for specifics.

---

## Phase 3: Generate Presentation

Generate the full presentation using content from Phase 1 (text, or text + curated images) and style from Phase 2.

If images were provided, the slide outline already incorporates them from Step 1.2. If not, CSS-generated visuals (gradients, shapes, patterns) provide visual interest — this is a fully supported first-class path.

**Before generating, read these supporting files:**

- [html-template.md](html-template.md) — HTML architecture and JS features
- [viewport-base.css](viewport-base.css) — Mandatory CSS (include in full)
- [animation-patterns.md](animation-patterns.md) — Animation reference for the chosen feeling

**Key requirements:**

- Single self-contained HTML file, all CSS/JS inline
- Include the FULL contents of viewport-base.css in the `<style>` block
- Use fonts from Fontshare or Google Fonts — never system fonts
- Add detailed comments explaining each section
- Every section needs a clear `/* === SECTION NAME === */` comment block

---

## Phase 4: PPT Conversion

When converting PowerPoint files:

1. **Extract content** — Run `python scripts/extract-pptx.py <input.pptx> <output_dir>` (install python-pptx if needed: `pip install python-pptx`)
2. **Confirm with user** — Present extracted slide titles, content summaries, and image counts
3. **Style selection** — Proceed to Phase 2 for style discovery
4. **Generate HTML** — Convert to chosen style, preserving all text, images (from assets/), slide order, and speaker notes (as HTML comments)

---

## Phase 5: Delivery

1. **Clean up** — Delete the per-build preview temp directory created in Phase 2.2 (the `mktemp -d` path under `/tmp/`). For backward compatibility, also remove a legacy `.claude-design/slide-previews/` directory if one exists at the project root from an older build.
2. **Open** — Use `open [filename].html` to launch in browser
3. **Summarize** — Tell the user:
   - File location, style name, slide count
   - Navigation: Arrow keys, Space, scroll/swipe, click nav dots
   - How to customize: `:root` CSS variables for colors, font link for typography, `.reveal` class for animations
   - If inline editing was enabled: Hover top-left corner or press E to enter edit mode, click any text to edit, Ctrl+S to save

---

## Phase 6: Share & Export (Optional)

After delivery, **ask the user:** _"Would you like to share this presentation? I can deploy it to a live URL (works on any device including phones) or export it as a PDF."_

Options:

- **Deploy to URL** — Shareable link that works on any device
- **Export to PDF** — Universal file for email, Slack, print
- **Both**
- **No thanks**

If the user declines, stop here. If they choose one or both, proceed below.

### 6A: Deploy to a Live URL (Vercel)

This deploys the presentation to Vercel — a free hosting platform. The link works on any device (phones, tablets, laptops) and stays live until the user takes it down.

**If the user has never deployed before, guide them step by step:**

1. **Check if Vercel CLI is installed** — Run `npx vercel --version`. If not found, install Node.js first (`brew install node` on macOS, or download from https://nodejs.org).

2. **Check if user is logged in** — Run `npx vercel whoami`.
   - If NOT logged in, explain: _"Vercel is a free hosting service. You need an account to deploy. Let me walk you through it:"_
     - Step 1: Ask user to go to https://vercel.com/signup in their browser
     - Step 2: They can sign up with GitHub, Google, email — whatever is easiest
     - Step 3: Once signed up, run `vercel login` and follow the prompts (it opens a browser window to authorize)
     - Step 4: Confirm login with `vercel whoami`
   - Wait for the user to confirm they're logged in before proceeding.

3. **Deploy** — Run the deploy script:

   ```bash
   bash scripts/deploy.sh <path-to-presentation>
   ```

   The script accepts either a folder (with index.html) or a single HTML file.

4. **Share the URL** — Tell the user:
   - The live URL (from the script output)
   - That it works on any device — they can text it, Slack it, email it
   - To take it down later: visit https://vercel.com/dashboard and delete the project
   - The Vercel free tier is generous — they won't be charged

**⚠ Deployment gotchas:**

- **Local images/videos must travel with the HTML.** The deploy script auto-detects files referenced via `src="..."` in the HTML and bundles them. But if the presentation references files via CSS `background-image` or unusual paths, those may be missed. **Before deploying, verify:** open the deployed URL and check that all images load. If any are broken, the safest fix is to put the HTML and all its assets into a single folder and deploy the folder instead of a standalone HTML file.
- **Prefer folder deployments when the presentation has many assets.** If the presentation lives in a folder with images alongside it (e.g., `my-deck/index.html` + `my-deck/logo.png`), deploy the folder directly: `bash scripts/deploy.sh ./my-deck/`. This is more reliable than deploying a single HTML file because the entire folder contents are uploaded as-is.
- **Filenames with spaces work but can cause issues.** The script handles spaces in filenames, but Vercel URLs encode spaces as `%20`. If possible, avoid spaces in image filenames. If the user's images have spaces, the script handles it — but if images still break, renaming files to use hyphens instead of spaces is the fix.
- **Redeploying updates the same URL.** Running the deploy script again on the same presentation overwrites the previous deployment. The URL stays the same — no need to share a new link.

### 6B: Export to PDF

This captures each slide as a screenshot and combines them into a PDF. Perfect for email attachments, embedding in documents, or printing.

**Note:** Animations and interactivity are not preserved — the PDF is a static snapshot. This is normal and expected; mention it to the user so they're not surprised.

1. **Run the export script:**

   ```bash
   bash scripts/export-pdf.sh <path-to-html> [output.pdf]
   ```

   If no output path is given, the PDF is saved next to the HTML file.

2. **What happens behind the scenes** (explain briefly to the user):
   - A headless browser opens the presentation at 1920×1080 (standard widescreen)
   - It screenshots each slide one by one
   - All screenshots are combined into a single PDF
   - The script needs Playwright (a browser automation tool) — it will install automatically if missing

3. **If Playwright installation fails:**
   - The most common issue is Chromium not downloading. Run: `npx playwright install chromium`
   - If that fails too, it may be a network/firewall issue. Ask the user to try on a different network.

4. **Deliver the PDF** — The script auto-opens it. Tell the user:
   - The file location and size
   - That it works everywhere — email, Slack, Notion, Google Docs, print
   - Animations are replaced by their final visual state (still looks great, just static)

**⚠ PDF export gotchas:**

- **First run is slow.** The script installs Playwright and downloads a Chromium browser (~150MB) into a temp directory. This happens once per run. Warn the user it may take 30-60 seconds the first time — subsequent exports within the same session are faster.
- **Slides must use `class="slide"`.** The export script finds slides by querying `.slide` elements. If the presentation uses a different class name, the script will report "0 slides found" and fail. All presentations generated by this skill use `.slide`, so this only matters for externally-created HTML.
- **Local images must be loadable via HTTP.** The script starts a local server and loads the HTML through it (so Google Fonts and relative image paths work). If images use absolute filesystem paths (e.g., `src="/Users/name/photo.png"`) instead of relative paths (e.g., `src="photo.png"`), they won't load. Generated presentations always use relative paths, but converted or user-provided decks might not — check and fix if needed.
- **Local images appear in the PDF** as long as they are in the same directory as (or relative to) the HTML file. The export script serves the HTML's parent directory over HTTP, so relative paths like `src="photo.png"` resolve correctly — including filenames with spaces. If images still don't appear, check: (1) the image files actually exist at the referenced path, (2) the paths are relative, not absolute filesystem paths like `/Users/name/photo.png`.
- **Large presentations produce large PDFs.** Each slide is captured as a full 1920×1080 PNG screenshot. An 18-slide deck can produce a ~20MB PDF. If the PDF exceeds 10MB, ask the user: _"The PDF is [size]. Would you like me to compress it? It'll look slightly less sharp but the file will be much smaller."_ If yes, re-run the export with the `--compact` flag:
  ```bash
  bash scripts/export-pdf.sh <path-to-html> [output.pdf] --compact
  ```
  This renders at 1280×720 instead of 1920×1080, typically cutting file size by 50-70% with minimal visual difference.

---

## Supporting Files

| File                                               | Purpose                                                              | When to Read              |
| -------------------------------------------------- | -------------------------------------------------------------------- | ------------------------- |
| [deck-structure.md](deck-structure.md)             | Evidence-based deck structure & orientation rules (BLUF, dividers/tracker, altitude discipline, assertion-evidence titles, cognitive-load mechanics) + structure-pass checklist | Phase 1 (content discovery); any "deck feels complicated" retrofit |
| [STYLE_PRESETS.md](STYLE_PRESETS.md)               | 12 curated visual presets with colors, fonts, and signature elements | Phase 2 (style selection) |
| [viewport-base.css](viewport-base.css)             | Mandatory responsive CSS — copy into every presentation              | Phase 3 (generation)      |
| [html-template.md](html-template.md)               | HTML structure, JS features, code quality standards                  | Phase 3 (generation)      |
| [animation-patterns.md](animation-patterns.md)     | CSS/JS animation snippets and effect-to-feeling guide                | Phase 3 (generation)      |
| [scripts/extract-pptx.py](scripts/extract-pptx.py) | Python script for PPT content extraction                             | Phase 4 (conversion)      |
| [scripts/deploy.sh](scripts/deploy.sh)             | Deploy slides to Vercel for instant sharing                          | Phase 6 (sharing)         |
| [scripts/export-pdf.sh](scripts/export-pdf.sh)     | Export slides to PDF                                                 | Phase 6 (sharing)         |

---

## Changelog

- **0.5.1** (2026-08-03) — `deck-structure.md` structure-pass checklist gains the **cold-reader test**: run persona critics (an exec + a specialist, neither shown the source docs) over the built deck to catch terms used before definition, numbered references to lists the deck never shows, and audience false friends. Proven pattern: two such critics on a real deck surfaced ~30 comprehension defects the author could no longer see, including one factual overclaim.
- **0.5.0** (2026-08-03) — Added `deck-structure.md`: evidence-based deck structure & orientation reference (answer-first/BLUF opening, orientation layer with exec-summary + tracker dividers + pre-training beat, single-altitude diagram discipline with cross-zoom name consistency, assertion-evidence claim titles, ranked cognitive-load mechanics, live-deck vs leave-behind split) distilled from a sourced research pass (Minto/BLUF, Garner & Alley, Mayer, Shneiderman, C4/arc42/Hohpe, Duarte/Reynolds). New core principle 5 ("Structure Before Styling") wires it into Phase 1 and the "deck feels complicated" retrofit case.
- **0.4.1** (2026-05-17) — Phase 2.2 style previews now write to a per-build `mktemp -d` directory under the OS `/tmp/` instead of `.claude-design/slide-previews/` at the project root. Phase 5.1 cleanup updated accordingly (with backward-compatible removal of the legacy path). Fixes drift against consumer-project scratch-and-tmp rules and prevents accidental commits of transient preview files.
- **0.4.0** (2026-05-02) — Fork baseline (see "Origin & Modifications").
