#!/usr/bin/env python3
"""
Bundle the whole site into one self-contained HTML file.

Useful for sharing a browsable preview where a real deployment isn't available
(or is behind auth). Inlines the stylesheet, the script, and the SVG marks, then
stacks every page body into one document and swaps between them client-side, so
the nav still works with no server and no network.

Two deliberate differences from the deployed site, both surfaced in the preview
itself: forms are inert (they would otherwise post real leads), and CreditMatch
is a compiled app that can't be inlined, so it gets a placeholder.

    python3 scripts/make-preview.py [output.html]
"""

import base64
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / "src" / "pages"
PARTIALS = ROOT / "src" / "partials"
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "preview.html"

# Order shapes the nav and the page stack.
ORDER = [
    "index", "solutions", "process", "industries", "coverage", "track-record",
    "partners", "about", "apply", "contact", "faq",
    "bridge-loans", "growth-capital", "working-capital", "second-lien",
    "acquisition-financing", "recapitalizations",
    "thanks", "privacy", "terms", "disclosures", "licensing",
]

DEPLOYED = "https://tvt-capital-f0ve7m8om-vincenttvt77-9161s-projects.vercel.app"


def read(p):
    return p.read_text(encoding="utf-8")


def data_uri(path):
    return "data:image/svg+xml;base64," + base64.b64encode(path.read_bytes()).decode()


def route_links(html):
    """Point every same-site link at the in-page router."""
    def sub(m):
        attr, slug = m.group(1), m.group(2)
        if slug == "creditmatch":
            return '%s="#creditmatch" data-goto="creditmatch"' % attr
        return '%s="#%s" data-goto="%s"' % (attr, slug, slug)
    return re.sub(r'(href)="([a-z0-9-]+)\.html"', sub, html)


