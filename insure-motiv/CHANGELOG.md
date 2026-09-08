# Changelog — Insure Motiv

All notable changes to the Insure Motiv site.

The site is one page. `index.html` is generated: `build/unbundle.py` produces it
from `bundled-original.html`, then `build/fix_cls.py` patches it. Both scripts
assert on their anchors and stop rather than half-apply, so a rebuild is:

    python build/unbundle.py && python build/fix_cls.py

---

## [1.1.0] — 2026-09-09

**Loading and layout stability.** Client report: *"An old menu header flashes
during load, potentially slowing site performance"*, plus the hero form
repositioning itself after load.

### Files changed

| File | What changed |
|---|---|
| `index.html` | Regenerated as a plain 51 KB page instead of a 1,426 KB self-extracting bundle; quote-form height reserved and skeleton added. |
| `assets/` | **New.** 18 files unpacked from the bundle: 6 webp, 9 woff2, 3 js, favicon. |
| `bundled-original.html` | **New.** The delivered bundle, kept for reference. Not deployed. |
| `build/unbundle.py` | **New.** Unpacks the bundle into a normal static site. |
| `build/fix_cls.py` | **New.** Reserves the quote-form height and fills the reserve while it loads. |
| `.image-slots.state.json` | **New.** Empty state file the image-slot component fetches; silences a 404. |
| `vercel.json` | **New.** Immutable caching on `/assets/`. |
| `.vercelignore` | **New.** Keeps `build/`, `CHANGELOG.md` and the 1.4 MB bundle out of the deploy. |

### The header flash

The delivered `index.html` was a self-extracting bundle: a full-screen navy
placeholder with an "Unpacking…" badge, a 1.4 MB base64 manifest holding every
image, font and script, and the real page stored as a JSON string. Nothing
rendered until JavaScript decoded ~926 KB of base64 and rebuilt the document,
so every visitor saw the placeholder first. **That placeholder was the "old
menu header" the client reported** — not a stale header, but the bundler's
splash.

`build/unbundle.py` writes the real document to `index.html` and each asset to
`assets/`, so the browser gets HTML in the first byte and fetches assets in
parallel and individually cacheable. It also:

- drops one script the page never referenced,
- removes two Google font preconnects that cost a DNS + TLS handshake each and
  were never used, since the fonts are self-hosted,
- hoists the `@font-face` block out of `<helmet>` into `<head>` so the font
  fetch starts during the initial HTML parse rather than after a 69 KB script
  has executed,
- adds the title, meta description, robots tag and a preload for the first
  font.

| | Before | After |
|---|---|---|
| `index.html` | 1,426 KB | 51 KB |
| DOMContentLoaded | 109 ms | 29 ms |
| First Contentful Paint | 96 ms (splash) | 68 ms (real content) |
| Splash screen | shown every load | gone |

First-party console errors: 0. Four remain, all from Cloudflare Turnstile
inside the embedded GoHighLevel form.

### The hero form jump (CLS 0.1495 → 0.0000)

Both quote-form iframes declared `min-height: 652px`, but the GoHighLevel
resizer grows them to their real height once the form reports back — measured
**1027px** at 1440px wide and **1187px** at 390px. The hero card therefore grew
~375px after load. Measured CLS was **0.1495** ("needs work"), and both shifts
attributed to `div#quote`.

`build/fix_cls.py` moves the sizing out of the inline `style` attribute — which
cannot hold a media query — into a `<head>` rule that reserves the measured
height at each breakpoint. The resizer is still free to adjust afterwards; this
only removes the first-load jump.

| Viewport | Before | After |
|---|---|---|
| 1440 × 900 | 0.1495 | 0.0002 |
| 390 × 844 | 0.1495 | 0.0000 |

### The blank card

Reserving the height exposed the next problem: the resizer keeps its iframe
`visibility: hidden` until the form reports, so the reserved space showed as a
tall empty card. Each iframe now sits over a skeleton — a label bar and a field
bar tiled down the full reserve, with a shimmer sweep.

No load handshake is involved. The skeleton sits at `z-index: 0` and the iframe
at `z-index: 1`, so the skeleton is simply covered when the resizer reveals the
iframe over it. Both iframes are given an opaque white background for this: the
GoHighLevel form itself is transparent, and the footer copy shipped without a
background, so the skeleton bars showed through its loaded fields. Both cards
behind these iframes are already white, so this changes nothing once loaded.

The shimmer runs a bounded 10 iterations — the skeleton stays in the DOM under
the loaded form, and an infinite animation there would repaint for the life of
the page.

### Tried and reverted

Both were verified in the browser, not assumed:

- **`onload` on the iframe** to fade the skeleton out. The embed strips the
  attribute and re-parents the iframe into its own `.ep-wrapper`, so the
  handler never fires and `this.parentNode` is no longer the shell.
- **`loading="lazy"` on the below-fold second form.** The resizer hides the
  iframe at init and reveals it when the form posts its height; deferring the
  load misses that handshake and the iframe stays `visibility: hidden`
  permanently, leaving the skeleton up for good.

### Deploy

`public/` is deliberately not used as a folder name — Vercel treats it as the
entire output directory for a zero-config static project, which would publish
the assets and no `index.html`.
