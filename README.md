# Workspace KTH Digital Research Collaborative Hub

This repository contains the content for the Workspace KTH Digital Research Collaborative Hub.

The workspace is maintained in two languages:

- English: `docs/en/`
- Swedish: `docs/sv/`

## Before you start

- If you only want to edit text, you can do everything directly in GitHub (no local setup needed).
- If you want to preview changes on your computer, follow the local setup section below.

## Easiest way to contribute (no local setup)

1. Open this repository on GitHub.
2. Go to the page you want to change in `docs/en/` or `docs/sv/`.
3. Click the pencil icon (Edit this file).
4. Make your changes.
5. Scroll down and choose "Create a new branch".
6. Click "Propose changes".
7. Open a pull request.

## Where files are

- `docs/`: all workspace pages and images.
- `docs/en/`: English pages.
- `docs/sv/`: Swedish pages.
- `mkdocs.yml`: website menu/navigation.
- `site/`: generated website files. Do not edit this folder manually.

## Adding Documentation Files

### Documentation

- Create a new Markdown file: Add your new documentation file in the `docs/` directory with an appropriate name.
- Update `mkdocs.yml`: Ensure that the new file is included in the nav section of the `mkdocs.yml` configuration file for both `en` and `sv`.

#### Example

If you want to add a new document called usage:

Create `docs/en/usage.md` for the English version.
Create `docs/sv/usage.md` for the Swedish version.
Update `mkdocs.yml`:

```yaml
nav:
  - Home: index.md
  # add the new document here
  - Usage: usage.md
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
        - Användning: usage.md
```

## Local development

Use this only if you want to preview the site locally.

Requirements:

- Python 3.12+
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

Open: `http://127.0.0.1:8000`

## Build the site

Create static output in `site/`:

```bash
uv run mkdocs build
```

## Contributing

If you spot a typo, error, or want to add more information, feel free to contribute, we welcome all contributions to the KTH Data Repository Documentation.

You can either open an issue or submit a pull request.

Here's how you can fork, edit, and submit a pull request. While there are multiple ways to do this, we'll guide you through the easiest method using [GitHub Codespaces](https://github.com/features/codespaces).

Steps to follow:

- Make sure you have a GitHub account.
- Navigate to the repository page.
- Click the "Fork" button in the top-right corner of the page to create a copy of the repository in your account.
- Open your fork of the repository and press . on your keyboard to launch it in GitHub Codespaces.
- Create a new branch for your changes.
- Make the necessary updates or edits.
- Commit your changes.
- Push the changes to your fork.
- Submit a pull request.
- Wait for your pull request to be reviewed and merged.

## Deployment

The site is deployed through GitHub Actions to GitHub Pages. After changes are merged, publishing is automatic.