def build():
    css = read(ROOT / "tvt.css")
    js = read(ROOT / "tvt.js")
    meta = json.loads(read(ROOT / "src" / "pages.json"))

    wordmark = data_uri(ROOT / "assets" / "tvt-wordmark.svg")
    wordmark_light = data_uri(ROOT / "assets" / "tvt-wordmark-light.svg")

    # --- shared chrome -------------------------------------------------
    sys.path.insert(0, str(ROOT))
    import build as builder  # single source of truth for ticker items
    ticker = builder.ticker_markup()

    chrome = read(PARTIALS / "chrome.html").replace("{{TICKER_ITEMS}}", ticker)
    for token in ("A_SOLUTIONS", "A_PROCESS", "A_INDUSTRIES", "A_COVERAGE",
                  "A_TRACK", "A_PARTNERS", "A_CREDITMATCH"):
        chrome = chrome.replace("{{%s}}" % token, "")
    chrome = route_links(chrome).replace("assets/tvt-wordmark.svg", wordmark)

    footer = read(PARTIALS / "footer.html")
    footer = footer.split('<script src="tvt.js"')[0]
    footer = route_links(footer).replace("assets/tvt-wordmark-light.svg", wordmark_light)

    cta = route_links(read(PARTIALS / "cta.html"))

    # --- page stack ----------------------------------------------------
    sections = []
    for slug in ORDER:
        body = route_links(read(PAGES / ("%s.html" % slug)))
        tail = cta if meta.get(slug, {}).get("cta", True) else ""
        sections.append(
            '<div class="pv-page" id="page-%s" data-page="%s" hidden>\n%s\n%s</div>'
            % (slug, slug, body, tail)
        )

    sections.append('''<div class="pv-page" id="page-creditmatch" data-page="creditmatch" hidden>
  <section class="dark-panel">
    <div class="wrap page-hero">
      <div class="eyebrow on-dark">CreditMatch</div>
      <h1 class="h-xl" style="color:#fff;">A separate app, <span class="italic-accent">not restyled.</span></h1>
      <div class="hero-rule"></div>
      <p class="lede on-dark">CreditMatch is a pre-compiled single-page application whose source lives outside
      the website repository. It ships unchanged and keeps its own look, so it can't be bundled into this
      single-file preview.</p>
      <div class="actions">
        <a class="btn btn-brass" href="%s/creditmatch.html" target="_blank" rel="noopener">Open it on the deployment <span class="arrow" aria-hidden="true">&rarr;</span></a>
      </div>
    </div>
  </section>
</div>''' % DEPLOYED)

    nav_titles = {slug: meta.get(slug, {}).get("title", slug) for slug in ORDER}
    nav_titles["creditmatch"] = "CreditMatch | TVT Capital"

    preview_css = '''
/* ---- preview shell (not part of the site) ---- */
.pv-page[hidden] { display: none; }
.pv-note {
  position: fixed; left: 16px; bottom: 16px; z-index: 200;
  display: flex; align-items: center; gap: 12px;
  background: var(--forest-950); color: rgba(255,255,255,.82);
  border: 1px solid var(--rule-dark); border-radius: 2px;
  padding: 11px 14px; font-family: var(--font-body); font-size: 12px;
  letter-spacing: .01em; max-width: min(92vw, 460px);
  box-shadow: 0 10px 30px rgba(7,26,18,.28);
}
.pv-note b { color: var(--brass-400); font-weight: 600; letter-spacing: .12em;
  text-transform: uppercase; font-size: 10px; }
.pv-note button {
  background: none; border: none; color: rgba(255,255,255,.5);
  font-size: 16px; line-height: 1; cursor: pointer; padding: 2px 4px; margin-left: auto;
}
.pv-note button:hover { color: #fff; }
.pv-note[hidden] { display: none; }
.pv-toast {
  position: fixed; left: 50%; bottom: 32px; transform: translate(-50%, 14px);
  z-index: 240; background: var(--forest-900); color: #fff;
  border: 1px solid var(--brass); border-radius: 2px; padding: 14px 22px;
  font-family: var(--font-body); font-size: 13.5px;
  opacity: 0; pointer-events: none; transition: opacity .25s ease, transform .25s ease;
}
.pv-toast.on { opacity: 1; transform: translate(-50%, 0); }
@media (prefers-reduced-motion: reduce) { .pv-toast { transition: none; } }
'''

    router = '''
(function () {
  "use strict";
  var TITLES = %s;
  var pages = document.querySelectorAll(".pv-page");
  var navLinks = document.querySelectorAll(".nav-links a, .nav-mobile a");

  var io = null;
  if ("IntersectionObserver" in window &&
      !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target;
        var d = parseInt(el.getAttribute("data-reveal-delay") || "0", 10);
        setTimeout(function () { el.classList.add("in"); }, d);
        io.unobserve(el);
      });
    }, { rootMargin: "0px 0px -8%% 0px", threshold: 0.06 });
  }

  function show(slug, push) {
    var target = document.getElementById("page-" + slug);
    if (!target) { slug = "index"; target = document.getElementById("page-index"); }

    Array.prototype.forEach.call(pages, function (p) { p.hidden = true; });
    target.hidden = false;

    // Replay the scroll reveal for the page being shown.
    var reveals = target.querySelectorAll(".reveal");
    Array.prototype.forEach.call(reveals, function (el) {
      el.classList.remove("in");
      if (io) io.observe(el); else el.classList.add("in");
    });

    Array.prototype.forEach.call(navLinks, function (a) {
      a.classList.toggle("active", a.getAttribute("data-goto") === slug);
    });

    document.title = TITLES[slug] || "TVT Capital";
    var bar = document.getElementById("navBar");
    if (bar) bar.classList.remove("open");
    window.scrollTo(0, 0);
    if (push && location.hash !== "#" + slug) history.replaceState(null, "", "#" + slug);
  }

  document.addEventListener("click", function (e) {
    var a = e.target.closest ? e.target.closest("[data-goto]") : null;
    if (!a) return;
    e.preventDefault();
    show(a.getAttribute("data-goto"), true);
  });

  window.addEventListener("hashchange", function () {
    show((location.hash || "#index").slice(1), false);
  });

  // Forms are inert here — submitting would post a real lead.
  var toast = document.querySelector(".pv-toast");
  var toastTimer;
  document.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!toast) return;
    toast.classList.add("on");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.classList.remove("on"); }, 2600);
  });

  var dismiss = document.querySelector(".pv-note button");
  if (dismiss) dismiss.addEventListener("click", function () {
    dismiss.parentNode.hidden = true;
  });

  show((location.hash || "#index").slice(1), false);
})();
''' % json.dumps(nav_titles)

    doc = []
    # Must come first: the page carries UTF-8 punctuation throughout, and
    # without this the host renders it as mojibake.
    doc.append('<meta charset="utf-8" />')
    doc.append("<title>TVT Capital Redesign</title>")
    doc.append('<link rel="preconnect" href="https://fonts.googleapis.com" />')
    doc.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />')
    doc.append('<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,'
               'wght@0,9..144,300..600;1,9..144,300..500&family=Inter:wght@400;500;600'
               '&display=swap" rel="stylesheet" />')
    doc.append("<style>\n%s\n%s</style>" % (css, preview_css))
    doc.append(chrome)
    doc.append("\n".join(sections))
    doc.append(footer)
    doc.append('''<div class="pv-note">
  <b>Preview</b>
  <span>Every page is bundled into this one file — links switch in place. Forms are inert.</span>
  <button type="button" aria-label="Dismiss">&times;</button>
</div>
<div class="pv-toast" role="status">Preview only — nothing was submitted.</div>''')
    doc.append("<script>\n%s\n%s</script>" % (js, router))

    OUT.write_text("\n".join(doc) + "\n", encoding="utf-8")
    kb = OUT.stat().st_size / 1024
    print("wrote %s (%.0f KB, %d pages)" % (OUT, kb, len(ORDER) + 1))


if __name__ == "__main__":
    build()
