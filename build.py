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


def crumb_markup(meta):
    """A trail back to the front page, the way a site of this kind is signposted.

    Each entry is "Label" or "Label|slug"; the last one is the current page and
    is not a link. The home page gets no trail.
    """
    trail = meta.get("crumb")
    if not trail:
        return ""
    parts = ['<a href="index.html">Home</a>']
    for i, entry in enumerate(trail):
        label, _, target = entry.partition("|")
        last = i == len(trail) - 1
        if last or not target:
            parts.append('<span aria-current="page">{}</span>'.format(label)
                         if last else "<span>{}</span>".format(label))
        else:
            parts.append('<a href="{}.html">{}</a>'.format(target, label))
    sep = '<i aria-hidden="true">&rsaquo;</i>'
    return ('<nav class="crumbs" aria-label="Breadcrumb"><div class="wrap">'
            + sep.join(parts) + "</div></nav>\n")


def build_page(slug, meta, partials):
    body = read(PAGES / "{}.html".format(slug))

    head = partials["head"]
    head = head.replace("{{TITLE}}", meta["title"])
    head = head.replace("{{DESCRIPTION}}", meta["description"])
    head = head.replace("{{ROBOTS}}", meta.get("robots", "index, follow"))
    head = head.replace("{{CANONICAL}}", "" if slug == "index" else "{}.html".format(slug))
    head = head.replace("{{HEAD_EXTRA}}", meta.get("head_extra", ""))

    chrome = partials["chrome"].replace("{{TICKER_ITEMS}}", partials["ticker"])
    active = meta.get("nav")
    for key, token in NAV_KEYS.items():
        chrome = chrome.replace("{{%s}}" % token, ' class="active"' if key == active else "")

    tail = (partials["cta"] if meta.get("cta", True) else "") + partials["footer"]

    return head + chrome + crumb_markup(meta) + body.rstrip("\n") + "\n\n" + tail


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
