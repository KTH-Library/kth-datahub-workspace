# Ändringslogg — tjänstekatalogen

## 2026-09-17

- **Rättat:** filtrering och sökning dolde inte korten. Korten markerades som
  dolda med attributet `hidden`, men regeln `.svc-card { display: flex }` vann
  över webbläsarens svagare inbyggda `[hidden]`-regel, så alla kort låg kvar
  medan räknaren visade rätt antal. Åtgärdat med en uttrycklig regel
  `.svc-card[hidden] { display: none; }`.
- Hover- och fokusmarkering (`:focus-visible`) för sökfält, rullgardiner,
  kort, taggar, knappar och stängkryss.
- Mörkare taggfärger i ljust läge och ljusare i mörkt läge för läsbar kontrast.
- Utförliga kommentarer och docstrings i generatorn, stilmallen och skriptet,
  inklusive en uttrycklig varning om `hidden`-fällan.
- Generatorn refaktorerad: typannoteringar, namngivna konstanter i stället för
  hårdkodade värden, uppdelade hjälpfunktioner för filter, modalsektioner och
  modalknappar.
- Ny dokumentation i repots rot: `ARCHITECTURE.md`, `SERVICES_PAGE.md`,
  `README_DEVELOPER.md`, `TECHNICAL_DEBT.md`, `AI_DEVELOPMENT_NOTES.md`.

## 2026-09-16

- Tjänstekatalogen samlad i egna mappar: logiken i `service_catalog/`,
  tjänstesidorna i `docs/en/services/` och `docs/sv/services/`,
  stilar i `docs/stylesheets/service_catalog/` och skript i
  `docs/javascripts/service_catalog/`.
- Översiktssida med fritextsökning, rullgardinsfilter, rutnät med kort,
  modal med utfällbara avsnitt och klickbara färgkodade taggar.
- Fem tjänster på både engelska och svenska: KTH OneDrive, Zenodo, GitHub,
  EOSC EU Node storage, Dropbox.
- `not_in_nav` täcker både tjänstesidorna och den gamla `knowledge_base/tools.md`
  så att bygget klarar strikt läge.
- Ändringslogg tillagd.
