# -*- coding: utf-8 -*-
"""Reserve the space the embedded quote form needs, and fill it while it loads.

Two problems, one cause. Both GoHighLevel iframes declare min-height: 652px,
but the embed's resizer grows them to their real height once the form reports
back - 1027px on desktop, 1187px at 390px wide. So the hero card jumped ~375px
after load: the whole of the measured CLS, 0.1495.

Reserving the settled height removes the jump but leaves a tall blank card,
because the resizer also keeps the iframe hidden until the form reports. So
each iframe gets a skeleton - field-shaped bars with a shimmer sweep - painted
underneath it. No load handshake is needed: the skeleton is simply covered
when the resizer reveals the iframe over it. An onload attribute would not
survive anyway; the embed strips it and re-parents the iframe.

Run after build/unbundle.py:

    python build/unbundle.py && python build/fix_cls.py
"""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "index.html")
s = io.open(PAGE, encoding="utf-8").read()

if "im-form-shell" in s:
    raise SystemExit("index.html already reserves the form height")

MOBILE, DESKTOP = 1187, 1027
IDS = ["inline-h5FNem45vE6b3op3S8TN", "inline-h5FNem45vE6b3op3S8TN-2"]

for i, fid in enumerate(IDS, 1):
    m = re.search(r'<iframe[^>]*\bid="%s"[^>]*></iframe>' % re.escape(fid), s)
    if not m:
        raise SystemExit("iframe %s not found" % fid)
    tag = m.group(0)

    # Sizing moves to the stylesheet so the reserve can be responsive; an
    # inline style attribute cannot hold a media query.
    style_attr = re.search(r'style="[^"]*"', tag).group(0)
    style = re.sub(r"\s*(?:min-)?height:\s*[^;]+;", "", style_attr[7:-1]).strip()
    tag_new = tag.replace(style_attr, 'style="%s"' % style)

    # No loading="lazy" on the footer copy, tempting as it is: the embed's
    # resizer hides the iframe at init and reveals it when the form posts its
    # height. Deferring the load misses that handshake and the iframe stays
    # visibility:hidden forever, leaving the skeleton up for good.

    s = s[:m.start()] + ('<div class="im-form-shell">'
                         '<div class="im-form-skeleton" aria-hidden="true"></div>'
                         '%s</div>') % tag_new + s[m.end():]
    print("  ok  iframe %d: reserve + skeleton" % i)

SEL = ",\n".join("#" + i for i in IDS)
SHELL = """<style id="im-form-shell-css">
/* The GoHighLevel embed reports its height after load and its resizer then
   sets it inline. Reserving the settled height up front stops the card
   growing ~375px once the form arrives - this was the page's entire CLS.
   Measured on the live form: %(desktop)dpx at >=768px, %(mobile)dpx at 390px. */
.im-form-shell {
  position: relative;
  min-height: %(mobile)dpx;
}

%(sel)s {
  min-height: %(mobile)dpx;
}

@media (min-width: 768px) {
  .im-form-shell {
    min-height: %(desktop)dpx;
  }

%(sel_i)s {
    min-height: %(desktop)dpx;
  }
}

/* Held space with nothing in it reads as a broken card, so the reserve is
   filled with the shape of the form until the real one paints over it.
   The embed hides its iframe until the form reports back, so the skeleton
   needs no "loaded" signal - it is simply covered when the iframe appears. */
.im-form-skeleton {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  border-radius: 12px;
  padding: 22px 0;
  /* One label + one field, tiled down the full reserve, so the placeholder
     fills the height instead of leaving dead space under a few bars.
     background-origin keeps the tiling inside the padding. */
  background-image:
    linear-gradient(#ECE7DF 0 13px, transparent 13px),
    linear-gradient(transparent 0 25px, #F4F1EB 25px 71px, transparent 71px);
  background-size: 38%% 99px, 100%% 99px;
  background-repeat: repeat-y;
  background-origin: content-box;
  background-color: #FFFFFF;
}

/* The iframe is what covers the skeleton, so it has to win the stack and be
   opaque. The resizer sets position: relative itself; this adds the layer.
   The background matters: the GoHighLevel form is transparent, and the footer
   copy shipped without one, so the skeleton bars showed through the loaded
   fields. Both cards behind these iframes are white, so white is what the
   form already renders on - this changes nothing once loaded. */
%(sel_r)s {
  position: relative;
  z-index: 1;
  background: #FFFFFF;
}

.im-form-skeleton::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(100deg,
    transparent 20%%, rgba(255, 255, 255, 0.75) 50%%, transparent 80%%);
  transform: translateX(-100%%);
  /* Bounded: the skeleton stays in the DOM under the loaded form, and an
     infinite animation there would repaint for the life of the page. */
  animation: im-form-shimmer 1.4s ease-in-out 10;
}

@keyframes im-form-shimmer {
  to { transform: translateX(100%%); }
}

@media (prefers-reduced-motion: reduce) {
  .im-form-skeleton::after { animation: none; }
}
</style>
""" % {"mobile": MOBILE, "desktop": DESKTOP, "sel": SEL,
       "sel_i": ",\n".join("  #" + i for i in IDS), "sel_r": SEL}

if s.count("</head>") != 1:
    raise SystemExit("expected exactly one </head>")
s = s.replace("</head>", SHELL + "</head>", 1)
print("  ok  reserve + skeleton stylesheet")

io.open(PAGE, "w", encoding="utf-8", newline="").write(s)
print("index.html updated: %dpx mobile / %dpx desktop reserved" % (MOBILE, DESKTOP))
