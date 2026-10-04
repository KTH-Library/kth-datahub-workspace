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

from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape as xml_escape

log = logging.getLogger("mkdocs.hooks.services")

MARKER = "<!-- SERVICES_ARCHIVE -->"
SERVICES_DIRNAME = ""
MISSING = "Missing data"

# Which front matter keys become tags, and the colour class they get.
TAG_GROUPS = (
    ("provider", "provider"),
    ("group", "group"),
    ("type", "type"),
    ("data", "data"),
    ("location", "location"),
)

REQUIRED = ("name", "provider", "group", "summary")

# ---------------------------------------------------------------------------
# Traffic light ratings
# ---------------------------------------------------------------------------

# Critical dimensions determine the overall traffic light
CRITICAL_RATINGS = ("legal", "ip", "security")
NON_CRITICAL_RATINGS = ("cost", "support")

# Normalize color variants (both Swedish and English) to standard tokens
RATING_COLORS = {
    "green": "green", "gron": "green", "grön": "green",
    "yellow": "yellow", "gul": "yellow",
    "red": "red", "rod": "red", "röd": "red",
    "grey": "grey", "gray": "grey", "gra": "grey", "grå": "grey",
}

# Aliases to allow Swedish keys in markdown front matter
RATING_KEY_ALIASES = {
    "juridik": "legal",
    "kostnad": "cost",
    "sakerhet": "security",
    "säkerhet": "security",
}

RATING_LABELS = {
    "sv": {
        "legal": "Juridik & GDPR",
        "ip": "Immateriella rättigheter (IP)",
        "cost": "Kostnadsmodell",
        "security": "Informationssäkerhet",
        "support": "Support & Tillgänglighet",
        "green": "Inga kända väsentliga risker",
        "yellow": "Risker eller villkor identifierade",
        "red": "Betydande risker identifierade",
        "grey": "Under utredning / partiell bedömning",
        "missing": "Bedömning saknas",
        "traffic_light": "Övergripande riskbild",
    },
    "en": {
        "legal": "Legal & GDPR",
        "ip": "Intellectual Property (IP)",
        "cost": "Cost Model",
        "security": "Information Security",
        "support": "Support & Availability",
        "green": "No significant known risks",
        "yellow": "Risks or conditions identified",
        "red": "Significant risks identified",
        "grey": "Under review / partial assessment",
        "missing": "Assessment unavailable",
        "traffic_light": "Overall Risk Profile",
    },
}
# Icons for modal collapsible sections
SECTION_ICONS = {
    # Svenska
    "åtkomst": "material/key",
    "om tjänsten": "material/book-open-page-variant",
    "guider": "material/compass-outline",
    "support": "material/help-circle-outline",
    # Engelska
    "access": "material/key",
    "about the service": "material/book-open-page-variant",
    "about": "material/book-open-page-variant",
    "guides": "material/compass-outline",
    "support": "material/help-circle-outline",
}
DEFAULT_SECTION_ICON = "material/text-box-outline"


def _section_icon(title: str) -> str:
    """Return an inlined SVG icon corresponding to the section title."""
    clean_title = title.lower().strip()
    icon_name = SECTION_ICONS.get(clean_title, DEFAULT_SECTION_ICON)
    return _icon_html(icon_name)


def normalize_ratings(raw_ratings: dict) -> dict[str, dict[str, str]]:
    """Normalize rating keys, color values, and optional explanatory notes.
    
    Supports both compact format:
        legal: green
    and detailed format with note:
        legal:
          status: green
          note: "Approved by KTH legal team."
    """
    if not isinstance(raw_ratings, dict):
        return {}
    normalized = {}
    for key, val in raw_ratings.items():
        clean_key = RATING_KEY_ALIASES.get(str(key).lower().strip(), str(key).lower().strip())
        status_val = None
        note_val = ""

        if isinstance(val, dict):
            raw_status = val.get("status") or val.get("color") or val.get("farg") or val.get("färg")
            status_val = RATING_COLORS.get(str(raw_status).lower().strip()) if raw_status else None
            raw_note = val.get("note") or val.get("kommentar") or val.get("beskrivning") or ""
            note_val = str(raw_note).strip()
        elif isinstance(val, str):
            status_val = RATING_COLORS.get(val.lower().strip())

        if status_val:
            normalized[clean_key] = {"status": status_val, "note": note_val}
    return normalized


