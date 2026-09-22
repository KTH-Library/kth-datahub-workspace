"""MkDocs hook that renders the digital service catalogue.

WHY THIS EXISTS
---------------
Editors of this site are librarians and research-support staff, not developers.
The catalogue must therefore be maintainable by dropping a single markdown file
into a folder — no central registry, no JSON index, no build step to remember.
This hook is what makes that possible: it turns the markdown files next to the
overview page into cards, filter dropdowns, clickable tags and modal windows.

HOW IT PLUGS IN
---------------
`mkdocs.yml` registers this file under `hooks:`. MkDocs then calls
:func:`on_page_markdown` for every page. Only pages containing the marker
``<!-- SERVICES_ARCHIVE -->`` are touched; the marker is replaced by the
generated HTML block. Everything else passes through unchanged.

INPUTS
    * `docs/<lang>/services/index.md` — the overview page carrying the marker.
    * `docs/<lang>/services/<service>.md` — one file per service, YAML frontmatter
      plus `##` sections (Access / Guides / About the service).

OUTPUT
    A single raw-HTML block injected into the overview page: filter form,
    card grid, one modal per service.

SIDE EFFECTS
    Reads files from disk and writes warnings to the MkDocs log. It never
    writes files; strict builds turn these warnings into build failures only
    for MkDocs' own warnings, not for ours.

ASSUMPTIONS
    * Service pages live in the SAME directory as the overview page.
    * Language is derived from the source path prefix (`sv/` → Swedish).
    * The generated markup is raw HTML, so styling and behaviour come from
      `docs/stylesheets/service_catalog/services.css` and
      `docs/javascripts/service_catalog/services.js`. The class names below are
      a contract with those two files — renaming one means renaming all three.

DEPENDENCIES
    markdown, PyYAML and mkdocs-material (for the inline icon SVGs).
"""

from __future__ import annotations

import html
import logging
import os
import re
from typing import Any, Iterable

import markdown as md_lib
import yaml

log = logging.getLogger("mkdocs.hooks.services")

# --------------------------------------------------------------------------- #
# Constants — no magic values further down.
# --------------------------------------------------------------------------- #

#: Placeholder in the overview page that gets replaced by the generated HTML.
MARKER = "<!-- SERVICES_ARCHIVE -->"

#: Rendered wherever an editor left a required field empty. The specification
#: requires missing information to be *visible* rather than silently omitted.
MISSING = "uppgift saknas"

#: Markdown extensions used when rendering the body sections of a service file.
MD_EXTENSIONS = ["admonition", "attr_list", "md_in_html", "tables", "pymdownx.details"]

#: Front matter keys that become tags, mapped to the CSS colour modifier used
#: for them (`.svc-tag--provider`, `.svc-tag--group`, ...). Only the first three
#: have a matching dropdown; `data` and `location` are display/search only.
TAG_GROUPS: tuple[tuple[str, str], ...] = (
    ("provider", "provider"),
    ("group", "group"),
    ("type", "type"),
    ("data", "data"),
    ("location", "location"),
)

#: Front matter keys a service file must define; a missing one is logged and
#: rendered as MISSING instead of breaking the build.
REQUIRED_FIELDS = ("name", "provider", "group", "summary")

#: Files in the services folder that are never treated as a service.
SKIPPED_FILENAMES = ("index.md",)
SKIPPED_PREFIX = "_"

#: Icon used when a service file does not name one.
DEFAULT_ICON = "material/apps"

#: Heading level that separates the expandable sections inside a service file.
SECTION_PREFIX = "## "

_FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_NON_SLUG_CHARS = re.compile(r"[^a-z0-9]+")


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #


def _markdown_renderer() -> md_lib.Markdown:
    """Create a fresh Markdown renderer.

    A new instance per section is deliberate: python-markdown instances keep
    state (footnotes, reference links) between conversions, which would leak
    content from one service card into the next.
    """
    return md_lib.Markdown(extensions=MD_EXTENSIONS)


