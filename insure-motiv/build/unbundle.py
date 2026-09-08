# -*- coding: utf-8 -*-
"""Unpack the self-extracting bundle into a normal static site.

The delivered index.html was a "bundled page": a full-screen navy placeholder
plus an "Unpacking..." badge, a 1.4 MB JSON manifest holding every image, font
and script as base64, and the real page as a JSON string. Nothing rendered
until JavaScript decoded ~926 KB of base64 and rebuilt the document, so the
visitor watched the placeholder first. That placeholder is the header flash the
client reported.

This writes the real document to index.html and each asset to assets/, so the
browser gets HTML on the first byte and fetches assets in parallel, cached
individually.

    python build/unbundle.py            # writes index.html + assets/
    python build/unbundle.py --check    # report only, writes nothing

The original is kept as bundled-original.html for reference.
"""
import base64, gzip, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SOURCE = os.path.join(ROOT, "bundled-original.html")
PAGE = os.path.join(ROOT, "index.html")
ASSETS = os.path.join(ROOT, "assets")
CHECK = "--check" in sys.argv

EXT = {"font/woff2": ".woff2", "font/woff": ".woff", "image/webp": ".webp",
       "image/png": ".png", "image/jpeg": ".jpg", "image/svg+xml": ".svg",
       "text/javascript": ".js", "application/javascript": ".js", "text/css": ".css"}

TITLE = "Final Expense Insurance Quotes | Insure Motiv"
DESCRIPTION = ("Compare final expense life insurance options and speak with a licensed "
               "agent. Insure Motiv connects consumers with participating insurance providers.")

# ---------------------------------------------------------------- read ----
if not os.path.isfile(SOURCE):
    if not os.path.isfile(PAGE):
        raise SystemExit("neither bundled-original.html nor index.html found")
    original = io.open(PAGE, encoding="utf-8").read()
    if '__bundler/manifest' not in original:
        raise SystemExit("index.html is not a bundle; nothing to unpack")
    if not CHECK:
        io.open(SOURCE, "w", encoding="utf-8", newline="").write(original)
        print("kept the original as bundled-original.html")
else:
    original = io.open(SOURCE, encoding="utf-8").read()


def payload(kind):
    m = re.search(r'<script type="__bundler/%s">\n(.*?)\n\s*</script>' % kind, original, re.S)
    if not m:
        raise SystemExit("could not find the %s payload" % kind)
    return json.loads(m.group(1))


manifest = payload("manifest")
template = payload("template")

# ------------------------------------------------------------- decode ----
decoded, dead = {}, []
for uid, asset in manifest.items():
    raw = base64.b64decode(asset["data"])
    if asset["compressed"]:
        raw = gzip.decompress(raw)
    decoded[uid] = raw

# A uuid counts as live if the template names it, or another live asset does.
live = {u for u in decoded if u in template}
changed = True
while changed:
    changed = False
    for uid, blob in decoded.items():
        if uid in live:
            continue
        text = blob.decode("utf-8", "ignore") if manifest[uid]["mime"].endswith(("javascript", "css")) else ""
        if any(other in text for other in live) or any(uid in decoded[o].decode("utf-8", "ignore")
                                                       for o in live
                                                       if manifest[o]["mime"].endswith(("javascript", "css"))):
            live.add(uid)
            changed = True
dead = [u for u in decoded if u not in live]

names = {uid: uid.split("-")[0] + EXT.get(manifest[uid]["mime"], "") for uid in decoded}

print("bundle holds %d assets (%.0f KB decoded)" % (len(decoded), sum(len(b) for b in decoded.values()) / 1024))
for uid in sorted(live, key=lambda u: -len(decoded[u])):
    print("   keep  %-14s %-16s %7.1f KB" % (names[uid], manifest[uid]["mime"], len(decoded[uid]) / 1024))
for uid in dead:
    print("   DROP  %-14s %-16s %7.1f KB  (referenced nowhere)"
          % (names[uid], manifest[uid]["mime"], len(decoded[uid]) / 1024))

# ------------------------------------------------------------ rewrite ----
html = template
for uid in live:
    html = html.replace(uid, "/assets/" + names[uid])

# Fonts are self-hosted now, so preconnecting to Google's font hosts only costs
# two DNS + TLS handshakes that are never used.
html, n_pre = re.subn(r'\s*<link rel="preconnect" href="https://fonts\.g[^"]*"[^>]*>', "", html)

# <helmet> is moved into <head> by the runtime, which means the @font-face
# rules are only discovered after a 69 KB script has parsed and executed.
# Hoisting them at build time lets the browser start the font fetch during the
# initial HTML parse. The <helmet> element stays for the runtime to process.
fonts = re.search(r"<helmet>\s*(<style>[\s\S]*?</style>)", html)
hoisted = ""
if fonts:
    first = "/assets/" + names[next(u for u in live if manifest[u]["mime"] == "font/woff2")]
    hoisted = ("\n" + fonts.group(1)
               + '\n<link rel="preload" href="%s" as="font" type="font/woff2" crossorigin>' % first)

head_extra = (
    '\n<title>%s</title>'
    '\n<meta name="description" content="%s">'
    '\n<meta name="robots" content="index, follow">%s\n'
) % (TITLE, DESCRIPTION, hoisted)

html = html.replace("</head>", head_extra + "</head>", 1)

if CHECK:
    print("\n--check: nothing written")
    raise SystemExit(0)

# -------------------------------------------------------------- write ----
if not os.path.isdir(ASSETS):
    os.makedirs(ASSETS)
for uid in live:
    io.open(os.path.join(ASSETS, names[uid]), "wb").write(decoded[uid])
io.open(PAGE, "w", encoding="utf-8", newline="").write(html)

before = len(original.encode("utf-8"))
after = len(html.encode("utf-8"))
print("\nindex.html  %.0f KB -> %.0f KB   (%d assets in assets/)"
      % (before / 1024, after / 1024, len(live)))
print("dropped %d unreferenced script(s), %.0f KB decoded"
      % (len(dead), sum(len(decoded[u]) for u in dead) / 1024))
print("removed %d dead font-host preconnect(s)" % n_pre)
