# TVT Capital — website

Static marketing site for TVT Capital. No framework, no deploy-time build:
Vercel (or any static host) serves the generated `*.html` at the repo root.

## Layout

```
index.html, solutions.html, …   generated pages — commit these, don't hand-edit
creditmatch.html                self-contained app, see "CreditMatch" below
tvt.css                         design system
tvt.js                          nav, scroll reveal, form wizard, phone masking
refinements.css                 distinct main-page layouts, ticker, location styling
refinements.js                  financing filters, process explorer, ticker motion
assets/                         SVG wordmarks + favicon
build.py                        assembles pages from src/
src/partials/                   shared shell: head, ticker + nav, closing CTA, footer
src/pages/                      per-page body content
src/pages.json                  per-page title, description, robots, nav state
```

## Making a change

Edit the body in `src/pages/<slug>.html` (or the shell in `src/partials/`), then:

```
python3 build.py
```

That regenerates every root-level page. Commit the regenerated HTML along with
the source — the site is served straight from the repo, so stale output ships.

`build.py` fails loudly if a `{{PLACEHOLDER}}` survives assembly.

## Visual design

The September 2026 redesign keeps the original TVT logo byte-for-byte. It uses
Helvetica Neue with system sans-serif fallbacks for headings and body copy,
the logo’s forest greens, white, and restrained silver accents. The homepage pairs a
large typographic introduction with a licensed Utah skyline photograph. TVT is
Utah-based with offices across the United States, including Manhattan; the
supplied NYC address is labeled as the Manhattan office. The main pages use
shorter copy, open layouts, lightly shaded surfaces, and restrained green accents.
Photo attribution and location details are in `docs/utah-location-update.md`.

Solutions, Process, About, and Partners have distinct compositions. Financing
filters and a four-stage process explorer progressively enhance the static
content. All options and steps remain readable without JavaScript. The restored
top conveyor pauses on hover or keyboard focus and uses the original representative structures and “What we fund”
label; it is not a live feed of verified funded deals.

All 27 marketing pages share the navigation, page shell, forms, and design
system. The company-provided brief is retained in `docs/company-brief.txt`.
The financing range, track-record figures, address, and contact details come
from the supplied company material. Existing specialized financing pages and
legal disclosures remain available.

`creditmatch.html` is an existing compiled tax-credit application. Its JavaScript
is preserved; `creditmatch-theme.css` provides the visual refresh. Describe it
as tax-credit exploration, not as a general financing-matching tool.

## Adding a page

1. Write the body in `src/pages/<slug>.html` (content only — no `<head>`, nav, or footer).
2. Add an entry to `src/pages.json` with at least `title` and `description`.
   Optional keys: `nav` (which primary link to mark active), `robots`,
   `head_extra` (e.g. JSON-LD), `cta: false` to drop the shared closing CTA.
3. Run `python3 build.py`.

## Navigation and forms

The top navigation prioritizes financing, approach, company, and partners.
The footer and mobile menu expose the full destination set. Forms preserve the
existing Web3Forms destination and consent text. The borrower form now uses
explicit Continue buttons and validates each step. A same-origin confirmation
redirect follows a successful provider submission. No test lead is sent.

## Assets and publishing

The original brand PNGs and optimized JPEG photographs are included in Git.
The logo is unmodified. The large source photograph PNGs are omitted from the
public output. `python3 scripts/build-static.py` runs the normal page generator
and packages only public HTML, CSS, JavaScript, and assets into `dist/`.
`python3 scripts/check-site.py` checks local links, assets, and required pages.

## Single-file preview

`scripts/make-preview.py` bundles every page into one self-contained HTML file —
stylesheet, script, and SVG marks inlined, nav wired to switch pages in place.
Useful for sharing the design where a deployment isn't available.

```
python3 scripts/make-preview.py        # writes preview.html (gitignored)
```

Two deliberate differences from the deployed site, both stated in the preview
itself: forms are inert, since they would otherwise post real leads, and
CreditMatch gets a placeholder because a compiled app can't be inlined.

## Local preview

```
python3 -m http.server 8000
```

Then open http://127.0.0.1:8000/.

## Forms

All three forms (borrower intake, partner application, contact) post to
Web3Forms with the shared `access_key`, and redirect to `thanks.html`.
Submit-time subject lines and the phone-number mask are handled in `tvt.js`.

Original site: https://tvt-capital.vercel.app/ (preserved separately). Redesign review: https://tvt-capital-redesign.vincenttvt77.chatgpt.site/ . The redesign remains on its own draft PR; the original branch is not merged or replaced.
