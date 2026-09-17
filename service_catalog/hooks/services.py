"""MkDocs hook: builds the digital services archive.

Every service is a single markdown file in <lang>/knowledge_base/services/.
Dropping a new file in that folder is enough: it shows up as a card on the
services overview page, becomes searchable and filterable, gets colour-coded
clickable tags, and is published as its own "About the service" page.

The overview page opts in by containing the marker <!-- SERVICES_ARCHIVE -->.
"""

from __future__ import annotations

import html
import json
import logging
import os
import re

import markdown as md_lib
import yaml

log = logging.getLogger("mkdocs.hooks.services")

MARKER = "<!-- SERVICES_ARCHIVE -->"
SERVICES_DIRNAME = ""
MISSING = "uppgift saknas"

# Which front matter keys become tags, and the colour class they get.
TAG_GROUPS = (
    ("provider", "provider"),
    ("group", "group"),
    ("type", "type"),
    ("data", "data"),
    ("location", "location"),
)

REQUIRED = ("name", "provider", "group", "summary")

_FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def _md():
    return md_lib.Markdown(
        extensions=["admonition", "attr_list", "md_in_html", "tables", "pymdownx.details"]
    )


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _as_list(value) -> list:
    if value is None or value == "":
        return []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value if str(v).strip()]
    return [str(value)]


def _split_sections(body: str) -> list[tuple[str, str]]:
    """Split the markdown body into (heading, markdown) pairs on '## '."""
    sections: list[tuple[str, str]] = []
    current_title = None
    buffer: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current_title is not None:
                sections.append((current_title, "\n".join(buffer).strip()))
            current_title = line[3:].strip()
            buffer = []
        else:
            if current_title is None:
                continue
            buffer.append(line)
    if current_title is not None:
        sections.append((current_title, "\n".join(buffer).strip()))
    return sections


def _parse_service(path: str, docs_dir: str) -> dict | None:
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

    body = raw[match.end():]

    for key in REQUIRED:
        if not meta.get(key):
            log.warning("services: %s is missing '%s' — rendered as '%s'", path, key, MISSING)

    rel = os.path.relpath(path, docs_dir).replace(os.sep, "/")
    # docs/en/knowledge_base/services/x.md -> ../knowledge_base/services/x/ from the overview page
    url = re.sub(r"\.md$", "/", os.path.basename(path))

    tags = []
    for key, kind in TAG_GROUPS:
        for label in _as_list(meta.get(key)):
            tags.append({"label": label, "kind": kind, "value": _slug(label)})

    sections = []
    for title, section_md in _split_sections(body):
        sections.append({"title": title, "html": _md().convert(section_md)})

    service = {
        "id": _slug(os.path.splitext(os.path.basename(path))[0]),
        "name": meta.get("name") or MISSING,
        "icon": meta.get("icon") or "material/apps",
        "provider": meta.get("provider") or MISSING,
        "group": meta.get("group") or MISSING,
        "type": meta.get("type") or "",
        "summary": meta.get("summary") or MISSING,
        "access": meta.get("access") or MISSING,
        "link": meta.get("link") or "",
        "link_login": bool(meta.get("link_requires_login")),
        "page": url,
        "tags": tags,
        "sections": sections,
        "source": rel,
    }
    service["search"] = " ".join(
        [service["name"], service["provider"], service["group"], service["type"],
         service["summary"], service["access"]]
        + [t["label"] for t in tags]
    ).lower()
    return service


def _collect(page, config) -> list[dict]:
    docs_dir = config["docs_dir"]
    page_dir = os.path.dirname(os.path.join(docs_dir, page.file.src_path))
    services_dir = page_dir
    if not os.path.isdir(services_dir):
        return []

    services = []
    for name in sorted(os.listdir(services_dir)):
        if not name.endswith(".md") or name.startswith("_") or name == "index.md":
            continue
        service = _parse_service(os.path.join(services_dir, name), docs_dir)
        if service:
            services.append(service)
    services.sort(key=lambda s: (s["provider"].lower(), s["name"].lower()))
    return services


def _icon_html(icon: str) -> str:
    """Inline the Material icon SVG so it renders inside raw HTML blocks."""
    try:
        import material

        base = os.path.join(os.path.dirname(material.__file__), "templates", ".icons")
        path = os.path.join(base, *f"{icon}.svg".split("/"))
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as handle:
                return f'<span class="svc-icon">{handle.read()}</span>'
    except Exception:  # pragma: no cover - icon is decorative
        pass
    log.warning("services: icon '%s' not found", icon)
    return '<span class="svc-icon"></span>'



def _tag_html(tag: dict) -> str:
    return (
        f'<button type="button" class="svc-tag svc-tag--{tag["kind"]}" '
        f'data-tag-kind="{tag["kind"]}" data-tag-value="{html.escape(tag["value"], quote=True)}">'
        f'{html.escape(tag["label"])}</button>'
    )