def _slug(value: str) -> str:
    """Turn a human label into a stable identifier used in HTML and URLs.

    The same function is used for dropdown option values, card `data-*`
    attributes and tag values, which is what makes "click a tag" equal
    "select that dropdown option" on the client side.
    """
    return _NON_SLUG_CHARS.sub("-", value.lower()).strip("-")


def _as_list(value: Any) -> list[str]:
    """Normalise a front matter value to a list of non-empty strings.

    Editors may write either `data: Öppna data` or a YAML list; both must work.
    """
    if value is None or value == "":
        return []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def _split_sections(body: str) -> list[tuple[str, str]]:
    """Split a service file body into ``(heading, markdown)`` pairs on ``## ``.

    Content before the first `##` heading is intentionally dropped: the card
    summary comes from front matter, so stray prose above the first section
    would have no place to go in the modal.
    """
    sections: list[tuple[str, str]] = []
    current_title: str | None = None
    buffer: list[str] = []
    for line in body.splitlines():
        if line.startswith(SECTION_PREFIX):
            if current_title is not None:
                sections.append((current_title, "\n".join(buffer).strip()))
            current_title = line[len(SECTION_PREFIX):].strip()
            buffer = []
        elif current_title is not None:
            buffer.append(line)
    if current_title is not None:
        sections.append((current_title, "\n".join(buffer).strip()))
    return sections


# --------------------------------------------------------------------------- #
# Parsing service files
# --------------------------------------------------------------------------- #


def _build_tags(meta: dict[str, Any]) -> list[dict[str, str]]:
    """Build the tag list for one service from its front matter.

    Returns dicts of ``label`` (shown), ``kind`` (colour + which dropdown it
    drives) and ``value`` (slug compared against the dropdown value).
    """
    tags: list[dict[str, str]] = []
    for key, kind in TAG_GROUPS:
        for label in _as_list(meta.get(key)):
            tags.append({"label": label, "kind": kind, "value": _slug(label)})
    return tags


def _search_blob(service: dict[str, Any], tags: list[dict[str, str]]) -> str:
    """Pre-compute the lowercase text the free-text search matches against.

    Doing this at build time keeps the client-side search to a single
    `indexOf` per card, which is why filtering stays instant without a search
    library.
    """
    parts = [
        service["name"],
        service["provider"],
        service["group"],
        service["type"],
        service["summary"],
        service["access"],
    ] + [tag["label"] for tag in tags]
    return " ".join(parts).lower()


def _parse_service(path: str, docs_dir: str) -> dict[str, Any] | None:
    """Parse one service markdown file into the dict the renderers consume.

    Args:
        path: Absolute path to the service markdown file.
        docs_dir: MkDocs `docs_dir`, used to record a readable source path.

    Returns:
        A service dict, or None when the file has no/unreadable front matter.

    Side effects: reads the file and logs warnings for missing fields.
    """
    with open(path, encoding="utf-8") as handle:
        raw = handle.read()

    match = _FRONT_MATTER.match(raw)
    if not match:
        log.warning("services: %s has no front matter, skipping", path)
        return None

    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        log.warning("services: could not read front matter in %s (%s)", path, exc)
        return None

    for key in REQUIRED_FIELDS:
        if not meta.get(key):
            log.warning("services: %s is missing '%s' — rendered as '%s'", path, key, MISSING)

    body = raw[match.end():]
    filename = os.path.basename(path)

    service: dict[str, Any] = {
        "id": _slug(os.path.splitext(filename)[0]),
        "name": meta.get("name") or MISSING,
        "icon": meta.get("icon") or DEFAULT_ICON,
        "provider": meta.get("provider") or MISSING,
        "group": meta.get("group") or MISSING,
        "type": meta.get("type") or "",
        "summary": meta.get("summary") or MISSING,
        "access": meta.get("access") or MISSING,
        "link": meta.get("link") or "",
        "link_login": bool(meta.get("link_requires_login")),
        # Service pages sit next to the overview page, so a relative
        # "<name>/" link works in both languages and under a sub-path deploy.
        "page": re.sub(r"\.md$", "/", filename),
        "tags": _build_tags(meta),
        "sections": [
            {"title": title, "html": _markdown_renderer().convert(section_md)}
            for title, section_md in _split_sections(body)
        ],
        "source": os.path.relpath(path, docs_dir).replace(os.sep, "/"),
    }
    service["search"] = _search_blob(service, service["tags"])
    return service


