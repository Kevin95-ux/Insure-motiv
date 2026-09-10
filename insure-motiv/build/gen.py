# -*- coding: utf-8 -*-
"""Build the Insure Motiv plain-document legal pages.

Reads a lightweight source file (build/src/<name>.txt) and wraps the rendered
document in the shared global header and footer.

Source directives
-----------------
:key value      page metadata (eyebrow, title, effective, updated, out)
H2 <text>       numbered section heading
H3 <text>       sub-heading
NOTE <text>     emphasised legal notice paragraph
ADDR <text>     address / contact block line (consecutive lines group)
- <text>        list item (consecutive lines group)
RAW <html>      literal markup, used for the collected-data table
<text>          paragraph
[label](/href)  inline link
"""
import io, os, re, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

STYLE = u"""  <style>
    #wm-legal {
      /* Insure Motiv palette, taken from index.html: navy ink, teal accents,
         warm ivory ground, sand rules. */
      --wl-ink: #12304F;
      --wl-body: #3C4A55;
      --wl-muted: #5C6B76;
      --wl-line: #E7E0D6;
      --wl-band: #FBF8F4;
      --wl-navy: #12304F;
      --wl-blue: #0D6E63;
      --wl-orange: #0A574E;
      --wl-white: #ffffff;
      /* The two faces the site self-hosts; see _fonts.html. */
      --wl-serif: "Source Serif 4", "Iowan Old Style", Georgia,
        "Times New Roman", serif;
      --wl-sans: "Public Sans", -apple-system, BlinkMacSystemFont, "Segoe UI",
        Roboto, Arial, Helvetica, sans-serif;

      display: block;
      width: 100%;
      margin: 0;
      padding: 0;
      color: var(--wl-body);
      background: var(--wl-band);
      font-family: var(--wl-sans);
      -webkit-font-smoothing: antialiased;
    }

    #wm-legal *,
    #wm-legal *::before,
    #wm-legal *::after {
      box-sizing: border-box;
    }

    /* ---------- title band ---------- */

    #wm-legal .wl-band {
      padding: clamp(2.75rem, 6vw, 4.5rem) 1.25rem clamp(2.25rem, 5vw, 3.5rem);
      text-align: center;
      background: linear-gradient(180deg, #FFFFFF 0%, var(--wl-band) 100%);
    }

    #wm-legal .wl-eyebrow {
      margin: 0 0 0.9rem;
      color: var(--wl-blue);
      font-size: 0.6875rem;
      font-weight: 600;
      letter-spacing: 0.22em;
      text-transform: uppercase;
    }

    #wm-legal .wl-title {
      max-width: 60rem;
      margin: 0 auto;
      color: var(--wl-navy);
      font-family: var(--wl-serif);
      font-size: clamp(1.9rem, 5.2vw, 3.15rem);
      font-weight: 400;
      line-height: 1.14;
      letter-spacing: 0.015em;
    }

    #wm-legal .wl-rule {
      width: 3.5rem;
      height: 2px;
      margin: 1.5rem auto 0;
      border: 0;
      background: var(--wl-orange);
    }

    /* ---------- document card ---------- */

    #wm-legal .wl-doc {
      max-width: 62rem;
      margin: 0 auto clamp(3rem, 7vw, 5.5rem);
      padding: clamp(1.75rem, 5vw, 4rem) clamp(1.25rem, 5vw, 4.25rem);
      border: 1px solid var(--wl-line);
      border-radius: 4px;
      background: var(--wl-white);
      box-shadow: 0 1px 2px rgba(0, 31, 58, 0.04),
        0 1.25rem 3rem rgba(0, 31, 58, 0.05);
    }

    #wm-legal .wl-dates {
      margin: 0 0 2rem;
      padding-bottom: 1.5rem;
      border-bottom: 1px solid var(--wl-line);
      color: var(--wl-navy);
      font-size: 0.8125rem;
      font-weight: 600;
      line-height: 1.9;
    }

    #wm-legal p {
      margin: 0 0 1.05rem;
      font-size: 0.875rem;
      line-height: 1.85;
    }

    #wm-legal h2 {
      margin: 2.75rem 0 1rem;
      color: var(--wl-navy);
      font-family: var(--wl-serif);
      font-size: clamp(1.0625rem, 2.2vw, 1.375rem);
      font-weight: 400;
      line-height: 1.3;
      letter-spacing: 0.01em;
    }

    #wm-legal h2:first-of-type {
      margin-top: 1.5rem;
    }

    #wm-legal h3 {
      margin: 1.9rem 0 0.75rem;
      color: var(--wl-blue);
      font-family: var(--wl-serif);
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.4;
    }

    #wm-legal .wl-note {
      margin: 0 0 1.05rem;
      color: var(--wl-navy);
      font-size: 0.875rem;
      font-weight: 600;
      line-height: 1.8;
    }

    #wm-legal ul {
      margin: 0 0 1.05rem;
      padding-left: 1.35rem;
    }

    #wm-legal li {
      margin: 0 0 0.5rem;
      font-size: 0.875rem;
      line-height: 1.8;
    }

    #wm-legal .wl-addr {
      margin: 0 0 1.35rem;
      padding: 0.9rem 1.15rem;
      border-left: 3px solid var(--wl-blue);
      background: var(--wl-band);
      color: var(--wl-navy);
      font-size: 0.8125rem;
      line-height: 1.85;
    }

    #wm-legal a {
      color: var(--wl-blue);
      text-decoration: underline;
      text-underline-offset: 0.15em;
    }

    #wm-legal a:hover,
    #wm-legal a:focus-visible {
      color: var(--wl-orange);
    }

    #wm-legal .wl-table-scroll {
      margin: 0 0 1.35rem;
      overflow-x: auto;
    }

    #wm-legal table {
      width: 100%;
      min-width: 34rem;
      border-collapse: collapse;
      font-size: 0.8125rem;
    }

    #wm-legal th,
    #wm-legal td {
      padding: 0.7rem 0.85rem;
      border: 1px solid var(--wl-line);
      text-align: left;
      line-height: 1.7;
      vertical-align: top;
    }

    #wm-legal th {
      color: var(--wl-navy);
      background: var(--wl-band);
      font-weight: 600;
    }

    @media print {
      #wm-global-header,
      #wm-global-footer {
        display: none !important;
      }

      #wm-legal {
        background: #ffffff;
      }

      #wm-legal .wl-doc {
        max-width: none;
        margin: 0;
        padding: 0;
        border: 0;
        box-shadow: none;
      }

      #wm-legal h2,
      #wm-legal h3 {
        break-after: avoid;
      }
    }
  </style>
"""

