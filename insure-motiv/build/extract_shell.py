# -*- coding: utf-8 -*-
"""Pull the Insure Motiv header and font faces out of index.html into build/.

The legal pages have to carry the same header and footer as the site, and
index.html is the only place they exist - this is a one-page site with inline
styles, not a component tree. Extracting rather than copying by hand means a
change to the site's header reaches the legal pages by re-running this and
gen.py.

Two edits are made on the way out:

  - The footer's dead #privacy and #terms anchors become real page links. They
    were anchors to nothing, because the pages did not exist.
  - The header's "Get Your Free Quote" button points at #quote, which is on the
    home page, so on a legal page it becomes /#quote.

The self-hosted @font-face block is extracted too, so the legal pages render in
Public Sans and Source Serif 4 like the rest of the site instead of falling
back to system fonts.

    python build/extract_shell.py
"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGE = os.path.join(ROOT, "index.html")

# Relative, so the pages work from disk and from any folder, not only when
# this folder is the web root.
LINKS = [
    ('href="#privacy"', 'href="privacy-policy.html"'),
    ('href="#terms"', 'href="terms-of-use.html"'),
    ('href="#quote"', 'href="index.html#quote"'),
]


def grab(s, tag, label):
    """Take the last top-level <tag>...</tag>, which is the site's own."""
    matches = list(re.finditer(r"^  <%s[ >][\s\S]*?^  </%s>\n" % (tag, tag), s, re.M))
    if not matches:
        raise SystemExit("could not find the %s in index.html" % label)
    out = matches[-1].group(0)
    print("  ok  %s: %d lines" % (label, out.count("\n")))
    return out


s = io.open(PAGE, encoding="utf-8").read()
header = grab(s, "header", "header")

fonts = re.search(r"<style>/\* vietnamese \*/[\s\S]*?</style>", s)
if not fonts:
    raise SystemExit("could not find the @font-face block in index.html")
io.open(os.path.join(HERE, "_fonts.html"), "w", encoding="utf-8", newline="").write(fonts.group(0))
print("  ok  _fonts.html: %d @font-face rules" % fonts.group(0).count("@font-face"))

# The footer is not extracted: build/fork_footer.py owns it.
for name, part in (("_header.html", header),):
    n = 0
    for old, new in LINKS:
        n += part.count(old)
        part = part.replace(old, new)
    io.open(os.path.join(HERE, name), "w", encoding="utf-8", newline="").write(part)
    print("  ok  wrote %s (%d link(s) repointed)" % (name, n))
