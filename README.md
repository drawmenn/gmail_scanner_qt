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

If you want an explicit one-file build with Nuitka on Windows, this command works from the project root:

```powershell
.\.venv\Scripts\python.exe -m nuitka gmail_ai_qt.py `
  --onefile `
  --follow-imports `
  --enable-plugin=pyside6 `
  --include-package=playwright `
  --include-package=pyqtgraph `
  --include-module=PySide6.QtOpenGL `
  --include-module=PySide6.QtOpenGLWidgets `
  --include-data-dir=src/gmail_ai_qt_app/assets=gmail_ai_qt_app/assets `
  --windows-icon-from-ico=src/gmail_ai_qt_app/assets/icon.ico `
  --windows-console-mode=disable `
  --output-dir=dist `
  --output-filename=gmail-ai-qt `
  --assume-yes-for-downloads
```

## Playwright In Packaged EXE

The packaged executable expects Playwright's Chromium browser beside the EXE, not inside `.venv`.

Install Chromium into a folder next to the packaged executable like this:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\dist\playwright-browsers"
.\.venv\Scripts\python.exe -m playwright install chromium
```

After that, keep these together when you run or distribute the packaged app:

```text
dist/
  gmail-ai-qt.exe
  playwright-browsers/
```

Without that `playwright-browsers` folder, the `Playwright Page` and `Google Browser` providers will report that Chromium is missing.
