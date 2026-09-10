# -*- coding: utf-8 -*-
"""Turn the Window Motiv legal sources into Insure Motiv ones.

Same documents as Window Motiv - the 22-section Motiv privacy policy and the
33-section terms of use, in the same order - with the brand names swapped and
the vertical wording rewritten. A final-expense insurance site cannot promise
"window replacement services", and insurance carries disclaimers the home
improvement vertical does not: not a carrier, not affiliated with Medicare or
any government agency, coverage decided by the carrier's underwriting.

The vertical wording follows what index.html already tells visitors, so the
legal pages and the site cannot drift apart.

ENTITY - NEEDS CLIENT CONFIRMATION
    index.html never names a legal entity for Insure Motiv, so this follows the
    PestMotiv pattern: a DBA of Leads Motiv, LLC, a subsidiary of Motiv Brands,
    Inc. If Insure Motiv sits under a different entity, change ENTITY below and
    re-run; nothing else needs touching.

Run once on freshly copied build/src/*.txt. Every block rewrite asserts it
matched; anything Window-specific that survives is printed at the end so it can
be fixed by hand.
"""
import io, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _changelog import CHANGELOG  # noqa: E402

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
TODAY = "September 10, 2026"
ISO = "2026-09-10"
ENTITY = "Leads Motiv, LLC"