PAGE = u"""
<!--
==============================================================================
%(changelog)s
==============================================================================
-->

<div id="wm-legal" class="wm-legal">
%(style)s
  <section class="wl-band">
    <p class="wl-eyebrow">%(eyebrow)s</p>

    <h1 class="wl-title">%(title)s</h1>

    <hr class="wl-rule">
  </section>

  <article class="wl-doc">
%(dates)s
%(doc)s
  </article>
</div>
"""

# --------------------------------------------------------------------------
# Rich template: the standard WindowMotiv page design (hero, summary strip,
# sticky section nav, numbered policy cards, closing call to action).
#
# ponytail: _rich.css.html is the whole page stylesheet lifted from the
# affiliate directory so the two disclosure pages stay pixel-identical. It
# carries rules this page does not use; prune it only if the CSS is ever split
# into a shared file.
# --------------------------------------------------------------------------

RICH_EXTRA_CSS = u"""
    #wp-partners-page .wp-policy-intro {
      margin: 0 0 1.6rem;
      padding: 1.5rem 1.7rem;
      border: 1px solid var(--wp-line);
      border-left: 4px solid var(--wp-blue-600);
      border-radius: var(--wp-radius-sm);
      background: var(--wp-surface-blue);
    }

    #wp-partners-page .wp-policy-intro > :first-child {
      margin-top: 0;
    }

    #wp-partners-page .wp-policy-intro > :last-child {
      margin-bottom: 0;
    }

    #wp-partners-page .wp-policy-intro p {
      color: var(--wp-ink-800);
      font-size: 0.95rem;
      line-height: 1.75;
    }

    #wp-partners-page .wp-policy-card .wp-addr {
      margin: 0 0 1rem;
      padding: 0.9rem 1.15rem;
      border-left: 3px solid var(--wp-blue-600);
      border-radius: 0 var(--wp-radius-sm) var(--wp-radius-sm) 0;
      background: var(--wp-surface-soft);
      color: var(--wp-ink-900, var(--wp-ink-950));
      font-size: 0.9rem;
      line-height: 1.8;
    }

    #wp-partners-page .wp-policy-card .wp-note {
      margin: 0 0 1rem;
      color: var(--wp-navy-950);
      font-weight: 700;
    }
"""