def _value_html(value: str) -> str:
    if value == MISSING:
        return f'<span class="svc-missing">{MISSING}</span>'
    return html.escape(value)


def _card_html(service: dict) -> str:
    tags = "".join(_tag_html(t) for t in service["tags"])
    return f"""<article class="svc-card" id="svc-card-{service['id']}"
  data-id="{service['id']}"
  data-provider="{html.escape(_slug(service['provider']), quote=True)}"
  data-group="{html.escape(_slug(service['group']), quote=True)}"
  data-type="{html.escape(_slug(service['type']), quote=True)}"
  data-tags="{html.escape(' '.join(t['value'] for t in service['tags']), quote=True)}"
  data-search="{html.escape(service['search'], quote=True)}">
  <button type="button" class="svc-card__open" data-open="{service['id']}">
    <span class="svc-card__icon">{_icon_html(service['icon'])}</span>
    <span class="svc-card__title">{html.escape(service['name'])}</span>
    <span class="svc-card__provider">{_value_html(service['provider'])}</span>
    <span class="svc-card__summary">{_value_html(service['summary'])}</span>
  </button>
  <div class="svc-card__tags">{tags}</div>
</article>"""


LABELS = {
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


def _modal_html(service: dict, t: dict) -> str:
    tags = "".join(_tag_html(x) for x in service["tags"])
    sections = "".join(
        f'<details class="svc-section"><summary>{html.escape(s["title"])}</summary>'
        f'<div class="svc-section__body">{s["html"]}</div></details>'
        for s in service["sections"]
    )
    link = ""
    if service["link"]:
        login = t["login"] if service["link_login"] else ""
        link = (
            f'<a class="svc-btn svc-btn--primary" href="{html.escape(service["link"], quote=True)}">'
            f'{t["to_service"]}{login}</a>'
        )
    return f"""<div class="svc-modal" id="svc-modal-{service['id']}" role="dialog" aria-modal="true"
  aria-labelledby="svc-modal-title-{service['id']}" hidden>
  <div class="svc-modal__backdrop" data-close="{service['id']}"></div>
  <div class="svc-modal__panel">
    <button type="button" class="svc-modal__close" data-close="{service['id']}" aria-label="{t['close']}">&times;</button>
    <p class="svc-modal__icon">{_icon_html(service['icon'])}</p>
    <h2 class="svc-modal__title" id="svc-modal-title-{service['id']}">{html.escape(service['name'])}</h2>
    <p class="svc-modal__provider">{_value_html(service['provider'])}</p>
    <p class="svc-modal__summary">{_value_html(service['summary'])}</p>
    <div class="svc-modal__tags">{tags}</div>
    <div class="svc-modal__sections">{sections}</div>
    <div class="svc-modal__actions">
      <a class="svc-btn" href="{service['page']}">{t['about']}</a>
      {link}
    </div>
  </div>
</div>"""


def _options(values) -> str:
    seen = {}
    for label in values:
        if label and label != MISSING:
            seen.setdefault(_slug(label), label)
    return "".join(
        f'<option value="{html.escape(value, quote=True)}">{html.escape(label)}</option>'
        for value, label in sorted(seen.items(), key=lambda kv: kv[1].lower())
    )


def _archive_html(services: list[dict], t: dict) -> str:
    if not services:
        return f'<p class="svc-empty">{t["empty"]}</p>'

    providers = _options(s["provider"] for s in services)
    groups = _options(s["group"] for s in services)
    types = _options(s["type"] for s in services)

    cards = "".join(_card_html(s) for s in services)
    modals = "".join(_modal_html(s, t) for s in services)

    return f"""<div class="svc-archive" data-count="{len(services)}"
  data-label-of="{t['of']}" data-label-items="{t['items']}">
  <form class="svc-filters" role="search" onsubmit="return false;">
    <input type="search" class="svc-filters__search" name="q" placeholder="{t['search']}" aria-label="{t['search_label']}">
    <select name="provider" aria-label="{t['provider']}"><option value="">{t['provider']}</option>{providers}</select>
    <select name="group" aria-label="{t['group']}"><option value="">{t['group']}</option>{groups}</select>
    <select name="type" aria-label="{t['type']}"><option value="">{t['type']}</option>{types}</select>
    <button type="button" class="svc-filters__reset" disabled>{t['reset']}</button>
  </form>
  <p class="svc-count" aria-live="polite"></p>
  <div class="svc-grid">{cards}</div>
  <p class="svc-noresults" hidden>{t['noresults']}</p>
  <div class="svc-modals">{modals}</div>
</div>"""


def on_page_markdown(markdown, page, config, files, **kwargs):
    if MARKER not in markdown:
        return markdown
    src = page.file.src_path.replace(os.sep, "/")
    lang = "sv" if src.startswith("sv/") else "en"
    services = _collect(page, config)
    return markdown.replace(MARKER, _archive_html(services, LABELS[lang]))