# ---- phrase substitutions, longest and most specific first ---------------
PHRASES = [
    ("Motiv Brands Group, LLC, Motiv Brands, Inc., Leads Motiv, LLC, and their controlled",
     "Motiv Brands, Inc., Leads Motiv, LLC, and their controlled"),

    # The marketing-partners source words the entity differently. Left alone it
    # would say Motiv Brands Group, LLC on one page and Leads Motiv, LLC on the
    # other two - the same brand with two parents.
    ("Window Motiv is a consumer-facing marketing brand and DBA owned by Motiv Brands Group, LLC, "
     "a holding company that owns, holds, administers, or supports consumer-facing marketing "
     "brands used for lead generation and related services.",
     "Insure Motiv is a consumer-facing marketing brand and DBA of %s, a subsidiary of Motiv "
     "Brands, Inc. Leads Motiv, LLC is the entity through which Motiv's consumer-facing marketing "
     "brands are used for lead generation and related services." % ENTITY),
    ("Window Motiv is a consumer-facing marketing brand and DBA owned by Motiv Brands Group, LLC, "
     "and is not necessarily a separate legal entity.",
     "Insure Motiv is a consumer-facing marketing brand and DBA of %s, and is not a separate "
     "legal entity." % ENTITY),
    ("the request may be processed by Motiv Brands Group, LLC, Leads Motiv, LLC, Motiv Brands, Inc.",
     "the request may be processed by Leads Motiv, LLC, Motiv Brands, Inc."),
    ("- Motiv Brands Group, LLC;\n\n- Leads Motiv, LLC;", "- Leads Motiv, LLC;"),
    ("Window Motiv is a consumer-facing marketing brand and DBA of Motiv Brands Group, LLC.",
     "Insure Motiv is a consumer-facing marketing brand and DBA of %s, a subsidiary of "
     "Motiv Brands, Inc." % ENTITY),
    ("Window Motiv, Motiv Brands Group, LLC, Motiv Brands, Inc., Leads Motiv, LLC, and their affiliates",
     "Insure Motiv, Leads Motiv, LLC, Motiv Brands, Inc., and their affiliates"),
    ("including Motiv Brands Group, LLC, Motiv Brands, Inc., Leads Motiv, LLC, controlled subsidiaries",
     "including Motiv Brands, Inc., Leads Motiv, LLC, controlled subsidiaries"),

    # what the service is about
    ("window replacement, window installation, or related home-improvement services",
     "final expense life insurance and related insurance products"),
    ("window replacement, window installation, or closely related home-improvement services",
     "final expense life insurance and closely related insurance products"),
    ("window replacement, window installation, home-improvement, or remodeling providers",
     "licensed insurance agents, agencies, or carriers"),
    ("window replacement, window installation, remodeling, contractor, or home-improvement provider",
     "licensed insurance agent, agency, or carrier"),
    ("provide or arrange window replacement, window installation, or related home-improvement services",
     "provide, arrange, sell, or underwrite insurance coverage"),
    ("window replacement, window installation, and related home-improvement services",
     "final expense life insurance and related insurance products"),
    ("the consumer's window replacement or installation request", "the consumer's insurance inquiry"),
    ("window replacement or home-improvement inquiry", "insurance inquiry"),
    ("window replacement and home-improvement providers", "licensed insurance agents and carriers"),
    ("window replacement or home-improvement provider", "licensed insurance agent or carrier"),
    ("window replacement or home-improvement services", "insurance products or coverage"),
    ("participating window replacement and home-improvement providers",
     "participating licensed insurance agents, agencies, and carriers"),
    ("window or home-improvement service", "insurance product"),
    ("window or home-improvement provider", "licensed insurance agent or carrier"),
    ("window and home-improvement providers", "licensed insurance agents and carriers"),

    # what the provider list looks like
    ("window replacement; window and door installation; remodeling and general contracting; "
     "siding, roofing, and exterior home-improvement services; home-improvement financing",
     "final expense and burial insurance; whole and term life insurance; guaranteed-issue and "
     "simplified-issue life policies; supplemental insurance products; annuities and related "
     "retirement products"),

    # what the form actually asks for
    ("the window or home-improvement project you are considering", "the coverage you are considering"),
    ("property, project, or homeownership questionnaire responses",
     "coverage or eligibility questionnaire responses"),
    ("property and project information", "coverage and eligibility information"),
    ("Property and project information", "Coverage and eligibility information"),
    ("PROPERTY AND PROJECT INFORMATION", "COVERAGE AND ELIGIBILITY INFORMATION"),
    ("Certain Window Motiv Services request information regarding your property, your homeownership "
     "status, and the window or home-improvement project you are considering.",
     "Certain Insure Motiv Services request information regarding your age, your state of residence, "
     "and the coverage you are considering."),
    ("Property address and ZIP code are used to determine service-area coverage and provider "
     "availability. We do not use your property address to derive precise device geolocation.",
     "State and ZIP code are used to determine where a product is available and which agents are "
     "licensed in your state. We do not use your address to derive precise device geolocation."),

    # what can go wrong, and who decides
    ("workmanship or installation quality; property damage caused by a provider",
     "coverage decisions; underwriting outcomes; claim handling by a carrier"),
    ("Final eligibility, pricing, measurement, product availability, installation scheduling, "
     "warranty terms, financing approval, and other decisions",
     "Final eligibility, premium, underwriting outcome, product availability, policy issuance, "
     "policy terms, and other decisions"),
    ("any energy savings will be achieved; ", "any coverage will be issued; "),
    ("engineering, architectural, or construction advice; energy-efficiency certification;",
     "insurance, tax, legal, or financial advice; a recommendation of any particular policy;"),
    ("Submitting information through Window Motiv is not the same as applying for a rebate, tax "
     "credit, utility incentive, financing product, or home-improvement contract.",
     "Submitting information through Insure Motiv is not the same as applying for insurance, "
     "being approved for coverage, or being issued a policy."),
    ("Any qualification indication provided through Window Motiv is preliminary and is not a "
     "binding quote, estimate, price, or approval.",
     "Any qualification indication provided through Insure Motiv is preliminary and is not a "
     "binding quote, rate, offer of coverage, or approval."),
    ("Use of Window Motiv does not guarantee that you will be contacted, receive an appointment, "
     "receive an estimate, qualify for financing, obtain any promotional price, or achieve any "
     "particular outcome.",
     "Use of Insure Motiv does not guarantee that you will be contacted, receive a quote, qualify "
     "for coverage, be approved by any carrier, obtain any particular premium, or achieve any "
     "particular outcome."),

    # health information: the live form asks for none, and this says so
    ("Window Motiv does not request medical, disability, or health information through its lead forms.",
     "Insure Motiv does not request medical, disability, or health information through its lead "
     "forms. A licensed agent or carrier may ask health questions separately, after you are "
     "connected; any such information is collected by that agent or carrier under their own "
     "privacy practices, not through Insure Motiv."),


    # generic catch-all lists that still lean home improvement
    ("you qualify for any product, program, benefit, service, rebate, incentive, claim, quote, "
     "financing, or other opportunity",
     "you qualify for any product, program, benefit, coverage, quote, rate, or other opportunity"),
    ("you will qualify for any service, rebate, incentive, or financing",
     "you will qualify for any coverage, product, or premium"),
    ("the Services will result in savings; ", ""),
    ("availability; pricing; workmanship; advice; representations; financial condition; "
     "regulatory compliance; or performance",
     "availability; pricing; underwriting or claims handling; advice; representations; financial "
     "condition; regulatory compliance; or performance"),
    ("facilitate a requested quote, consultation, measurement, estimate, or service",
     "facilitate a requested quote, consultation, or connection with a licensed agent"),
    # Window Motiv keeps a separate participating-company directory at
    # /Disclosure.html. Insure Motiv has no such page, and section 3 of this
    # document is that list, so the link would only be dead.
    ("The current [directory of participating companies](/Disclosure.html) is also "
     "maintained on this website.",
     "The categories of company that may contact you are listed in section 3 above."),

    # Relative, matching the asset paths: a root-absolute link only works when
    # this folder is the web root.
    ("](/privacy-policy)", "](privacy-policy.html)"),
    ("](/terms-of-use)", "](terms-of-use.html)"),

    # Insure Motiv has no separate Marketing Partners page, so these would be
    # links to nothing. The reference stays, the link goes.
    ("[Brands, Affiliates, and Marketing Partners Disclosure](/disclosures/marketing-partners)",
     "Brands, Affiliates, and Marketing Partners Disclosure"),
    ("[Marketing Partners Disclosure](/disclosures/marketing-partners)",
     "Marketing Partners Disclosure"),
    ('"Leads Motiv," "Window Motiv,"', '"Leads Motiv," "Insure Motiv,"'),
    ("WINDOW MOTIV", "INSURE MOTIV"),
    ("Window Motiv", "Insure Motiv"),
    ("Windows Motiv", "Insure Motiv"),
    ("September 2, 2026", TODAY),
    ("2026-09-02", ISO),
]