HERO_ICONS = [
    u'<path d="M5 4v3M19 4v3M4 9h16M5 6h14v14H5V6Z" stroke="currentColor" stroke-width="1.8"></path>',
    u'<circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.8"></circle>'
    u'<path d="M12 9V4M12 20v-5M9 12H4M20 12h-5M9.8 9.8 6.4 6.4M17.6 17.6l-3.4-3.4'
    u'M14.2 9.8l3.4-3.4M6.4 17.6l3.4-3.4" stroke="currentColor" stroke-width="1.8" '
    u'stroke-linecap="round"></path>',
    u'<path d="M5 12.5 10 17l9-10" stroke="currentColor" stroke-width="2"></path>',
]

SUMMARY_ICONS = [
    u'<path d="M4 5h16v14H4V5Z" stroke="currentColor" stroke-width="1.8"></path>'
    u'<path d="M8 9h8M8 13h8M8 17h5" stroke="currentColor" stroke-width="1.8" '
    u'stroke-linecap="round"></path>',
    u'<circle cx="8" cy="8" r="3" stroke="currentColor" stroke-width="1.8"></circle>'
    u'<circle cx="16" cy="16" r="3" stroke="currentColor" stroke-width="1.8"></circle>'
    u'<path d="m10 10 4 4" stroke="currentColor" stroke-width="1.8"></path>',
    u'<path d="M12 3 5 6v5c0 4.8 2.9 8.8 7 10 4.1-1.2 7-5.2 7-10V6l-7-3Z" '
    u'stroke="currentColor" stroke-width="1.8"></path>',
]

RICH_SCRIPT = u"""  <script>
    (function () {
      "use strict";

      var root = document.getElementById("wp-partners-page");

      if (!root || root.dataset.wpPartnersInitialized === "true") {
        return;
      }

      root.dataset.wpPartnersInitialized = "true";

      var jumpMenu = root.querySelector("#wp-partners-jump");

      if (jumpMenu) {
        jumpMenu.addEventListener("change", function () {
          if (!jumpMenu.value) {
            return;
          }

          var target = root.querySelector("#" + jumpMenu.value);

          if (target) {
            target.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        });
      }

      var links = Array.prototype.slice.call(
        root.querySelectorAll(".wp-policy-nav__link")
      );

      links.forEach(function (link) {
        link.addEventListener("click", function (event) {
          var target = root.querySelector(link.getAttribute("href"));

          if (!target) {
            return;
          }

          event.preventDefault();
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        });
      });

      var printButton = root.querySelector("#wp-print-partners");

      if (printButton) {
        printButton.addEventListener("click", function () {
          window.print();
        });
      }

      if (!("IntersectionObserver" in window)) {
        return;
      }

      var visible = new Map();

      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              visible.set(entry.target.id, entry.intersectionRatio);
            } else {
              visible.delete(entry.target.id);
            }
          });

          var active = Array.from(visible.entries()).sort(function (a, b) {
            return b[1] - a[1];
          })[0];

          if (!active) {
            return;
          }

          links.forEach(function (link) {
            var isActive = link.getAttribute("href") === "#" + active[0];

            link.classList.toggle("is-active", isActive);

            if (isActive) {
              link.setAttribute("aria-current", "location");
            } else {
              link.removeAttribute("aria-current");
            }
          });
        },
        { rootMargin: "-16% 0px -68% 0px", threshold: [0.05, 0.2, 0.45, 0.7] }
      );

      root.querySelectorAll(".wp-policy-card").forEach(function (card) {
        observer.observe(card);
      });
    })();
  </script>
"""

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def inline(text):
    out = html.escape(text, quote=False)
    return LINK_RE.sub(
        lambda m: u'<a href="%s">%s</a>' % (m.group(2), m.group(1)), out
    )


