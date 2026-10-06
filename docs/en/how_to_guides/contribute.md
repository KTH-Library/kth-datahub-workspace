## This workspace is open for your contributions!

We love feedback, and especially in the form of contributions that we can
incorporate on the workspace.

Send us an email with your contribution, questions, suggestions, or simply to point out
a mistake of ours that you spotted at <data-info@kth.se>.

Did you notice that the full [source code for this site is shared on Github](https://github.com/KTH-Library/kth-digital-research-handbook)?
Don't be shy - [create an issue](https://github.com/KTH-Library/kth-digital-research-handbook/issues) or
[send us a pull request](https://github.com/KTH-Library/kth-digital-research-handbook/pulls) with
your contribution, question or bug report!

Contributions will naturally be subject to review by the Datahub team before incorporation
on this workspace.

We plan to offer more ways to submit your contributions in the near future - if you
have any suggestions on how we should receive contributions, please let us know.


### How to add an article or guide to the Workspace

1. Create your Markdown file in a suitable folder under `docs/en/`
   (we will assume you are writing an English-language text, but the same applies
   for your Swedish translation).
   For example, let's say you have created `docs/en/methodologies/optogenetics.md`.
2. Add your document's path and title to the English-language `nav` variable in `mkdocs.yml`.
3. Add a hyperlink to your document in `docs/en/index.md`.

For your Swedish-language version of your article/guide, do the same but simply
replace `docs/en` with `docs/sv`.

> NOTE! The filename of the document in both languages needs to be the same!
> (As far as I can tell this is a MkDocs limitation).

Optionally, [render the updated Workspace site in your local browser](https://github.com/KTH-Library/kth-datahub-workspace/tree/master#local-development).

When you are happy with your changes and want to share them with us and the world,
commit your changes in your local repository, and then push your commit to your
own remote fork.
On GitHub, create a pull request from your branch to ours.

N.B. this Workspace uses the [MkDocs site generator](https://www.mkdocs.org/user-guide/writing-your-docs)
under the hood.
