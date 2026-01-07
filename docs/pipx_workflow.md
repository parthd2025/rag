# pipx workflow for isolated CLI tools

This document shows how to use `pipx` to install and run project-global CLI tools (like a Docling CLI) in isolated environments while keeping your project virtualenv clean.

Prerequisites

- `pipx` installed. On Windows (PowerShell):

```powershell
python -m pip install --user pipx
python -m pipx ensurepath
```

Installing a tool with pipx

```powershell
# Example: install a hypothetical docling CLI (replace with real package name)
pipx install docling

# Run the installed CLI
pipx run docling --help
```

Using a specific Python interpreter (project venv)

If you want pipx to use your project `.venv` Python when installing a tool:

```powershell
pipx install --python D:\RAG\.venv\Scripts\python.exe docling
```

Developing local CLIs with pipx

For local development of a CLI package in the repository, install from the path:

```powershell
pipx install --editable .
```

Uninstalling/updating

```powershell
pipx upgrade docling
pipx uninstall docling
```

Notes

- Use `pipx run --spec 'pkg==version' cmd` for one-off runs without installation.
- Keep `requirements-dev.txt` for reproducible project dependencies, and use `pipx` for tools that should live outside the project venv.