# ---- whole-block rewrites ------------------------------------------------
TERMS_BLOCK_START = "H3 No Contractor or Design-Professional Relationship"
TERMS_BLOCK_END = "H2 9. OTHER GOVERNMENT AND INSURANCE DISCLAIMERS"
TERMS_BLOCK_NEW = u"""H3 No Insurance Agency or Advisory Relationship

Insure Motiv is not an insurance carrier, insurer, underwriter, insurance agency, or licensed insurance producer.

Your use of a Motiv website, completion of a form, or communication with Motiv does not create an agent-client, broker-client, insurer-insured, or advisory relationship between you and Motiv, and does not create an application for, or a contract of, insurance.

An independent provider to whom you are referred may be a licensed insurance agent, agency, or carrier. Any professional or contractual relationship with such a provider arises only under the terms separately established between you and that provider, and any policy is issued solely by the carrier.

H2 8. INSURE MOTIV AND INSURANCE SERVICES

Insure Motiv is a private marketing and lead-generation service that helps connect consumers with licensed insurance agents and providers.

Insure Motiv, Leads Motiv, LLC, Motiv Brands, Inc., and their affiliates:

- do not sell, solicit, negotiate, underwrite, issue, service, or administer insurance policies, and do not pay, adjudicate, or adjust claims;

- are not a licensed insurance producer, agency, or carrier in any jurisdiction;

- are not affiliated with Medicare, Medicaid, the Social Security Administration, any state insurance department, or any other government agency or program;

- are not endorsed, sponsored, or approved by any government agency, insurance regulator, or carrier; and

- cannot guarantee the availability, premium, underwriting outcome, issuance, terms, or claim treatment of any policy or promotional offer.

Coverage, rates, eligibility, and availability vary by provider, state, age, and health, and are determined solely by the applicable carrier under its own underwriting rules.

Submitting information through Insure Motiv is not the same as applying for insurance, being approved for coverage, or being issued a policy.

Any qualification indication provided through Insure Motiv is preliminary and is not a binding quote, rate, offer of coverage, or approval.

You may contact a licensed insurance agent or carrier directly without using Insure Motiv.

Use of Insure Motiv does not guarantee that you will be contacted, receive a quote, qualify for coverage, be approved by any carrier, obtain any particular premium, or achieve any particular outcome.

Nothing on an Insure Motiv website is an offer of insurance, a solicitation in any state where a product is not available, or insurance, tax, legal, or financial advice.

"""