def _collect(page: Any, config: Any) -> list[dict[str, Any]]:
    """Collect every service defined next to the overview page.

    Sorted by provider then name so the grid order is stable between builds
    (a changing order would produce noisy diffs in the generated site).
    """
    docs_dir = config["docs_dir"]
    services_dir = os.path.dirname(os.path.join(docs_dir, page.file.src_path))
    if not os.path.isdir(services_dir):
        return []

    services: list[dict[str, Any]] = []
    for filename in sorted(os.listdir(services_dir)):
        if not filename.endswith(".md"):
            continue
        if filename.startswith(SKIPPED_PREFIX) or filename in SKIPPED_FILENAMES:
            continue
        service = _parse_service(os.path.join(services_dir, filename), docs_dir)
        if service:
            services.append(service)
    services.sort(key=lambda s: (s["provider"].lower(), s["name"].lower()))
    return services


# --------------------------------------------------------------------------- #
# HTML rendering
# --------------------------------------------------------------------------- #


def _icon_html(icon: str) -> str:
    """Inline a Material icon SVG.

    The markup is emitted as raw HTML, so the usual `:material-icon:` shortcode
    is not processed here — the SVG has to be inlined directly.
    """
    try:
        import material

        base = os.path.join(os.path.dirname(material.__file__), "templates", ".icons")
        path = os.path.join(base, *f"{icon}.svg".split("/"))
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as handle:
                return f'<span class="svc-icon">{handle.read()}</span>'
    except Exception:  # pragma: no cover - the icon is decorative only
        pass
    log.warning("services: icon '%s' not found", icon)
    return '<span class="svc-icon"></span>'


def _tag_html(tag: dict[str, str]) -> str:
    """Render one clickable tag.

    A real `<button>` (not a span) so it is reachable by keyboard and exposed
    to screen readers; the JS reads `data-tag-kind`/`data-tag-value`.
    """
    return (
        f'<button type="button" class="svc-tag svc-tag--{tag["kind"]}" '
        f'data-tag-kind="{tag["kind"]}" data-tag-value="{html.escape(tag["value"], quote=True)}">'
        f'{html.escape(tag["label"])}</button>'
    )


def _value_html(value: str) -> str:
    """Escape a value, marking up the "missing information" placeholder."""
    if value == MISSING:
        return f'<span class="svc-missing">{MISSING}</span>'
    return html.escape(value)


def _attr(value: str) -> str:
    """Escape a string for use inside a double-quoted HTML attribute."""
    return html.escape(value, quote=True)


def _card_html(service: dict[str, Any]) -> str:
    """Render one grid card.

    The `data-provider` / `data-group` / `data-type` attributes hold slugs that
    are compared against the dropdown values, and `data-search` holds the
    pre-computed search blob. All filtering reads these attributes, so the card
    markup is the single source of truth for what is filterable.
    """
    tags = "".join(_tag_html(tag) for tag in service["tags"])
    tag_values = " ".join(tag["value"] for tag in service["tags"])
    return f"""<article class="svc-card" id="svc-card-{service['id']}"
  data-id="{service['id']}"
  data-provider="{_attr(_slug(service['provider']))}"
  data-group="{_attr(_slug(service['group']))}"
  data-type="{_attr(_slug(service['type']))}"
  data-tags="{_attr(tag_values)}"
  data-search="{_attr(service['search'])}">
  <button type="button" class="svc-card__open" data-open="{service['id']}">
    <span class="svc-card__icon">{_icon_html(service['icon'])}</span>
    <span class="svc-card__title">{html.escape(service['name'])}</span>
    <span class="svc-card__provider">{_value_html(service['provider'])}</span>
    <span class="svc-card__summary">{_value_html(service['summary'])}</span>
  </button>
  <div class="svc-card__tags">{tags}</div>
</article>"""


