# Prototype Workspace of the KTH Data Hub

This repository contains the content for the KTH Data Hub Workspace, which is a
prototype service developed by the [KTH Data Hub](https://www.kth.se/datahub).

Our aim is to maintain it in both English and Swedish.

This is a statically generated website for research data and research software
support at KTH, built with MkDocs and deployed to GitHub Pages.


## How to contribute

- If you only have small text contributions (e.g., additions, corrections),
  we suggest you (in order of increasing required technical know-how):
  1. propose your changes by using the built-in editing function here on Github (described below), or
  2. [open an issue](../../issues), or
  3. [create a pull request](../../pulls) ([how?](https://github.blog/developer-skills/github/beginners-guide-to-github-creating-a-pull-request)).
- If you want to preview your changes, follow the instructions in
  the [Local development section](#local-development) below.


## Contribute using Github's built-in *Edit* function (requires no local setup)

1. Open this repository on GitHub.
2. Go to the page you want to change in `docs/en/` or `docs/sv/`.
3. Click the pencil icon (Edit this file).
4. Make your changes.
5. Scroll down and choose "Create a new branch".
6. Click "Propose changes".
7. Open a pull request.


## Repository layout

```text
.
├── mkdocs.yml                  # Site config: navigation, menu, theme, plugins, etc.
├── requirement.txt             # Pinned Python dependencies (mkdocs>=1.6,<2)
├── pyproject.toml / uv.lock    # Same dependencies for `uv`
├── .github/workflows/ci.yaml   # Build + deploy to GitHub Pages on push to master
├── service_catalog/            # Service Catalogue *logic* (never published)
│   ├── hooks/services.py       # MkDocs hook that generates the Service Catalogue HTML
│   ├── VERSION                 # Catalogue version, shown in the page footer
│   └── CHANGELOG.md            # Catalogue change log
├── docs/                       # All Workspace content (pages, assets, etc.)
│   ├── en/                     # English-language content
│   │   ├── how_to_guides       # 
│   │   ├── methodologies       # 
│   │   ├── ...                 # 
│   │   └── services/           # Service catalogue English **content**
│   │       ├── index.md        # Overview page (holds the ARCHIVE comment marker)
│   │       └── <service>.md    # One Markdown file per service
│   ├── sv/                     # Swedish-language content
│   │   ├── how_to_guides       # 
│   │   ├── methodologies       # 
│   │   ├── ...                 # 
│   │   └── services/           # Service catalogue Swedish **content**
│   │       ├── index.md        # Overview page (holds the ARCHIVE comment marker)
│   │       └── <service>.md    # One Markdown file per service
│   ├── stylesheets/service_catalog/services.css
│   └── javascripts/service_catalog/services.js
└── site/                       # Generated website HTML, CS, JSS (to be published)
```

Note that it is necessary to keep the Python hook *outside*  the `docs/` tree to
avoid it being copied to the published `site/` tree.



## Add your own contribution to the Workspace

### Overview

If you want to add a new document named `reproducible-numerical-analysis.md`,

- create `docs/en/<choose-suitable-directory-here>/reproducible-numerical-analysis.md`.
- ideally also create a Swedish-language version in `docs/sv/<choose-suitable-directory-here>/reproducible-numerical-analysis.md`.
- update `mkdocs.yml`:
  Ensure that your filename is included in the `nav` section of the `mkdocs.yml`
  configuration for both `en` and `sv`, for example:

```yaml
nav:
  - Home: index.md
  # add the new document here
  - Reproducible numerical analysis: reproducible-numerical-analysis.md
# ...
# and for the Swedish version:
plugins:
  - i18n:
    - locale: sv
      name: Svenska
      build: true
      nav:
        - Hem: index.md
        # add the new document here
        - Reproducerbar numerisk analys: reproducible-numerical-analysis.md
```

### Adding a Card (Service, Guide, Checklist, Support)

All catalogue cards are automatically discovered from Markdown files. You **do not** need to register them in `mkdocs.yml` `nav`.

#### 1. File placement
- English version: `docs/en/services/[subfolder/]<id>.md`
- Swedish version: `docs/sv/services/[subfolder/]<id>.md`
- Files can be stored directly in `services/` or organized in subdirectories (e.g., `tools/`, `guides/`, `checklists/`, `support/`).
- **Important:** The filename `<id>.md` must be identical in both language directories so the engine can pair them.

---

#### 2. Complete Template Example

```yaml
---
name: Zenodo Research Storage
type: service              # service, guide, checklist, or support
provider: CERN
group: Research Data Storage
tags:
  - Open Access
  - DOI
  - FAIR Data
last_updated: 2026-10-04    # YYYY-MM-DD: sets publication date in RSS feeds
link: https://zenodo.org    # Always link to a webpage (avoid direct mailto:)
button_text: Open service  # Optional: overrides default button label
related:
  - kth-onedrive           # Bi-directional: links both cards automatically
rating:                    # Traffic light assessment (optional)
  legal:
    status: green
    note: GDPR compliant within the EU
  ip:
    status: green
  security:
    status: yellow
    note: Only approved for data classification up to Level 2
  cost:
    status: green
    note: Free of charge up to 50 GB per dataset
  support:
    status: yellow
    note: Community-driven and CERN helpdesk
---

A brief summary displayed on the card face in the catalogue grid. Keep this to 1–3 concise sentences.

##Field & Feature Reference
Feature	Details
Date (last_updated)	YYYY-MM-DD. Dictates card publication in the language RSS feeds (/services-en.xml and /services-sv.xml). Update this date when significant content changes are published. (Fallback: file modification timestamp).
Tables	Standard Markdown pipe syntax | col | col | inside any ## section. Rendered with neat borders and zebra striping inside the modal accordions.
Images	Standard Markdown ![alt text](../../path/to/image.png). Images are constrained to max-width: 100% so they never overflow the modal container.
Card Types (type)	service (tools/services), guide, checklist, or support. Controls the card's color-coded icon, top filter tabs, and default action button text.
Buttons (link & button_text)	Target destination URL. Default label is "Open service / Öppna tjänsten" for services, and "More information / Mer information" for guides, checklists, and support. Override at any time with button_text: "Custom label".
Headings (##)	Text before the first ## is the front card summary. Every subsequent ## Heading becomes an expandable accordion inside the details modal.
Traffic Lights (rating)	Dimensions: legal, ip, security, cost, support. Allowed statuses: green, yellow, red. The overall badge displays the worst rating among critical categories (legal, ip, security). Missing critical ratings show as incomplete (grey).
Assessment Notes (note)	Optional explanations per rating dimension. Clicking the traffic light in the modal expands these notes for full transparency.
Bi-directional Relations (related)	List of other card IDs (e.g. related: [kth-onedrive, gitlab]). Defining it on one card automatically establishes mutual mini-card links in both modals.
Tags (tags)	Keyword list. Displayed as badges on the card face, searchable via free text, and automatically aggregated in the tag filter dropdown.
Cross-language Fallback	If a card only exists in one language, it is still displayed in both language catalogues with an [In English] or [På svenska] badge and an informational notice inside the modal.

## About the service

Every second-level heading (`##`) automatically becomes a collapsible accordion section inside the details modal.

Standard Markdown tables are fully supported inside any section:

| Feature | Details | Supported |
| :--- | :--- | :---: |
| Maximum upload | 50 GB per dataset | Yes |
| Persistent ID | Automatic DOI minting | Yes |
| Versioning | GitHub release integration | Yes |

## Architecture

Images are supported and will automatically scale responsively inside the modal:

![Service Architecture](../../assets/images/zenodo-architecture.png)

## Getting started

- Log in using your ORCID or GitHub account.
- Select your research community or repository.
- Upload your dataset and complete the required metadata fields.


### Local development

This is only required if you want to preview the site locally, and not necessary
unless you are also contributing changes to the site's configuration, structure or logic.

Requirements:

- Python >=3.12
- `uv`

Install `uv`:
<https://docs.astral.sh/uv/getting-started/installation>

Install project dependencies:

```bash
make install
```

Start local preview:

```bash
make serve
```

Open the localhost address that the script provides in your local browser, usually
`http://127.0.0.1:8000`.


### Build the site

This creates the static files in `site/`:

```bash
uv run mkdocs build
```

Alternatively (or in addition) you might want to use the same flags used by our
CI build pipeline (to avoid surprises):

```bash
uv run mkdocs build --clean --strict -v
```

---
## Field & Feature Reference
Feature	Details
Date (last_updated)	YYYY-MM-DD. Dictates card publication in the language RSS feeds (/services-en.xml and /services-sv.xml). Update this date when significant content changes are published. (Fallback: file modification timestamp).

Tables	Standard Markdown pipe syntax | col | col | inside any ## section. Rendered with neat borders and zebra striping inside the modal accordions.

Images	Standard Markdown ![alt text](../../path/to/image.png). Images are constrained to max-width: 100% so they never overflow the modal container.

Card Types (type)	service (tools/services), guide, checklist, or support. Controls the card's color-coded icon, top filter tabs, and default action button text.

Buttons (link & button_text)	Target destination URL. Default label is "Open service / Öppna tjänsten" for services, and "More information / Mer information" for guides, checklists, and support. Override at any time with button_text: "Custom label".

Headings (##)	Text before the first ## is the front card summary. Every subsequent ## Heading becomes an expandable accordion inside the details modal.

Traffic Lights (rating)	Dimensions: legal, ip, security, cost, support. Allowed statuses: green, yellow, red. The overall badge displays the worst rating among critical categories (legal, ip, security). 
Missing critical ratings show as incomplete (grey).

Assessment Notes (note)	Optional explanations per rating dimension. Clicking the traffic light in the modal expands these notes for full transparency.

Bi-directional Relations (related)	List of other card IDs (e.g. related: [kth-onedrive, gitlab]). Defining it on one card automatically establishes mutual mini-card links in both modals.

Tags (tags)	Keyword list. Displayed as badges on the card face, searchable via free text, and automatically aggregated in the tag filter dropdown.

Cross-language Fallback	If a card only exists in one language, it is still displayed in both language catalogues with an [In English] or [På svenska] badge and an informational notice inside the modal.--

## Other ways to contribute

If you spot a typo, error, or want to add more information, feel free to contribute, we welcome all contributions to the KTH Data Hub Workspace.

Please [open an issue](../../issues) or [submit a pull request](../../pulls).

To submit a pull request, you always need to start by forking, but note that you
can replace the traditional workflow of *cloning, committing, then pushing* by simply
opening your forked Github repository in [Github.dev](https://github.dev) and make
your changes and commits without leaving your browser.
(Github.dev is just the VSCode editor in your browser, provided by Github and
facilitated by the fact that the core of VSCode is freely licensed software).

For the traditional workflow, you may follow these steps (but please note that you
can find far many better guides on the web):

- Make sure you have a GitHub account.
- Open [this repository](#).
- Click the "Fork" button in the top-right corner to create a copy of the repository in your account.
- Open your fork of the repository and clone it to your computer.
- Optionally, create a new branch for your changes.
- Make the necessary updates or edits.
- Commit your changes.
- Push the changes to your fork.
- Submit a pull request from your fork to this repository.
- Wait for your pull request to be reviewed and merged by us.


## How this site is deployed

In short, the site is deployed through GitHub Actions to GitHub Pages.
New commits to the `master` branch trigger a Github Action that runs the
`mkdocs` build pipeline and automatically copies the updated `site/` tree
to Github Pages.

### GitHub Actions

`.github/workflows/ci.yaml` runs on every push to `master`:

1. checkout
2. set up Python 3.12 and `uv`
3. `uv sync`
4. `uv run mkdocs build --clean --strict`
5. `uv run mkdocs gh-deploy --force` → pushes `site/` to the `gh-pages` branch

**Strict mode matters.** Any MkDocs warning, e.g., due to a broken link,
a page in `docs/` that is not in the `nav`, will fail the build.
Pages that need to stay out of the `nav` must be listed in `not_in_nav`, e.g.,
`*/services/*.md` because Service Catalogue pages are reached through the
catalogue, not the navigation menu.


### Dependencies

| Package | Why |
| ---     | --- |
| `mkdocs` (>=1.6,<2) | Site generator. **Do not upgrade to 2.0** — would remove the plugin system this site depends on |
| `mkdocs-material` | Theme; also supplies the icon SVGs the Service Catalogue inlines |
| `mkdocs-static-i18n` | English/Swedish builds from `docs/en` and `docs/sv` |
| `markdown`, `PyYAML` | Used directly by the Services Catalogue hook |