def render(lines, css_prefix="wl"):
    body, buf, mode = [], [], [None]

    def flush():
        if not buf:
            return
        if mode[0] == "list":
            body.append(u"      <ul>")
            body.extend(u"        <li>%s</li>" % inline(x) for x in buf)
            body.append(u"      </ul>")
        elif mode[0] == "addr":
            joined = u"<br>\n        ".join(inline(x) for x in buf)
            body.append(u'      <p class="%s-addr">%s</p>' % (css_prefix, joined))
        del buf[:]

    for raw in lines:
        stripped = raw.strip()

        if not stripped:
            flush()
            mode[0] = None
            continue

        if stripped.startswith("- "):
            if mode[0] != "list":
                flush()
                mode[0] = "list"
            buf.append(stripped[2:].strip())
            continue

        if stripped.startswith("ADDR "):
            if mode[0] != "addr":
                flush()
                mode[0] = "addr"
            buf.append(stripped[5:].strip())
            continue

        flush()
        mode[0] = None

        # hero furniture belongs to the rich template only
        if stripped.split(" ", 1)[0] in ("META", "SUMMARY", "CTA"):
            continue

        if stripped.startswith("H2 "):
            # "H2 1. Title || Short nav label" - the label is for the rich
            # template's sidebar, so plain output keeps just the heading.
            heading = stripped[3:].split("||")[0].strip()
            body.append(u"      <h2>%s</h2>" % inline(heading))
        elif stripped.startswith("H3 "):
            body.append(u"      <h3>%s</h3>" % inline(stripped[3:].strip()))
        elif stripped.startswith("NOTE "):
            body.append(u'      <p class="%s-note">%s</p>'
                        % (css_prefix, inline(stripped[5:].strip())))
        elif stripped.startswith("RAW "):
            body.append(u"      " + stripped[4:])
        else:
            body.append(u"      <p>%s</p>" % inline(stripped))

    flush()
    return u"\n".join(body)


def slugify(text):
    return "wp-partners-" + re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]