PRIVACY_ROWS_OLD_START = 'RAW <tr><td>Property information</td>'
PRIVACY_ROWS_OLD_END = 'RAW <tr><td>Communications</td>'
PRIVACY_ROWS_NEW = u"""RAW <tr><td>Eligibility information</td><td>Age or age range, state of residence, and whether you are requesting coverage for yourself or for another person</td></tr>
RAW <tr><td>Coverage information</td><td>Type of coverage requested, approximate coverage amount, any existing coverage, and preferred contact timing</td></tr>
RAW <tr><td>Premium information</td><td>Whether you are interested in a particular premium range or payment option, expressed as general budget categories rather than detailed financial records</td></tr>
"""

# The generic insurance row is redundant once the whole document is about
# insurance; the two rows above say it precisely.
PRIVACY_GENERIC_ROW = ("RAW <tr><td>Insurance information</td><td>General insurance status, type of "
                       "coverage, or similar information relevant to the requested service</td></tr>\n")

LEFTOVERS = re.compile(r"window|home-improvement|contractor|remodel|siding|roofing|workmanship|"
                       r"measurement|energy-effic|rebate|utility incentive", re.I)


def block_replace(text, start, end, new, label):
    i, j = text.find(start), text.find(end)
    if i < 0 or j <= i:
        raise SystemExit("%s: could not locate the block" % label)
    print("  ok  %s" % label)
    return text[:i] + new + text[j:]


for name in ("privacy-policy", "terms-of-use"):
    path = os.path.join(SRC, name + ".txt")
    s = io.open(path, encoding="utf-8").read()
    print("%s.txt" % name)

    if name == "terms-of-use":
        s = block_replace(s, TERMS_BLOCK_START, TERMS_BLOCK_END, TERMS_BLOCK_NEW,
                  "sections 7-8 rewritten for insurance")
    else:
        s = block_replace(s, PRIVACY_ROWS_OLD_START, PRIVACY_ROWS_OLD_END, PRIVACY_ROWS_NEW,
                  "collected-data rows")
        if PRIVACY_GENERIC_ROW in s:
            s = s.replace(PRIVACY_GENERIC_ROW, "")
            print("  ok  dropped the now-redundant generic insurance row")

    for old, new in PHRASES:
        s = s.replace(old, new)

    # Inserted after the phrase pass on purpose: this prose names Window
    # Motiv and PestMotiv deliberately, and must not be rewritten.
    s = re.sub(r"^:changelog .*$", ":changelog " + CHANGELOG[name].replace("\\", "\\\\"),
               s, count=1, flags=re.M)
    print("  ok  changelog rewritten for Insure Motiv")


    io.open(path, "w", encoding="utf-8", newline="").write(s)

    left = [(i + 1, l.strip()[:110]) for i, l in enumerate(s.split("\n")) if LEFTOVERS.search(l)]
    if left:
        print("  REVIEW - lines still sounding like home improvement:")
        for n, l in left:
            print("     %5d  %s" % (n, l))
    print()
