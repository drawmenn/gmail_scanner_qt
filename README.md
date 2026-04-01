# Gmail AI Qt

A small PySide6 desktop dashboard for live username checks, charting, and scan logs.

## Project layout

```text
gmail_ai_qt/
  gmail_ai_qt.py
  pyproject.toml
  src/
    gmail_ai_qt_app/
      app.py
      models/
      services/
      ui/
```

## Run locally

If you already have the dependencies installed in `.venv`, the compatibility launcher still works:

```powershell
.\.venv\Scripts\python.exe gmail_ai_qt.py
```

If you want the package-style workflow, install the project in editable mode first:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\gmail-ai-qt.exe
```

If you are working in a restricted or offline environment, this variant avoids build isolation:

```powershell
.\.venv\Scripts\python.exe -m pip install -e . --no-build-isolation
```

## Packaging

For cross-platform releases, build on each target OS separately. With PySide6 installed, you can start from:

```powershell
.\.venv\Scripts\pyside6-deploy.exe gmail_ai_qt.py
```
