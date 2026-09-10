# -*- coding: utf-8 -*-
"""The :changelog metadata line for each generated legal page.

Kept out of adapt_sources.py because it is prose about this site, not a
find-and-replace rule. gen.py emits it as the HTML comment at the top of the
generated page.

The line is physically one line with literal backslash-n escapes; gen.py turns
those into real newlines. A real newline here would end the metadata line and
the remainder would render as page copy.
"""

_PRIVACY = [
    "PRIVACY POLICY - INSURE MOTIV",
    "VERSION: V1.0.0",
    "EFFECTIVE DATE: 2026-09-10",
    "LAST UPDATED: 2026-09-10",
    "",
    "CHANGE LOG",
    "-" * 78,
    "V1.0.0 | 2026-09-10",
    "- First Privacy Policy for Insure Motiv. The site previously had none; the",
    "  footer linked a dead #privacy anchor.",
    "- Adopted the 22-section Motiv plain-document Privacy Policy already used by",
    "  Window Motiv and PestMotiv, in the same order, reworded for final expense",
    "  life insurance.",
    "- Replaced the property and project sections with coverage and eligibility",
    "  sections; the collected-data table now lists what the live form asks for.",
    "- States that Insure Motiv does not collect health information through its",
    "  lead forms, and that a licensed agent or carrier may ask separately under",
    "  their own privacy practices.",
    "- Uses the Insure Motiv navy and teal palette.",
]

_TERMS = [
    "TERMS OF USE - INSURE MOTIV",
    "VERSION: V1.0.0",
    "EFFECTIVE DATE: 2026-09-10",
    "LAST UPDATED: 2026-09-10",
    "",
    "CHANGE LOG",
    "-" * 78,
    "V1.0.0 | 2026-09-10",
    "- First Terms of Use for Insure Motiv. The site previously had none; the",
    "  footer linked a dead #terms anchor.",
    "- Adopted the 33-section Motiv plain-document Terms of Use already used by",
    "  Window Motiv and PestMotiv, in the same order, reworded for final expense",
    "  life insurance.",
    "- Replaced the contractor and home-improvement sections with insurance ones:",
    "  not a carrier, insurer, agency, or licensed producer; not affiliated with",
    "  Medicare, Medicaid, the SSA, or any state insurance department; coverage,",
    "  rates, and eligibility decided solely by the carrier's underwriting.",
    "- Uses the Insure Motiv navy and teal palette.",
]



_ENTITY_NOTE = [
    "",
    "ENTITY - NEEDS CLIENT CONFIRMATION",
    "-" * 78,
    "index.html never names a legal entity for Insure Motiv. This document",
    "follows the PestMotiv pattern: a DBA of Leads Motiv, LLC, a subsidiary of",
    "Motiv Brands, Inc. Confirm before publication; change ENTITY in",
    "build/adapt_sources.py and re-run if it differs.",
    "",
    "SOURCE OF TRUTH",
    "-" * 78,
    "Edit build/src/<name>.txt and run:  python build/gen.py build/src/*.txt",
    "Do not hand-edit the generated file.",
    "",
    "IMPORTANT LEGAL REVIEW",
    "-" * 78,
    "Insurance is a regulated vertical and this document must be reviewed and",
    "approved by qualified legal counsel before publication, including the state",
    "privacy rights, California, sale/sharing, data-retention, arbitration, and",
    "insurance-disclaimer sections.",
]

CHANGELOG = {
    "privacy-policy": "\\n".join(_PRIVACY + _ENTITY_NOTE),
    "terms-of-use": "\\n".join(_TERMS + _ENTITY_NOTE),
}
