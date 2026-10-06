## Detta Workspace välkomnar ditt bidrag!

Vi älskar feedback, och särskilt i form av bidrag som vi kan införliva på arbetsytan.

E-posta oss ditt bidrag eller dina frågor och förslag på <data-info@kth.se>.

Lade du märke till att [källkoden för den här webbplatsen delas öppet på Github](https://github.com/KTH-Library/kth-digital-research-handbook)?
Tveka inte - [öppna ett ärende](https://github.com/KTH-Library/kth-digital-research-handbook/issues) eller
[skicka oss en PR](https://github.com/KTH-Library/kth-digital-research-handbook/pulls) med
ditt bidrag, din fråga eller felrapport!

Alla bidrag kommer att granskas av Datahub-teamet innan de publiceras på denna arbetsplats.

Vi planerar att inom kort erbjuda fler sätt att skicka in dina bidrag - om du
har några förslag på hur vi bör ta emot bidrag, tveka inte att höra av dig.



### Så här lägger du till en artikel eller guide till Workspacet

1. Skapa din Markdown-fil i en lämplig mapp under `docs/sv/`
   (vi antar att du skriver en svenskspråkig text, men detsamma gäller
   för din engelska översättning).
   Anta till exempel att du har skapat `docs/sv/methodologies/optogenetics.md`.
2. Lägg till ditt dokuments sökväg och titel till den svenskspråkiga variabeln `nav` i `mkdocs.yml`.
3. Lägg till en hyperlänk till ditt dokument i `docs/sv/index.md`.

För din engelskspråkiga version av din artikel/guide, gör samma sak men helt ersätt
`docs/sv` med `docs/en`.

> OBS! Dokumentets filnamn på båda språken måste vara detsamma!
> (Såvitt jag förstår är detta en begränsning från MkDocs).

Om du vill, [rendera Workspace-sajten i din lokala webbläsare](https://github.com/KTH-Library/kth-datahub-workspace/tree/master#local-development).

När du är nöjd med dina förändringar och vill dela dem med oss och världen,
checka in dina ändringar i ditt lokala Git-förråd och *pusha* sedan dina *commits*
till ditt eget Git-förråd på GitHub.
På GitHub skapar du sedan en *pull request* från din *branch* till vår.

Obs! Detta Workspace använder [MkDocs webbplatsgenerator](https://www.mkdocs.org/user-guide/writing-your-docs)
under huven.
