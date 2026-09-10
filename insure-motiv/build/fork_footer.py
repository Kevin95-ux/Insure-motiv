# -*- coding: utf-8 -*-
"""Fork the Window Motiv global footer into the Insure Motiv one.

Reads ../../motiv/build/_footer.html, writes ./_footer.html.

Same layout as Window Motiv and PestMotiv, which is the point of forking rather
than restyling what the bundle shipped: a primary band with the brand on the
left and the call to action on the right, then a secondary band carrying the
disclosure with the copyright and legal links side by side beneath it.

Insure Motiv differences, each forced by something real:

  - Palette is the site's navy and teal; type is Public Sans and Source Serif 4,
    the two faces this site self-hosts, not Inter.
  - The brand mark is the "IM" tile from the header, not Window Motiv's window
    glyph.
  - The call to action is a link to the quote form, so Window Motiv's survey
    button and the ~300 lines of modal-opening JavaScript behind it go. Insure
    Motiv has no survey modal for it to open.
  - The legal row is Privacy Policy and Terms of Use. Window Motiv's third link
    is Marketing Partners; this site has no such page.
  - The insurance and TCPA paragraph from the bundle sits under the logo and
    name, in the primary band, per the client. It carries the carrier, Medicare
    and Do Not Call language the house disclosure does not cover.

    python build/fork_footer.py
"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "motiv", "build", "_footer.html")
OUT = os.path.join(HERE, "_footer.html")

TAGLINE = "Final expense coverage"
PHONE = "(800) 555-0123"
TEL = "tel:18005550123"

s = io.open(SRC, encoding="utf-8").read()


def sub(pattern, repl, count, label, flags=0):
    global s
    found = len(re.findall(pattern, s, flags))
    if found != count:
        raise SystemExit("%s: expected %d match(es), found %d" % (label, count, found))
    s = re.sub(pattern, repl.replace("\\", "\\\\"), s, count=count, flags=flags)
    print("  ok  %s" % label)


# 1. palette: the site's navy ground, teal accents ---------------------------
sub(r"--wmf-navy-1100:[\s\S]*?--wmf-focus:[^;]*;", """--wmf-navy-1100: #0b2340;
      --wmf-navy-1050: #0e2a4a;
      --wmf-navy-1000: #12304F;
      --wmf-navy-950: #1a3d61;
      --wmf-blue-700: #0A574E;
      --wmf-blue-600: #A8D8CF;
      --wmf-blue-100: #dcefe9;
      --wmf-orange-700: #0A574E;
      --wmf-orange-600: #0D6E63;
      --wmf-orange-500: #12857a;
      --wmf-white: #ffffff;
      --wmf-text: #dfe8ef;
      --wmf-muted: #a8b8c4;
      --wmf-line: rgba(255, 255, 255, 0.16);
      --wmf-focus: 0 0 0 4px rgba(168, 216, 207, 0.35);""", 1, "palette")

sub(r"background:\s*radial-gradient\(circle at 95% 0,[\s\S]*?var\(--wmf-navy-1100\)\);",
    """background:
        radial-gradient(circle at 95% 0,
          rgba(13, 110, 99, 0.20),
          transparent 32%),
        linear-gradient(145deg,
          var(--wmf-navy-1000),
          var(--wmf-navy-1100));""", 1, "footer gradient")

sub(r"font-family:\n        Inter,\n        Arial,\n        Helvetica,\n        sans-serif;",
    """font-family:
        "Public Sans",
        Arial,
        Helvetica,
        sans-serif;""", 1, "body font -> Public Sans")

# 2. brand: the header's IM tile, wordmark in the site serif ------------------
sub(r'<span class="wmf-logo" aria-hidden="true">[\s\S]*?</span>\s*<span class="wmf-brand-copy">',
    '<span class="wmf-logo wmf-logo--mark" aria-hidden="true">IM</span>\n\n'
    '          <span class="wmf-brand-copy">', 1, "brand mark -> IM tile")
sub(r'<span class="wmf-brand-name">\s*Window<strong>Motiv</strong>\s*</span>',
    '<span class="wmf-brand-name">\n              Insure<strong> Motiv</strong>\n            </span>',
    1, "brand name")
sub(r'<span class="wmf-brand-tagline">\s*Smarter window project matching\s*</span>',
    '<span class="wmf-brand-tagline">\n              %s\n            </span>' % TAGLINE, 1, "tagline")
sub(r'aria-label="WindowMotiv home"', 'aria-label="Insure Motiv home"', 1, "brand aria-label")
sub(r'href="/" data-wmf-nav-link', 'href="index.html" data-wmf-nav-link', 1, "brand link")

# 3. call to action: a link to the form, and the phone beside it -------------
# Window Motiv's button opens a survey modal through a long JS bridge. There is
# no modal here - the form is a section on the home page - so the button becomes
# an anchor and the bridge goes with it.
sub(r'<button class="wmf-survey-button"[\s\S]*?</button>',
    '''<div class="wmf-cta-group">
          <a class="wmf-phone" href="%s">
            <span class="wmf-phone-label">Talk to a licensed agent</span>
            <span class="wmf-phone-number">%s</span>
          </a>

          <a class="wmf-survey-button" href="index.html#quote"
            data-cta-page="global-footer" data-cta-section="compact-footer"
            data-cta-name="get-your-free-quote">
            Get Your Free Quote

            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M5 12h14M14 7l5 5-5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                stroke-linejoin="round"></path>
            </svg>
          </a>
        </div>''' % (TEL, PHONE), 1, "CTA -> quote link + phone")

# 4. the house disclosure, alone in the secondary band as on Window Motiv ----
# .wmf-secondary-inner is "minmax(0, 1fr) auto": the disclosure on the left,
# copyright and legal links on the right. A third child would break that row.
sub(r'<p class="wmf-disclosure">[\s\S]*?</p>', """<p class="wmf-disclosure">
          <strong>Insure Motiv disclosure:</strong>
          Insure Motiv is a DBA of Leads Motiv, LLC. Insure Motiv connects
          consumers with participating licensed insurance agents and carriers.
          By submitting a request, you agree to our
          <a href="terms-of-use.html" data-wmf-nav-link>Terms of Use</a> and
          acknowledge our
          <a href="privacy-policy.html" data-wmf-nav-link>Privacy Policy</a>.
          Your information may be shared with participating providers and
          marketing partners as described in our Privacy Policy.
        </p>""", 1, "house disclosure")

# 4b. the insurance and TCPA paragraph sits under the logo and name --------
# Client's placement. It carries the carrier, Medicare and Do Not Call language
# the house disclosure does not cover, and it reads as the brand's own
# statement, so it belongs with the brand rather than in the legal row.
brand = re.search(r'(<a class="wmf-brand-link"[\s\S]*?</a>)\n\n(\s*)(<div class="wmf-cta-group">)', s)
if not brand:
    raise SystemExit("could not find the brand link to wrap")
s = s[:brand.start()] + (
    '<div class="wmf-brand-block">\n          '
    + brand.group(1).replace("\n", "\n  ")
    + """

          <p class="wmf-brand-disclosure">
            Insure Motiv is not an insurance carrier. Insure Motiv is a marketing
            service that helps connect consumers with licensed insurance agents
            and providers. Coverage, rates, eligibility, and availability vary by
            provider, state, age, and health. Insure Motiv is not affiliated with
            Medicare, Social Security, or any government agency. By submitting
            your information, you agree to be contacted by Insure Motiv, including
            by phone, text, or AI-generated voice message, using the contact
            information provided, even if your number is on a Do Not Call list.
            Consent is not a condition of purchase. Message and data rates may
            apply. See our
            <a href="privacy-policy.html" data-wmf-nav-link>Privacy Policy</a> and
            <a href="terms-of-use.html" data-wmf-nav-link>Terms of Use</a> for
            more information.
          </p>
        </div>