def render_rich(lines, meta):
    """Render the source into the standard WindowMotiv page design."""
    chips, summaries, cta = [], [], None
    intro, cards = [], []

    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith("META "):
            chips.append(stripped[5:].strip())
        elif stripped.startswith("SUMMARY "):
            summaries.append([p.strip() for p in stripped[8:].split("||")])
        elif stripped.startswith("CTA "):
            cta = [p.strip() for p in stripped[4:].split("||")]
        elif stripped.startswith("H2 "):
            title, _, nav = stripped[3:].partition("||")
            cards.append({"title": title.strip(), "nav": (nav or title).strip(), "lines": []})
        elif cards:
            cards[-1]["lines"].append(raw)
        else:
            intro.append(raw)

    if not cards:
        raise SystemExit("rich template needs at least one H2 section")

    for index, card in enumerate(cards, start=1):
        card["id"] = slugify(card["nav"])
        card["number"] = u"%02d" % index

    out = []
    add = out.append

    # ---- hero ----
    add(u'  <main>\n    <section class="wp-hero" aria-labelledby="wp-partners-title">')
    add(u'      <div class="wp-hero__visual" aria-hidden="true">')
    add(u'        <div class="wp-hero__rings"></div>\n')
    add(u'        <div class="wp-hero__network">')
    add(u'          <svg viewBox="0 0 64 64" role="presentation" focusable="false">')
    add(u'            <path class="wp-network-line" d="M32 32 14 14M32 32 32 8M32 32 50 14'
        u'M32 32 10 36M32 32 54 36M32 32 17 53M32 32 47 53"></path>')
    for cx, cy, blue in ((14, 14, 0), (32, 8, 1), (50, 14, 0), (10, 36, 1),
                         (54, 36, 0), (17, 53, 0), (47, 53, 1)):
        add(u'            <circle class="wp-network-node%s" cx="%d" cy="%d" r="4.4"></circle>'
            % (u" wp-network-node--blue" if blue else u"", cx, cy))
    add(u'            <circle class="wp-network-center" cx="32" cy="32" r="7.5"></circle>')
    add(u'          </svg>\n        </div>\n      </div>\n')
    add(u'      <div class="wp-container wp-hero__inner">\n        <div class="wp-content-limit">')
    add(u'          <div class="wp-hero__content">')
    add(u'            <p class="wp-eyebrow">%s</p>\n' % inline(meta["eyebrow"]))
    add(u'            <h1 class="wp-heading" id="wp-partners-title">%s</h1>\n'
        % inline(meta["title"]))
    add(u'            <p class="wp-hero__lead">%s</p>\n' % inline(meta["lead"]))
    add(u'            <div class="wp-hero__meta">')
    for i, chip in enumerate(chips):
        add(u'              <span class="wp-hero__meta-item">')
        add(u'                <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">%s</svg>\n'
            % HERO_ICONS[i % len(HERO_ICONS)])
        add(u'                %s\n              </span>\n' % inline(chip))
    add(u'            </div>\n')
    add(u'            <div class="wp-hero__actions">')
    add(u'              <a class="wp-button wp-button--primary" href="#%s">Read the Disclosure</a>\n'
        % cards[0]["id"])
    add(u'              <button class="wp-button wp-button--outline" id="wp-print-partners"'
        u' type="button"\n                style="color:#ffffff;border-color:rgba(255,255,255,.34);'
        u'background:rgba(255,255,255,.08);">\n                Print This Disclosure'
        u'\n              </button>')
    add(u'            </div>\n          </div>\n        </div>\n      </div>\n    </section>\n')

    # ---- summary strip ----
    if summaries:
        add(u'    <section class="wp-summary-strip" aria-label="Disclosure summary">')
        add(u'      <div class="wp-container">')
        add(u'        <div class="wp-content-limit wp-summary-strip__inner">')
        for i, item in enumerate(summaries):
            add(u'          <article class="wp-summary-item">')
            add(u'            <span class="wp-summary-item__icon" aria-hidden="true">')
            add(u'              <svg viewBox="0 0 24 24" fill="none">%s</svg>'
                % SUMMARY_ICONS[i % len(SUMMARY_ICONS)])
            add(u'            </span>\n')
            add(u'            <div>\n              <strong>%s</strong>\n' % inline(item[0]))
            add(u'              <p>%s</p>\n            </div>' % inline(item[1]))
            add(u'          </article>\n')
        add(u'        </div>\n      </div>\n    </section>\n')

    # ---- sections ----
    add(u'    <section class="wp-section wp-section--soft">')
    add(u'      <div class="wp-container">\n        <div class="wp-content-limit">')
    add(u'          <div class="wp-mobile-policy-nav">')
    add(u'            <label for="wp-partners-jump">Jump to a disclosure section</label>\n')
    add(u'            <select id="wp-partners-jump">')
    add(u'              <option value="">Select a section</option>')
    for card in cards:
        add(u'              <option value="%s">%s</option>' % (card["id"], inline(card["title"])))
    add(u'            </select>\n          </div>\n')
    add(u'          <div class="wp-policy-layout">')
    add(u'            <nav class="wp-policy-nav" aria-label="Disclosure sections">')
    add(u'              <div class="wp-policy-nav__heading">Disclosure contents</div>\n')
    add(u'              <div class="wp-policy-nav__links">')
    for card in cards:
        add(u'                <a class="wp-policy-nav__link" href="#%s">%s</a>'
            % (card["id"], inline(card["nav"])))
    add(u'              </div>\n            </nav>\n')
    add(u'            <div class="wp-policy-content">')
    if any(line.strip() for line in intro):
        add(u'              <div class="wp-policy-intro">')
        add(render(intro, css_prefix="wp"))
        add(u'              </div>\n')
    for card in cards:
        add(u'              <article class="wp-policy-card" id="%s">' % card["id"])
        add(u'                <header class="wp-policy-card__header">')
        add(u'                  <span class="wp-policy-card__number">%s</span>' % card["number"])
        add(u'                  <h2>%s</h2>' % inline(card["title"]))
        add(u'                </header>\n')
        add(u'                <div class="wp-policy-card__body">')
        add(render(card["lines"], css_prefix="wp"))
        add(u'                </div>\n              </article>\n')
    add(u'            </div>\n          </div>\n        </div>\n      </div>\n    </section>\n')

    # ---- closing call to action ----
    if cta:
        add(u'    <section class="wp-final">\n      <div class="wp-container">')
        add(u'        <div class="wp-content-limit wp-final__inner">')
        add(u'          <div>\n            <h2>%s</h2>\n' % inline(cta[0]))
        add(u'            <p>%s</p>\n          </div>\n' % inline(cta[1]))
        add(u'          <a class="wp-button wp-button--primary" href="%s">%s</a>'
            % (cta[3], inline(cta[2])))
        add(u'        </div>\n      </div>\n    </section>')
    add(u'  </main>')

    return u"\n".join(out), len(cards)


