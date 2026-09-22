---
name: GitHub
icon: material/github
provider: Microsoft
group: Datahantering
type: Versionshantering
data: Kod
location: Globalt
summary: Version control and collaboration for code, analysis scripts and documentation, with a KTH organisation available.
access: Free accounts for anyone; KTH-Library and other KTH organisations host institutional repositories.
link: https://github.com/KTH-Library
link_requires_login: false

rating:
  legal:
    status: yellow
    note: "Suitable for open-source code and collaboration. Should not be used for classified information or sensitive personal data."

  ip:
    status: yellow
    note: "Requires awareness of the selected licence and the rights of external contributors."

  security:
    status: green
    note: "Supports two-factor authentication (2FA) and KTH SSO through GitHub Enterprise."

  cost: green
  support: yellow

---
## Access

Create a personal account and ask the relevant KTH organisation owner to add
you. Private repositories are included at no cost for academic use.

## Guides

1. Create a repository and add a `README.md` and a licence file.
2. Clone it locally with `git clone` and commit your work regularly.
3. Use branches and pull requests when several people work in parallel.
4. Connect the repository to Zenodo to get a DOI for each release.

## About the service

GitHub is well suited for code and text-based material. It should not be used
for personal data or large binary datasets. Data stored on GitHub is hosted
globally, which must be considered when the project has location requirements.
