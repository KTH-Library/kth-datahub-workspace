---
name: KTH Data Repository
icon: material/archive-lock
provider: KTH Library & IT
group: RDM
type: service
data: Research data
tags:
  - FAIR
  - archive
location: Sweden
summary: >
   KTH's official institutional archive for research data, software, and related outputs.
   Supports sharing of restricted datasets, i.e., records with public metadata but
   restricted data.
   Not suitable for day-to-day work files.
link: https://datarepository.kth.se
link_requires_login: false
rating:
  legal:
    status: green
    note: >
      Provided through KTH.
  ip: green
  security:
    status: green
    note: >
      Authentication via KTH SSO and GitHub SSO which are secure, but also
      via ORCID authentication which is not considered as secure.
      The service is not suitable for data with strict confidentiality due to
      absolute secrecy classification.
  cost:
    status: green
    note: Included as part of centrally funded services.
  support:
    status: green
    note: Supported by the Research Data (KTH Library).
---

## Access

Public datasets are visible to the web and indexable by search engines.

The service is available to all staff and PhD students with a KTH account.
No application or extra cost for the individual researcher;
the service is part of the central agreement.

Uploads up to 30 GB per record (max 100 files) by default, but can be increased on request.


## Guides

+ Open <https://datarepository.kth.se> and sign in (use KTH SSO, the other login methods
  are primarily meant to support collaborators and such).
+ Stuck? Read the documentation <https://docs.datarepository.kth.se>.
+ Still stuck? We can help, ask us: <mailto:researchdata@kth.se>.


## About the service

This is an *archive* for KTH's research data, software or any other digitally storable
research outputs.

It *is* suitable for storing or archiving research data containing personal
or otherwise sensitive information, as well as for publicly shareable research data.

The service runs InvenioRDM on KTH infrastructure and is developed
and maintained by KTH Research Data and KTH IT staff.
