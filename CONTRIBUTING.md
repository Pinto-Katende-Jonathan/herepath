# Contributing to pyhere

Thanks for taking the time to contribute. This project is small and friendly;
contributions of all sizes are welcome: bug reports, docs, tests, and code.

## Development setup

```bash
git clone https://github.com/katendepinto/py-here
cd py-here
python -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pre-commit install            # optional but recommended
```

## Running the checks

```bash
pytest                # tests
pytest --cov          # tests + coverage report
ruff check .          # lint
ruff format .         # auto-format
mypy                  # type-check
```

All of the above run in CI on every pull request, across Python 3.8 to 3.13 on
Linux, macOS and Windows. Please make sure they pass locally first.

## Pull request guidelines

- Keep changes focused; one logical change per PR.
- Add or update tests for any behaviour change.
- Update `README.md` and `CHANGELOG.md` (under an `## [Unreleased]` heading)
  when user-facing behaviour changes.
- Write clear commit messages in the imperative mood ("Add X", not "Added X").

## Design philosophy

`pyhere` deliberately mirrors the small, restricted surface of the R
[`here`](https://here.r-lib.org/) package. Before adding a new public function,
consider whether it fits that minimal philosophy. More powerful root-finding
belongs in user code or a separate library.

## Reporting bugs

Open an issue using the bug-report template and include the output of
`pyhere --report` so we can see how the root was resolved.

## Code of Conduct

By participating you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).
