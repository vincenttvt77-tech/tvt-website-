#!/usr/bin/env python3
"""
Assemble the static site.

Every page shares one shell (deal ticker, announcement bar, nav, footer), so the
shell lives in src/partials/ and the per-page body lives in src/pages/. Run this
after touching either, then commit the generated HTML at the repo root — Vercel
serves those files directly, no build step required at deploy time.

    python3 build.py
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
PARTIALS = ROOT / "src" / "partials"
PAGES = ROOT / "src" / "pages"
MANIFEST = ROOT / "src" / "pages.json"

# Representative deal structures shown in the top ticker. Deliberately no dates,
# amounts, or borrower names — these describe the kinds of transactions the
# platform funds, not specific closed deals.
TICKER = [
    ("OH", "Industrial Mfg", "2nd-Lien"),
    ("TX", "Healthcare Services", "Growth"),
    ("NJ", "Industrial Dist.", "Bridge"),
    ("CA", "Tech-Enabled Svcs", "Growth"),
    ("FL", "Multi-Unit Retail", "Working Cap"),
    ("IL", "Specialty Chem", "Senior"),
    ("GA", "Logistics", "Bridge"),
    ("PA", "Building Products", "Acquisition"),
    ("AZ", "Behavioral Health", "Growth"),
    ("NC", "Franchise Platform", "Recap"),
    ("WA", "Aerospace & Defense", "Acquisition"),
    ("TN", "Home Health", "Working Cap"),
]

NAV_KEYS = {
    "solutions": "A_SOLUTIONS",
    "process": "A_PROCESS",
    "industries": "A_INDUSTRIES",
    "coverage": "A_COVERAGE",
    "track-record": "A_TRACK",
    "partners": "A_PARTNERS",
    "creditmatch": "A_CREDITMATCH",
}


def read(path):
    return path.read_text(encoding="utf-8")


def ticker_markup():
    """Two identical passes so the -50% marquee keyframe loops seamlessly."""
    row = "".join(
        '        <span><i>{}</i> {} <b>{}</b></span>\n'.format(
            state, sector.replace("&", "&amp;"), structure
        )
        for state, sector, structure in TICKER
    )
    return (row + row).rstrip("\n")


def build_page(slug, meta, partials):
    body = read(PAGES / "{}.html".format(slug))

    head = partials["head"]
    head = head.replace("{{TITLE}}", meta["title"])
    head = head.replace("{{DESCRIPTION}}", meta["description"])
    head = head.replace("{{ROBOTS}}", meta.get("robots", "index, follow"))
    head = head.replace("{{CANONICAL}}", "" if slug == "index" else "{}.html".format(slug))
    head = head.replace("{{HEAD_EXTRA}}", meta.get("head_extra", ""))
    head = head.replace("<body>", '<body data-page="{}">'.format(slug))

    if slug != "index":
        label = meta["title"].split("|")[0].strip().split(" — ")[0]
        import html
        crumb = '<div class="breadcrumb"><a href="index.html">Home</a><span aria-hidden="true">/</span><span>{}</span></div>'.format(html.escape(label))
        body = body.replace('<div class="wrap page-hero">', '<div class="wrap page-hero">' + crumb, 1)
    chrome = partials["chrome"].replace("{{TICKER_ITEMS}}", partials["ticker"])
    active = meta.get("nav")
    if slug == "about":
        chrome = chrome.replace('href="about.html"', 'href="about.html" class="active" aria-current="page"', 1)
    for key, token in NAV_KEYS.items():
        chrome = chrome.replace("{{%s}}" % token, ' class="active" aria-current="page"' if key == active else "")

    tail = (partials["cta"] if meta.get("cta", True) else "") + partials["footer"]

    return head + chrome + '\n<main id="main-content" tabindex="-1">\n' + body.rstrip("\n") + "\n</main>\n\n" + tail


def main():
    partials = {
        "head": read(PARTIALS / "head.html"),
        "chrome": read(PARTIALS / "chrome.html"),
        "cta": read(PARTIALS / "cta.html"),
        "footer": read(PARTIALS / "footer.html"),
        "ticker": ticker_markup(),
    }

    manifest = json.loads(read(MANIFEST))
    written = []
    for slug, meta in manifest.items():
        src = PAGES / "{}.html".format(slug)
        if not src.exists():
            sys.exit("missing body: {}".format(src))
        out = ROOT / "{}.html".format(slug)
        out.write_text(build_page(slug, meta, partials), encoding="utf-8")
        written.append(out.name)

    # Any placeholder left unreplaced is a build error, not a cosmetic issue.
    for name in written:
        leftover = re.findall(r"\{\{[A-Z_]+\}\}", read(ROOT / name))
        if leftover:
            sys.exit("unreplaced placeholder in {}: {}".format(name, leftover))

    print("built {} pages: {}".format(len(written), " ".join(sorted(written))))


if __name__ == "__main__":
    main()