def calculate_overall_rating(ratings: dict[str, dict[str, str]]) -> str | None:
    """Calculate overall traffic light badge:

    1. If no ratings exist at all -> return None (no badge shown)
    2. Any critical is red -> red
    3. Any critical is yellow -> yellow
    4. Any critical is grey or missing -> grey (partial assessment)
    5. All critical are green -> green
    """
    if not ratings:
        return None

    critical_values = [
        ratings[dim]["status"] if dim in ratings else None
        for dim in CRITICAL_RATINGS
    ]

    # Red always surfaces immediately
    if "red" in critical_values:
        return "red"
    # Yellow surfaces if no red
    if "yellow" in critical_values:
        return "yellow"
    # If any critical dimension is missing or explicitly grey -> grey
    if any(val is None or val == "grey" for val in critical_values):
        return "grey"
    # Only if all critical dimensions are green
    if all(val == "green" for val in critical_values):
        return "green"

    return "grey"



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

    raw_ratings = meta.get("rating") or meta.get("ratings") or {}
    norm_ratings = normalize_ratings(raw_ratings)
    overall_rating = calculate_overall_rating(norm_ratings)

    # Extrahera uppdateringsdatum FÖRE vi bygger service-dicten
    raw_date = meta.get("last_updated") or meta.get("updated") or meta.get("date")
    parsed_date = None
    if raw_date:
        try:
            if isinstance(raw_date, datetime):
                parsed_date = raw_date if raw_date.tzinfo else raw_date.replace(tzinfo=timezone.utc)
            elif hasattr(raw_date, "isoformat"):
                parsed_date = datetime.combine(raw_date, datetime.min.time(), tzinfo=timezone.utc)
            else:
                dt = datetime.strptime(str(raw_date).strip()[:10], "%Y-%m-%d")
                parsed_date = dt.replace(tzinfo=timezone.utc)
        except Exception:
            parsed_date = None

    if not parsed_date:
        mtime = os.path.getmtime(path)
        parsed_date = datetime.fromtimestamp(mtime, tz=timezone.utc)

    service = {
        "id": _slug(os.path.splitext(os.path.basename(path))[0]),
        "name": meta.get("name") or MISSING,
        "icon": meta.get("icon") or "material/apps",
        "provider": meta.get("provider") or MISSING,
        "group": meta.get("group") or MISSING,
        "type": (
            str(meta.get("card_type") or meta.get("type") or "service").lower().strip()
            if str(meta.get("card_type") or meta.get("type") or "").lower().strip() in ("guide", "checklist", "support")
            else "service"
        ),
        "summary": meta.get("summary") or MISSING,
        "access": meta.get("access") or MISSING,
        "link": meta.get("link") or meta.get("url") or "",
        "button_text": str(meta.get("button_text") or meta.get("button_label") or "").strip(),
        "link_login": bool(meta.get("link_requires_login")),
        "ratings": norm_ratings,           
        "overall_rating": overall_rating,   
        "page": url,
        "tags": tags,
        "sections": sections,
        "related": _as_list(meta.get("related")),
        "date": parsed_date,
        "source": rel,
    }

    
    # Extrahera uppdateringsdatum (frontmatter 'last_updated', 'updated', 'date' eller filens mtime)
    raw_date = meta.get("last_updated") or meta.get("updated") or meta.get("date")
    parsed_date = None
    if raw_date:
        try:
            # Stöd både YYYY-MM-DD och datetime-objekt från PyYAML
            if isinstance(raw_date, datetime):
                parsed_date = raw_date if raw_date.tzinfo else raw_date.replace(tzinfo=timezone.utc)
            elif hasattr(raw_date, "isoformat"):  # t.ex. datetime.date
                parsed_date = datetime.combine(raw_date, datetime.min.time(), tzinfo=timezone.utc)
            else:
                dt = datetime.strptime(str(raw_date).strip()[:10], "%Y-%m-%d")
                parsed_date = dt.replace(tzinfo=timezone.utc)
        except Exception:
            parsed_date = None

    if not parsed_date:
        # Fallback till filens ändringsdatum
        mtime = os.path.getmtime(path)
        parsed_date = datetime.fromtimestamp(mtime, tz=timezone.utc)

    service["search"] = " ".join(
        [service["name"], service["provider"], service["group"], service["type"],
         service["summary"], service["access"]]
        + [t["label"] for t in tags]
    ).lower()
    return service


