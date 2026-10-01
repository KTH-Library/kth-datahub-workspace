---
name: GitHub
icon: material/github
provider: Microsoft
group: RDM
type: Versioning
data: Code
location: Global
summary: >
  Proprietär plattform för delning, lagring och hantering av kod,
  med tillhörande funktioner för samarbeten kring projekt.
access: >
  Många funktioner kräver ett konto, men att skapa ett konto är kostnadsfritt.
  KTH Biblioteket och andra KTH-enheter har institutionella förråd.
link: https://github.com/KTH-Library
link_requires_login: false
rating:
  legal:
    status: yellow
    note: >
      Lämplig för källkod och utveckling i samarbete med andra.
      Delning av personuppgifter eller andra känsliga uppgifter kräver
      bedömning i varje enskilt fall.
  ip:
    status: yellow
    note: >
      Använd inte utan att förstå licensvillkor, vem som äger kod, och
      hur kod från externa parter är licensierad.
  security:
    status: green
    note: >
      Stödjer multifaktor-autentisering och integration med institutionell
      "identity management".
  cost: green
  support: yellow
---

## Åtkomst

Skapa ett personligt konto och be ägaren till aktuell KTH-organisation lägga
till dig. Privata repositorier ingår utan kostnad för akademisk användning.

## Guider

1. Skapa ett repositorium och lägg till `README.md` och en licensfil.
2. Klona lokalt med `git clone` och committa arbetet regelbundet.
3. Använd brancher och pull requests när flera arbetar parallellt.
4. Koppla repositoriet till Zenodo för att få DOI vid varje release.

## Om tjänsten

GitHub passar för kod och textbaserat material. Det ska inte användas för
personuppgifter eller stora binära datamängder. Data lagras globalt, vilket
måste vägas in när projektet har krav på lagringsplats.