"""
    + brand.group(2) + brand.group(3)) + s[brand.end():]
print("  ok  insurance/TCPA paragraph under the brand")

# 5. legal row: no Marketing Partners page on this site ----------------------
sub(r'<a class="wmf-legal-link" href="/disclosures/marketing-partners" data-wmf-nav-link>\s*Marketing Partners\s*</a>\s*',
    "", 1, "drop the Marketing Partners link")
sub(r'href="/privacy-policy"', 'href="privacy-policy.html"', 1, "legal link: privacy")
sub(r'href="/terms-of-use"', 'href="terms-of-use.html"', 1, "legal link: terms")
sub(r'aria-label="WindowMotiv legal links"', 'aria-label="Insure Motiv legal links"', 1, "legal nav label")

# 6. the survey bridge, now that nothing triggers it -------------------------
for name, pattern in (
    ("getSurveyDetail", r"      function getSurveyDetail\(trigger\) \{[\s\S]*?\n      \}\n\n"),
    ("trySurveyFunction", r"      function trySurveyFunction\(detail\) \{[\s\S]*?\n      \}\n\n"),
    ("dispatchSurveyEvent", r"      function dispatchSurveyEvent\(detail\) \{[\s\S]*?\n      \}\n\n"),
    ("tryExistingSurveyTrigger", r"      function tryExistingSurveyTrigger\(\) \{[\s\S]*?\n      \}\n\n"),
    ("buildFallbackUrl", r"      function buildFallbackUrl\(detail\) \{[\s\S]*?\n      \}\n\n"),
    ("openSurvey", r"      function openSurvey\(trigger\) \{[\s\S]*?\n      \}\n\n"),
    ("initializeSurveyTrigger", r"      function initializeSurveyTrigger\(\) \{[\s\S]*?\n      \}\n\n"),
):
    sub(pattern, "", 1, "drop %s()" % name)
sub(r"\n      initializeSurveyTrigger\(\);", "", 1, "drop the survey init call")
sub(r",\n\n        surveyEvent:\n          \"windowmotiv:open-survey\"", "", 1, "drop the survey event name")

# 7. styles the fork needs --------------------------------------------------
sub(r"\n  </style>", """
    /* The header's brand tile, reversed for the navy ground. The base
       .wmf-logo is sized for an SVG; this one holds two letters. */
    #wm-global-footer .wmf-logo--mark {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 44px;
      height: 44px;
      border-radius: 13px;
      background: var(--wmf-white);
      color: var(--wmf-navy-1000);
      font-family: "Source Serif 4", Georgia, serif;
      font-size: 19px;
      font-weight: 700;
      letter-spacing: -0.3px;
    }

    #wm-global-footer .wmf-logo--mark::after {
      display: none;
    }

    #wm-global-footer .wmf-brand-name {
      font-family: "Source Serif 4", Georgia, serif;
      font-size: 22px;
      letter-spacing: -0.4px;
    }

    /* The phone sits beside the CTA, as it does in the header. */
    #wm-global-footer .wmf-cta-group {
      display: flex;
      align-items: center;
      gap: clamp(14px, 3vw, 26px);
      flex-wrap: wrap;
    }

    #wm-global-footer .wmf-phone {
      display: flex;
      flex-direction: column;
      line-height: 1.2;
    }

    #wm-global-footer .wmf-phone-label {
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.7px;
      text-transform: uppercase;
      color: var(--wmf-muted);
    }

    #wm-global-footer .wmf-phone-number {
      font-size: 20px;
      font-weight: 700;
      color: var(--wmf-white);
    }

    #wm-global-footer .wmf-brand-block {
      display: flex;
      flex-direction: column;
      gap: 18px;
      min-width: 0;
    }

    /* The left column is tall now, so the CTA sits level with the logo row
       instead of floating at its vertical centre. */
    #wm-global-footer .wmf-primary-inner {
      align-items: start;
    }

    #wm-global-footer .wmf-brand-disclosure {
      margin: 0;
      /* No width cap: the brand column is the 1fr of "minmax(0, 1fr) auto", so
         the paragraph runs to where the call to action begins. Capping it left
         a wide empty gap. */
      color: var(--wmf-muted);
      font-size: 12.5px;
      line-height: 1.75;
    }

    #wm-global-footer .wmf-brand-disclosure a {
      color: var(--wmf-white);
      text-decoration: underline;
      text-underline-offset: 0.15em;
    }

    #wm-global-footer .wmf-disclosure a {
      color: var(--wmf-white);
      text-decoration: underline;
      text-underline-offset: 0.15em;
    }

    @media (max-width: 60rem) {
      #wm-global-footer .wmf-cta-group {
        width: 100%;
        justify-content: space-between;
      }
    }
  </style>""", 1, "fork styles")

# 8. remaining brand strings ------------------------------------------------
# The brand accent is hardcoded to Window Motiv's orange, not a palette token.
sub(r"color: #ffab7b;", "color: var(--wmf-blue-600);", 1, "brand accent -> teal")

sub(r'data-wmf-version="V1\.1\.0"', 'data-wmf-version="IM-V1.0.0"', 1, "version attribute")
s = s.replace('"V1.1.0"', '"IM-V1.0.0"')
s = s.replace("WindowMotiv", "Insure Motiv").replace("windowmotiv", "insuremotiv")
s = s.replace("Window Motiv", "Insure Motiv")
s = s.replace('homeUrl:\n          "/",', 'homeUrl:\n          "index.html",')

io.open(OUT, "w", encoding="utf-8", newline="").write(s)
print("wrote %s (%d lines)" % (os.path.relpath(OUT, HERE), s.count("\n")))

left = [(i + 1, l.strip()[:100]) for i, l in enumerate(s.split("\n"))
        if re.search(r"window|survey|marketing-partners|Inter,", l, re.I)]
if left:
    print("REVIEW - lines still mentioning Window Motiv things:")
    for n, l in left:
        print("   %5d  %s" % (n, l))