def _scan_dir(target_dir: str, docs_dir: str) -> dict[str, dict]:
    """Skannar en specifik underkatalog och returnerar en dict med {id: service}."""
    res = {}
    if not os.path.isdir(target_dir):
        return res
    for root, _, files in os.walk(target_dir):
        for name in sorted(files):
            if not name.endswith(".md") or name.startswith("_") or name == "index.md":
                continue
            svc = _parse_service(os.path.join(root, name), docs_dir)
            if svc:
                res[svc["id"]] = svc
    return res


def _collect(page, config) -> list[dict]:
    docs_dir = config["docs_dir"]
    page_dir = os.path.dirname(os.path.join(docs_dir, page.file.src_path))
    
    # Identifiera nuvarande språk ("sv" eller "en")
    is_sv = "/sv/" in page.file.src_path or page.file.src_path.startswith("sv/")
    current_lang = "sv" if is_sv else "en"
    other_lang = "en" if is_sv else "sv"

    # Hitta katalogerna för båda språken
    current_dir = page_dir
    other_dir = page_dir.replace(f"/{current_lang}/", f"/{other_lang}/")

    current_services = _scan_dir(current_dir, docs_dir)
    other_services = _scan_dir(other_dir, docs_dir)

    # Bygg den sammanslagna listan: primära språket först
    services_dict = dict(current_services)

    # Lägg till saknade resurser från det andra språket som fallback
    for svc_id, svc in other_services.items():
        if svc_id not in services_dict:
            fallback_svc = dict(svc)
            fallback_svc["is_fallback"] = True
            fallback_svc["original_lang"] = other_lang
            services_dict[svc_id] = fallback_svc

    services = list(services_dict.values())
    services.sort(key=lambda s: (s["provider"].lower(), s["name"].lower()))
    _link_relations(services)
    return services


def _link_relations(services: list[dict]) -> None:
    """Resolve bidirectional relations between cards."""
    by_id = {s["id"]: s for s in services}

    # 1. Korskoppla: Om A länkar till B, se till att B också länkar till A
    for s in services:
        for target_id in list(s.get("related", [])):
            if target_id in by_id:
                target = by_id[target_id]
                if s["id"] not in target["related"]:
                    target["related"].append(s["id"])

    # 2. Skapa färdiga objekt så modalen enkelt kan rita ut knapparna
    for s in services:
        s["related_items"] = [
            {
                "id": rid,
                "name": by_id[rid]["name"],
                "type": by_id[rid].get("type", "service"),
                "icon": by_id[rid]["icon"],
            }
            for rid in s.get("related", [])
            if rid in by_id and rid != s["id"]
        ]


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


def _card_html(service: dict, lang: str = "sv") -> str:
    tags = "".join(_tag_html(t) for t in service["tags"])
    
    traffic_html = ""
    color = service.get("overall_rating")
    if color:
        labels = RATING_LABELS.get(lang, RATING_LABELS["sv"])
        desc = labels.get(color, color)
        traffic_html = (
            f'<span class="svc-traffic-badge svc-traffic-badge--{color}" '
            f'title="{labels["traffic_light"]}: {desc}"></span>'
        )

    # Språk-badge om resursen visas som fallback från det andra språket
    badge_lang = ""
    if service.get("is_fallback"):
        orig = service.get("original_lang")
        badge_text = "In English" if orig == "en" else "På svenska"
        badge_lang = f' <span class="svc-badge-lang">{badge_text}</span>'

    return f"""<article class="svc-card" id="svc-card-{service['id']}"
  data-id="{service['id']}"
  data-provider="{html.escape(_slug(service['provider']), quote=True)}"
  data-group="{html.escape(_slug(service['group']), quote=True)}"
  data-type="{html.escape(_slug(service['type']), quote=True)}"
  data-rating="{color or ''}"
  data-tags="{html.escape(' '.join(t['value'] for t in service['tags']), quote=True)}"
  data-search="{html.escape(service['search'], quote=True)}">
  <button type="button" class="svc-card__open" data-open="{service['id']}">
    {traffic_html}
    <span class="svc-card__icon svc-card__icon--{service['type']}">{_icon_html(service['icon'])}</span>
    <span class="svc-card__title">{html.escape(service['name'])}{badge_lang}</span>
    <span class="svc-card__provider">{_value_html(service['provider'])}</span>
    <span class="svc-card__summary">{_value_html(service['summary'])}</span>
  </button>
  <div class="svc-card__tags">{tags}</div>
</article>"""