#: All user-facing strings, keyed by language. Kept here rather than in the
#: markdown pages so the two languages cannot drift apart structurally.
LABELS: dict[str, dict[str, str]] = {
    "sv": {
        "login": " (kräver inloggning)",
        "to_service": "Till tjänsten",
        "about": "Om tjänsten",
        "close": "Stäng",
        "empty": "Inga tjänster är inlagda ännu. Lägg en markdownfil i mappen "
                 "<code>services/</code> så visas den här.",
        "search": "Sök tjänst, leverantör eller tagg…",
        "search_label": "Sök",
        "provider": "Alla leverantörer",
        "group": "Alla funktionsgrupper",
        "type": "Alla tjänstetyper",
        "reset": "Rensa",
        "noresults": "Inga tjänster matchar filtret.",
        "of": "av",
        "items": "tjänster",
    },
    "en": {
        "login": " (sign-in required)",
        "to_service": "To the service",
        "about": "About the service",
        "close": "Close",
        "empty": "No services are registered yet. Add a markdown file in the "
                 "<code>services/</code> folder and it will appear here.",
        "search": "Search service, provider or tag…",
        "search_label": "Search",
        "provider": "All providers",
        "group": "All function groups",
        "type": "All service types",
        "reset": "Clear",
        "noresults": "No services match the filter.",
        "of": "of",
        "items": "services",
    },
}

DEFAULT_LANG = "en"
SWEDISH_PREFIX = "sv/"


def _modal_sections_html(service: dict[str, Any]) -> str:
    """Render the expandable Access / Guides / About sections of a modal."""
    return "".join(
        f'<details class="svc-section"><summary>{html.escape(section["title"])}</summary>'
        f'<div class="svc-section__body">{section["html"]}</div></details>'
        for section in service["sections"]
    )


def _modal_actions_html(service: dict[str, Any], labels: dict[str, str]) -> str:
    """Render the modal's action buttons.

    "About the service" always exists (it is the generated service page); the
    external link is optional and is annotated when sign-in is required, so a
    researcher knows before clicking.
    """
    external = ""
    if service["link"]:
        login_note = labels["login"] if service["link_login"] else ""
        external = (
            f'<a class="svc-btn svc-btn--primary" href="{_attr(service["link"])}">'
            f'{labels["to_service"]}{login_note}</a>'
        )
    return (
        f'<a class="svc-btn" href="{service["page"]}">{labels["about"]}</a>\n      {external}'
    )


def _modal_html(service: dict[str, Any], labels: dict[str, str]) -> str:
    """Render the modal window for one service.

    Modals are rendered for every service up front (hidden) rather than built
    on demand: the content is static, and pre-rendering keeps the JavaScript
    free of any templating.
    """
    tags = "".join(_tag_html(tag) for tag in service["tags"])
    return f"""<div class="svc-modal" id="svc-modal-{service['id']}" role="dialog" aria-modal="true"
  aria-labelledby="svc-modal-title-{service['id']}" hidden>
  <div class="svc-modal__backdrop" data-close="{service['id']}"></div>
  <div class="svc-modal__panel">
    <button type="button" class="svc-modal__close" data-close="{service['id']}" aria-label="{labels['close']}">&times;</button>
    <p class="svc-modal__icon">{_icon_html(service['icon'])}</p>
    <h2 class="svc-modal__title" id="svc-modal-title-{service['id']}">{html.escape(service['name'])}</h2>
    <p class="svc-modal__provider">{_value_html(service['provider'])}</p>
    <p class="svc-modal__summary">{_value_html(service['summary'])}</p>
    <div class="svc-modal__tags">{tags}</div>
    <div class="svc-modal__sections">{_modal_sections_html(service)}</div>
    <div class="svc-modal__actions">
      {_modal_actions_html(service, labels)}
    </div>
  </div>
</div>"""


