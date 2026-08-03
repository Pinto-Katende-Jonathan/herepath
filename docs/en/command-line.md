# Command line

Installing the package gives you a `herepath` command. It is handy in shell
scripts, Makefiles, and CI pipelines where you want a path anchored at the
project root without writing any Python.

## Usage

```bash
herepath [components ...] [options]
```

## Examples

```bash
herepath                      # print the project root
herepath data sales.csv       # print root/data/sales.csv
herepath data/sales.csv       # same, components may contain "/"
herepath --report             # situation report: which root, and why?
herepath --version            # print the version
```

A common pattern, anchoring a command at the project root from any subfolder:

```bash
cat "$(herepath data/sales.csv)"
```

In a Makefile:

```makefile
DATA := $(shell herepath data)

train:
	python train.py --input $(DATA)/sales.csv
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--report` | `-r` | Print a situation report explaining the chosen root, then exit. |
| `--quiet-report` | `-q` | With `--report`, print one line only (omit the reason details). |
| `--version` | `-V` | Print the version and exit. |
| `--help` | `-h` | Show the help message. |

## Exit codes and error handling

The CLI is designed to behave well inside shell scripts:

- On success it prints the path (or report) to **stdout** and exits `0`.
- On failure (for example a misconfigured `HEREPATH_ROOT`) it prints a clean
  one-line `Error: ...` to **stderr** and exits `1`, with no traceback.

This makes shell capture safe and predictable:

```bash
if ROOT="$(herepath)"; then
    echo "Project root is $ROOT"
else
    echo "herepath could not find a project root" >&2
fi
```

!!! tip "Forcing the root in CI"
    In CI or Docker, where auto-detection may not apply, set the
    [`HEREPATH_ROOT`](advanced.md#forcing-the-root-herepath_root) environment
    variable:

    ```bash
    HEREPATH_ROOT=/app herepath data/sales.csv
    ```