def build_rich(meta, lines):
    css = io.open(os.path.join(HERE, "_rich.css.html"), encoding="utf-8").read()
    css = css.replace(u"  </style>", RICH_EXTRA_CSS + u"  </style>")
    doc, count = render_rich(lines, meta)
    page = u"""
<!--
==============================================================================
%(changelog)s
==============================================================================
-->

<div id="wp-partners-page" class="wp-partners-page">
%(css)s
%(doc)s

%(script)s</div>
""" % dict(meta, css=css, doc=doc, script=RICH_SCRIPT)
    return page, count


DATES = u"""    <p class="wl-dates">
      Effective Date: %(effective)s<br>
      Last Updated: %(updated)s
    </p>
"""

# Every Insure Motiv page is a real document (Window Motiv shipped bare fragments
# and rendered in quirks mode). The head carries the favicon set generated from
# assets/fav icon.png and a marked slot for the GA4 snippet.
DOCUMENT = u"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>%(title)s</title>
  <meta name="description" content="%(description)s">
  <meta name="robots" content="index, follow">
  <link rel="icon" href="assets/favicon.svg">
%(fonts)s
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-0TFCXJL0Z8"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-0TFCXJL0Z8');
  </script>
</head>
<body style="margin: 0; background: #FBF8F4;">
%(header)s
%(body)s
%(footer)s
</body>
</html>
"""


def wrap_document(title, description, body):
    """Wrap a page body in the shared header, footer, and document shell."""
    def part(name):
        return io.open(os.path.join(HERE, name), encoding="utf-8").read().rstrip("\n")

    return DOCUMENT % {
        "title": html.escape(title, quote=True),
        "description": html.escape(description, quote=True),
        "fonts": "  " + part("_fonts.html"),
        "header": part("_header.html"),
        "body": body.strip("\n"),
        "footer": part("_footer.html"),
    }


def build(src_path):
    lines = io.open(src_path, encoding="utf-8").read().split("\n")
    meta, start = {}, 0
    for i, line in enumerate(lines):
        if line.startswith(":"):
            key, _, value = line[1:].partition(" ")
            meta[key.strip()] = value.strip()
            start = i + 1
        elif line.strip():
            break

    for key in ("eyebrow", "title", "out", "changelog"):
        if key not in meta:
            raise SystemExit("%s: missing :%s" % (src_path, key))
    if "nodates" not in meta:
        for key in ("effective", "updated"):
            if key not in meta:
                raise SystemExit("%s: missing :%s (or set :nodates)" % (src_path, key))

    meta["changelog"] = meta["changelog"].replace("\\n", "\n")

    if meta.get("template") == "rich":
        page, sections = build_rich(meta, lines[start:])
    else:
        doc = render(lines[start:])
        dates = "" if "nodates" in meta else DATES % meta
        page = PAGE % dict(meta, style=STYLE, doc=doc, dates=dates)
        sections = doc.count("<h2>")

    out_path = os.path.join(ROOT, meta["out"])
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    page_title = meta.get("pagetitle") or (meta["title"].title() + " | Insure Motiv")
    io.open(out_path, "w", encoding="utf-8", newline="").write(
        wrap_document(page_title, meta.get("description", ""), page)
    )
    print("built %-42s %-6s %2d sections"
          % (meta["out"], meta.get("template", "plain"), sections))


def demo():
    """Self-check: directives round-trip into the expected markup."""
    out = render(
        [
            "H2 1. TEST",
            "",
            "A [link](/x) & an ampersand.",
            "",
            "- one",
            "- two",
            "",
            "ADDR Motiv Brands",
            "ADDR Cheyenne, WY",
            "",
            "NOTE READ THIS.",
            "H3 A. Sub",
        ]
    )
    assert "<h2>1. TEST</h2>" in out, out
    assert '<a href="/x">link</a>' in out and "&amp; an ampersand" in out, out
    assert "<ul>" in out and out.count("<li>") == 2, out
    assert 'class="wl-addr">Motiv Brands<br>' in out, out
    assert 'class="wl-note">READ THIS.' in out, out
    assert "<h3>A. Sub</h3>" in out, out
    print("gen.py self-check ok")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "--demo":
        demo()
    else:
        for arg in args:
            build(arg)