def _options(values: Iterable[str]) -> str:
    """Render dropdown `<option>`s, de-duplicated by slug and sorted by label.

    The dropdowns are derived from the service files themselves — adding a new
    provider or function group in a markdown file is all it takes for it to
    appear as a filter. MISSING is skipped: "uppgift saknas" is not a filter.
    """
    seen: dict[str, str] = {}
    for label in values:
        if label and label != MISSING:
            seen.setdefault(_slug(label), label)
    return "".join(
        f'<option value="{_attr(value)}">{html.escape(label)}</option>'
        for value, label in sorted(seen.items(), key=lambda item: item[1].lower())
    )


def _filters_html(services: list[dict[str, Any]], labels: dict[str, str]) -> str:
    """Render the search field, the three dropdowns and the clear button.

    `onsubmit="return false"` keeps Enter in the search field from reloading
    the page — filtering is live on input.
    """
    providers = _options(service["provider"] for service in services)
    groups = _options(service["group"] for service in services)
    types = _options(service["type"] for service in services)
    return f"""<form class="svc-filters" role="search" onsubmit="return false;">
    <input type="search" class="svc-filters__search" name="q" placeholder="{labels['search']}" aria-label="{labels['search_label']}">
    <select name="provider" aria-label="{labels['provider']}"><option value="">{labels['provider']}</option>{providers}</select>
    <select name="group" aria-label="{labels['group']}"><option value="">{labels['group']}</option>{groups}</select>
    <select name="type" aria-label="{labels['type']}"><option value="">{labels['type']}</option>{types}</select>
    <button type="button" class="svc-filters__reset" disabled>{labels['reset']}</button>
  </form>"""


def _archive_html(services: list[dict[str, Any]], labels: dict[str, str]) -> str:
    """Render the complete archive block that replaces the marker."""
    if not services:
        return f'<p class="svc-empty">{labels["empty"]}</p>'

    cards = "".join(_card_html(service) for service in services)
    modals = "".join(_modal_html(service, labels) for service in services)

    return f"""<div class="svc-archive" data-count="{len(services)}"
  data-label-of="{labels['of']}" data-label-items="{labels['items']}">
  {_filters_html(services, labels)}
  <p class="svc-count" aria-live="polite"></p>
  <div class="svc-grid">{cards}</div>
  <p class="svc-noresults" hidden>{labels['noresults']}</p>
  <div class="svc-modals">{modals}</div>
</div>"""


# --------------------------------------------------------------------------- #
# MkDocs entry point
# --------------------------------------------------------------------------- #


def on_page_markdown(markdown: str, page: Any, config: Any, files: Any, **kwargs: Any) -> str:
    """MkDocs hook: replace the archive marker with the generated catalogue.

    Args:
        markdown: The page source. Returned unchanged unless it holds MARKER.
        page: The MkDocs page; its `file.src_path` gives both the language and
            the folder to scan for service files.
        config: The MkDocs config, used for `docs_dir`.
        files: Unused; part of the MkDocs hook signature.

    Returns:
        The page markdown, with the marker replaced by raw HTML.
    """
    if MARKER not in markdown:
        return markdown
    src = page.file.src_path.replace(os.sep, "/")
    lang = "sv" if src.startswith(SWEDISH_PREFIX) else DEFAULT_LANG
    services = _collect(page, config)
    return markdown.replace(MARKER, _archive_html(services, LABELS[lang]))
