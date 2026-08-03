# Contributing

Thanks for taking the time to contribute. This project is small and friendly, and
contributions of every size are welcome: bug reports, documentation, tests, and
code. First-time contributors are welcome too.

!!! tip "New to open source? Start here"
    You do not need to be an expert. Fixing a typo, translating a sentence, or
    improving an example is a real contribution, and it gets your name in the
    project's history as a contributor. This page walks you through the whole
    process from zero.

## How you become a recognized contributor

On GitHub, you are credited as a contributor when a commit authored by you is
merged into the project. So the path is always the same:

1. Get your own copy of the code.
2. Make a change and commit it under your name.
3. Open a pull request so it can be merged.

Once it's merged, you appear on the repository's contributors list.

## Step 1: set up Git (once)

If you've never used Git, tell it who you are so your commits carry your name:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

!!! warning "Use the right email"
    GitHub links a commit to your account by its email address. Use the same
    email as your GitHub account (or a GitHub `noreply` email) so your commits
    are attributed to you.

## Step 2: fork and clone

1. Click **Fork** at the top-right of the
   [repository page](https://github.com/Pinto-Katende-Jonathan/herepath) to make your own
   copy.
2. Clone *your fork* to your machine:

```bash
git clone https://github.com/YOUR-USERNAME/herepath
cd herepath
```

## Step 3: install for development

=== "Linux / macOS"

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    pre-commit install        # optional but recommended
    ```

=== "Windows (PowerShell)"

    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -e ".[dev]"
    pre-commit install        # optional but recommended
    ```

To work on this documentation site, install the docs extras and preview live:

```bash
pip install -e ".[docs]"
mkdocs serve     # open http://127.0.0.1:8000
```

## Step 4: create a branch

Never work directly on `main`. Make a branch named after your change:

```bash
git switch -c docs/fix-typo-in-tutorial
```

## Step 5: make your change and commit it

Edit the files, then stage and commit. The commit is what makes you a
contributor, so write it under your name with a clear message:

```bash
git add .
git commit -m "docs: fix typo in the tutorial"
```

!!! note "Good commit messages"
    Write in the imperative mood ("Add X", not "Added X"). Keep one logical
    change per commit.

## Step 6: run the checks

Make sure everything still passes before you push:

```bash
pytest                # tests
pytest --cov          # tests + coverage
ruff check .          # lint
ruff format .         # auto-format
mypy                  # type-check
```

All of these run in CI on every pull request, across Python 3.8 to 3.13 on Linux,
macOS, and Windows. Please make sure they pass locally first.

!!! info "Docs-only change?"
    If you only touched Markdown under `docs/` or the tutorials, you don't need
    the full test suite. Just preview with `mkdocs serve` and read your change.

## Step 7: push and open a pull request

```bash
git push -u origin docs/fix-typo-in-tutorial
```

GitHub will print a link to open a pull request. Click it, fill in the template,
and submit. A maintainer will review it, and once merged, you're a contributor.

## Pull request guidelines

- Keep changes focused: one logical change per PR.
- Add or update tests for any behaviour change.
- Update `README.md` and `CHANGELOG.md` (under an `## [Unreleased]` heading) when
  user-facing behaviour changes.
- For documentation, keep the English and French pages in sync: if you edit
  `docs/en/tutorial.md`, mirror the change in `docs/fr/tutorial.md` (and vice
  versa). Same for the root `TUTORIAL.md` (French) and `TUTORIAL.en.md`
  (English).

## Translating the docs

This project ships in English and French. Translation is a good first
contribution:

- English pages live in `docs/en/`.
- French pages live in `docs/fr/`.
- The two folders mirror each other page-for-page.

You don't have to translate everything at once; even one improved paragraph helps.

### Example A: improve a page in your language

Say you spot an awkward sentence in the French tutorial. The change is small:

```bash
git switch -c docs/improve-fr-tutorial
# edit docs/fr/tutorial.md in your editor
mkdocs serve         # check it at http://127.0.0.1:8000 (switch to Français)
git add docs/fr/tutorial.md
git commit -m "docs(fr): clarify the i_am() section"
git push -u origin docs/improve-fr-tutorial
```

Open the pull request, and you're done.

### Example B: add the docs in your mother tongue

Want the documentation in your own language? Here is the full worked example,
using Spanish (`es`). Replace `es` and the names below with your language's
[ISO 639-1 code](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes)
and translations.

**1. Create the language folder** by copying the English one as a starting point:

```bash
git switch -c docs/add-spanish
cp -r docs/en docs/es        # Windows: xcopy /E /I docs\en docs\es
```

**2. Translate the pages** in `docs/es/` one at a time. Keep all code blocks,
file paths, and function names exactly as they are; translate only the prose.
You can start with a single page and add the rest later.

**3. Register the language** in `mkdocs.yml`, under `plugins > i18n > languages`,
next to the existing `en` and `fr` entries:

```yaml
        - locale: es
          name: Español
          build: true
          nav_translations:
            Home: Inicio
            Installation: Instalación
            Tutorial: Tutorial
            "Advanced guide": "Guía avanzada"
            "Command line": "Línea de comandos"
            "API reference": "Referencia de la API"
            Contributing: Contribuir
```

The `nav_translations` block translates the sidebar labels. If you skip it, the
navigation simply stays in English for your language.

**4. Preview it locally** and use the language switcher in the top bar to check
your pages:

```bash
mkdocs serve         # http://127.0.0.1:8000
```

**5. Commit and open a pull request:**

```bash
git add docs/es mkdocs.yml
git commit -m "docs(es): add Spanish translation"
git push -u origin docs/add-spanish
```

A partial translation is welcome: it's better to add three good pages than to
wait until every page is perfect. Later contributors (maybe you) can fill in the
rest, one page per pull request.

## Design philosophy

`herepath` deliberately mirrors the small, restricted surface of the R
[`here`](https://here.r-lib.org/) package. Before adding a new public function,
consider whether it fits that minimal philosophy. More powerful root-finding
belongs in user code or a separate library.

## Reporting bugs

Open an issue using the bug-report template and include the output of
`herepath --report` so we can see how the root was resolved.

## Code of Conduct

By participating, you agree to abide by our
[Code of Conduct](https://github.com/Pinto-Katende-Jonathan/herepath/blob/main/CODE_OF_CONDUCT.md).

## Acknowledgements

A big thank you to our top contributors, whose work has shaped `herepath`:

- **MWANZA LUBUKAYI Henock**
- **MUTONJI BUKAMA Arsène**
- **KHANG MATE ZULBAL Emmanuel**
- **MUKWIYO MUKALO Patrick**