LABELS = {
    "sv": {
        "login": " (kräver inloggning)",
        "to_service": "Öppna tjänsten",
        "more_info": "Mer information",
        "to_resource": "Öppna extern resurs",
        "contact_support": "Kontakta stödet",
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
        "to_service": "Open service",
        "more_info": "More information",
        "to_resource": "Open external resource",
        "contact_support": "Contact support",
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


def _modal_html(service: dict, t: dict, lang: str = "sv") -> str:
    tags = "".join(_tag_html(x) for x in service["tags"])
    sections = "".join(
        f'<details class="svc-section">'
        f'<summary>'
        f'{_section_icon(s["title"])}'
        f'<span class="svc-section__title">{html.escape(s["title"])}</span>'
        f'</summary>'
        f'<div class="svc-section__body">{s["html"]}</div>'
        f'</details>'
        for s in service["sections"]
    )

    fallback_notice = ""
    if service.get("is_fallback"):
        orig = service.get("original_lang")
        notice_text = (
            "Denna resurs finns för närvarande endast tillgänglig på engelska."
            if orig == "en"
            else "This resource is currently only available in Swedish."
        )
        fallback_notice = f'<div class="svc-modal__lang-notice">{notice_text}</div>'


    # Build smart primary button based on card type
    link = ""
    target_url = service.get("link") or service.get("url")
    if target_url:
        card_type = service.get("type", "service")
        
        # 1. Bestäm knapptext: antingen specifik button_text eller default per typ
        if service.get("button_text"):
            btn_text = html.escape(service["button_text"])
        elif card_type == "service":
            login = t["login"] if service.get("link_login") else ""
            btn_text = f"{t['to_service']}{login}"
        else:
            btn_text = t["more_info"]

        # 2. Avgör extern vs intern länk (för pil och target="_blank")
        is_external = target_url.startswith("http://") or target_url.startswith("https://")
        target_attr = ' target="_blank" rel="noopener noreferrer"' if is_external else ""
        arrow = "&nbsp;&nearr;" if is_external else "&nbsp;&rarr;"

        link = (
            f'<a class="svc-btn svc-btn--primary" href="{html.escape(target_url, quote=True)}"'
            f'{target_attr}>{btn_text}{arrow}</a>'
        )


    related_html = ""
    if service.get("related_items"):
        rel_label = "Relaterat innehåll" if lang == "sv" else "Related resources"
        rel_cards = []
        for rel in service["related_items"]:
            card_type = rel.get("type", "service")
            rel_cards.append(
                f'<button type="button" class="svc-mini-card svc-mini-card--{card_type}" data-open="{rel["id"]}">'
                f'<div class="svc-mini-card__header">'
                f'<span class="svc-mini-card__icon">{_icon_html(rel["icon"])}</span>'
                f'<span class="svc-mini-card__type">{html.escape(card_type.capitalize())}</span>'
                f'<span class="svc-mini-card__arrow">&rarr;</span>'
                f'</div>'
                f'<div class="svc-mini-card__title">{html.escape(rel["name"])}</div>'
                f'</button>'
            )
        related_html = (
            f'<div class="svc-modal__related">'
            f'<h4>{rel_label}</h4>'
            f'<div class="svc-modal__related-grid">{"".join(rel_cards)}</div>'
            f'</div>'
        )



    # Build expandable risk profile if ratings exist
    ratings_html = ""
    norm_ratings = service.get("ratings", {})
    if norm_ratings:
        labels = RATING_LABELS.get(lang, RATING_LABELS["sv"])
        overall_color = service.get("overall_rating") or "grey"
        overall_desc = labels.get(overall_color, labels["missing"])

        rows = []
        all_dimensions = CRITICAL_RATINGS + NON_CRITICAL_RATINGS
        for dim in all_dimensions:
            dim_title = labels.get(dim, dim.capitalize())
            dim_val = norm_ratings.get(dim)

            if isinstance(dim_val, dict):
                color = dim_val.get("status")
                note = dim_val.get("note", "")
            elif isinstance(dim_val, str):
                color = dim_val
                note = ""
            else:
                color = None
                note = ""

            if color:
                color_label = labels.get(color, color)
                badge_class = f"svc-traffic-badge--{color}"
            else:
                color_label = labels.get("missing", "Missing")
                badge_class = "svc-traffic-badge--missing"

            note_html = (
                f'<p class="svc-modal__rating-note">{html.escape(note)}</p>'
                if note else ""
            )

            rows.append(
                f'<div class="svc-modal__rating-item">'
                f'<div class="svc-modal__rating-header">'
                f'<span class="svc-traffic-badge {badge_class}"></span>'
                f'<span class="svc-modal__rating-dim">{dim_title}</span>'
                f'<span class="svc-modal__rating-val">{color_label}</span>'
                f'</div>'
                f'{note_html}'
                f'</div>'
            )

        ratings_html = (
            f'<details class="svc-modal__ratings-details">'
            f'<summary class="svc-modal__ratings-summary">'
            f'<span class="svc-traffic-badge svc-traffic-badge--{overall_color}"></span>'
            f'<span class="svc-modal__ratings-summary-text">'
            f'<strong>{labels["traffic_light"]}:</strong> {overall_desc}'
            f'</span>'
            f'</summary>'
            f'<div class="svc-modal__rating-list">{"".join(rows)}</div>'
            f'</details>'
        )


    # Informationsbanner i modalen om resursen är på det andra språket
    fallback_notice = ""
    if service.get("is_fallback"):
        orig = service.get("original_lang")
        notice_text = (
            "Denna resurs finns för närvarande endast tillgänglig på engelska."
            if orig == "en"
            else "This resource is currently only available in Swedish."
        )
        fallback_notice = f'<div class="svc-modal__lang-notice">{notice_text}</div>'

    return f"""<div class="svc-modal" id="svc-modal-{service['id']}" role="dialog" aria-modal="true"
  aria-labelledby="svc-modal-title-{service['id']}" hidden>
  <div class="svc-modal__backdrop" data-close="{service['id']}"></div>
  <div class="svc-modal__panel">
    <button type="button" class="svc-modal__close" data-close="{service['id']}" aria-label="{t['close']}">&times;</button>
    <p class="svc-modal__icon">{_icon_html(service['icon'])}</p>
    <h2 class="svc-modal__title" id="svc-modal-title-{service['id']}">{html.escape(service['name'])}</h2>
    {fallback_notice}
    <p class="svc-modal__provider">{_value_html(service['provider'])}</p>
    <p class="svc-modal__summary">{_value_html(service['summary'])}</p>
    <div class="svc-modal__tags">{tags}</div>
    {ratings_html}
    <div class="svc-modal__sections">{sections}</div>
    {related_html}
    <div class="svc-modal__actions">
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


def _archive_html(services: list[dict], t: dict, lang: str = "sv") -> str:
    if not services:
        return f'<p class="svc-empty">{t["empty"]}</p>'

    # 1. Bygg dropdown-options för leverantörer och funktionsgrupper
    providers = _options(s["provider"] for s in services)
    groups = _options(s["group"] for s in services)

    # 2. Samla alla unika taggar och bygg options för tagg-dropdownen
    all_tag_labels = {tag["label"] for s in services for tag in s.get("tags", []) if tag.get("label")}
    tags_options = _options(all_tag_labels)

    cards = "".join(_card_html(s, lang) for s in services)
    modals = "".join(_modal_html(s, t, lang) for s in services)
    type_tabs = _type_tabs_html(services, lang)

    tag_label = "Alla taggar / ämnen" if lang == "sv" else "All topics / tags"
    rss_title = "RSS-flöde för tjänster och guider" if lang == "sv" else "RSS feed for services and guides"
    feed_filename = f"services-{lang}.xml"

    # SVG för klassisk ren RSS-ikon
    rss_svg = (
        '<svg class="svc-rss-icon" viewBox="0 0 24 24" width="16" height="16" '
        'fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M4 11a9 9 0 0 1 9 9"></path>'
        '<path d="M4 4a16 16 0 0 1 16 16"></path>'
        '<circle cx="5" cy="19" r="1.5" fill="currentColor"></circle>'
        '</svg>'
    )

    return f"""<div class="svc-archive" data-count="{len(services)}"
  data-label-of="{t['of']}" data-label-items="{t['items']}">
  {type_tabs}
  <form class="svc-filters" role="search" onsubmit="return false;">
    <input type="search" class="svc-filters__search" name="q" placeholder="{t['search']}" aria-label="{t['search_label']}">
    <select name="provider" aria-label="{t['provider']}"><option value="">{t['provider']}</option>{providers}</select>
    <select name="group" aria-label="{t['group']}"><option value="">{t['group']}</option>{groups}</select>
    <select name="tag" aria-label="{tag_label}"><option value="">{tag_label}</option>{tags_options}</select>
    <button type="button" class="svc-filters__reset" disabled>{t['reset']}</button>
    <a href="../../{feed_filename}" class="svc-filters__rss" title="{rss_title}" aria-label="{rss_title}" target="_blank">
      {rss_svg}
      <span class="svc-filters__rss-label">RSS</span>
    </a>
  </form>
  <p class="svc-count" aria-live="polite"></p>
  <div class="svc-grid">{cards}</div>
  <p class="svc-noresults" hidden>{t['noresults']}</p>
  <div class="svc-modals">{modals}</div>
</div>"""




def _type_tabs_html(services: list[dict], lang: str) -> str:
    counts = {"all": len(services), "service": 0, "guide": 0, "checklist": 0, "support": 0}
    for s in services:
        t = s.get("type", "service")
        if t in counts:
            counts[t] += 1

    labels = {
        "en": {
            "all": "All resources",
            "service": "Tools",
            "guide": "Guides",
            "checklist": "Checklists",
            "support": "Support & Advice"
        },
        "sv": {
            "all": "Alla resurser",
            "service": "Verktyg",
            "guide": "Guider",
            "checklist": "Checklistor",
            "support": "Stöd & Rådgivning"
        }
    }.get(lang, {"all": "All resources", "service": "Services & Tools", "guide": "Guides", "checklist": "Checklists", "support": "Support & Advice"})

    buttons = []
    for t in ["all", "service", "guide", "checklist", "support"]:
        # Visa fliken om det är "all" eller om det finns kort av den typen
        if t != "all" and counts.get(t, 0) == 0:
            continue
            
        active = " is-active" if t == "all" else ""
        label = labels.get(t, t.title())
        count = counts.get(t, 0)
        
        buttons.append(
            f'<button type="button" class="svc-type-tab svc-type-tab--{t}{active}" data-filter-type="{t}">'
            f'<span class="svc-type-tab__label">{label}</span>'
            f'<span class="svc-type-tab__count">{count}</span>'
            f'</button>'
        )

    return f'<div class="svc-type-tabs" role="tablist">{"".join(buttons)}</div>'


def on_page_markdown(markdown, page, config, files, **kwargs):
    if MARKER not in markdown:
        return markdown
    src = page.file.src_path.replace(os.sep, "/")
    lang = "sv" if src.startswith("sv/") else "en"
    services = _collect(page, config)
    return markdown.replace(MARKER, _archive_html(services, LABELS[lang], lang))

def _generate_rss_xml(services: list[dict], site_url: str, lang: str) -> str:
    """Generates an RSS 2.0 feed for digital services and resources."""
    base_url = site_url.rstrip("/")
    feed_url = f"{base_url}/services-{lang}.xml"
    catalog_url = f"{base_url}/{lang}/services/"

    title = (
        "KTH Digitala tjänster & forskningsresurser"
        if lang == "sv"
        else "KTH Digital Services & Research Resources"
    )
    description = (
        "Uppdateringar och nya tillägg bland forskningsnära tjänster och guider vid KTH."
        if lang == "sv"
        else "Updates and additions across research services and guides at KTH."
    )

    now_rfc822 = format_datetime(datetime.now(timezone.utc))

    # Sortera så nyast uppdaterade kommer överst
    sorted_services = sorted(
        services,
        key=lambda s: s.get("date") or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )

    items_xml = []
    for s in sorted_services:
        item_id = s.get("id", "")
        item_link = f"{catalog_url}?service={item_id}"
        
        # Markera eventuell cross-language fallback i titeln
        item_title = str(s.get("name") or item_id)
        if s.get("is_fallback"):
            item_title += " [In English]" if s.get("original_lang") == "en" else " [På svenska]"

        # Formatera pubDate till RFC-822
        pub_dt = s.get("date")
        if isinstance(pub_dt, datetime):
            pub_date_str = format_datetime(pub_dt)
            guid_suffix = pub_dt.strftime("%Y-%m-%d")
        else:
            pub_date_str = now_rfc822
            guid_suffix = "latest"

        guid = f"{base_url}/{lang}/services/{item_id}#{guid_suffix}"
        item_desc = str(s.get("summary") or s.get("description") or "")

        # Kategorier: provider, typ samt eventuella tagg-labels (aldrig dict-objekt eller 'Missing data')
        categories: list[str] = []
        
        prov = s.get("provider")
        if prov and prov != MISSING and prov not in categories:
            categories.append(str(prov))
            
        stype = s.get("type")
        if stype and stype != MISSING and stype not in categories:
            categories.append(str(stype))

        for t in s.get("tags") or []:
            # t är en dict {"label": ..., "kind": ..., "value": ...}
            t_label = t.get("label") if isinstance(t, dict) else str(t)
            if t_label and t_label != MISSING and t_label not in categories:
                categories.append(str(t_label))

        cat_elements = "\n".join(
            f"      <category>{xml_escape(cat)}</category>" for cat in categories
        )

        items_xml.append(f"""    <item>
      <title>{xml_escape(item_title)}</title>
      <link>{xml_escape(item_link)}</link>
      <guid isPermaLink="false">{xml_escape(guid)}</guid>
      <pubDate>{pub_date_str}</pubDate>
      <description>{xml_escape(item_desc)}</description>
{cat_elements}
    </item>""")

    joined_items = "\n".join(items_xml)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{xml_escape(title)}</title>
    <link>{xml_escape(catalog_url)}</link>
    <description>{xml_escape(description)}</description>
    <language>{lang}</language>
    <lastBuildDate>{now_rfc822}</lastBuildDate>
    <atom:link href="{xml_escape(feed_url)}" rel="self" type="application/rss+xml" />
{joined_items}
  </channel>
</rss>
"""


def on_post_build(config, **kwargs):
    """Skriver RSS 2.0 XML-filer till site_dir efter att sajten byggts."""
    site_dir = config["site_dir"]
    docs_dir = config["docs_dir"]
    site_url = config.get("site_url") or ""

    for lang in ("sv", "en"):
        # Hitta katalogen för språket
        lang_services_dir = os.path.join(docs_dir, lang, "services")
        other_lang = "en" if lang == "sv" else "sv"
        other_services_dir = os.path.join(docs_dir, other_lang, "services")

        current_services = _scan_dir(lang_services_dir, docs_dir)
        other_services = _scan_dir(other_services_dir, docs_dir)

        services_dict = dict(current_services)
        for svc_id, svc in other_services.items():
            if svc_id not in services_dict:
                fb = dict(svc)
                fb["is_fallback"] = True
                fb["original_lang"] = other_lang
                services_dict[svc_id] = fb

        services = list(services_dict.values())
        rss_content = _generate_rss_xml(services, site_url, lang)

        out_path = os.path.join(site_dir, f"services-{lang}.xml")
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(rss_content)
            log.info("services: wrote RSS feed to %s", out_path)
        except Exception as e:
            log.error("services: failed to write RSS feed %s: %s", out_path, e)


