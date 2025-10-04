# VSCode Setup Guide

## Overview

VSCode is configured to **always use `.venv/bin/python`** and ignore your system/ASDF Python.

## What's Configured

### 1. Python Interpreter
`.vscode/settings.json` forces `.venv/bin/python`:
- No ASDF conflicts
- Always Python 3.10
- Auto-activates in terminal

### 2. Auto-Formatting
- Black formatter on save
- 120 character line length
- PEP 8 compliant

### 3. Linting
- Flake8 enabled
- Max line length: 120

### 4. Testing
- pytest integration
- Run tests from UI
- Debug tests with breakpoints

## Quick Start

### 1. Reload VSCode
```
Cmd/Ctrl+Shift+P → Developer: Reload Window
```

### 2. Install Extensions
When prompted, click "Install All" for:
- Python
- Pylance
- Black Formatter
- Flake8
- Docker

### 3. Verify Python
Bottom-left status bar should show:
```
Python 3.10.18 ('.venv': venv) ✅
```

If not:
```
Cmd/Ctrl+Shift+P → Python: Select Interpreter
→ Choose .venv/bin/python
```

## Running the App

### Option 1: Debug Mode (F5)
1. Press `F5`
2. Select "Python: Streamlit App"
3. App opens with debugger attached

### Option 2: Task Menu
```
Cmd/Ctrl+Shift+P → Tasks: Run Task → Run Streamlit App
```

### Option 3: Terminal
```bash
streamlit run src/ui/app.py
```
(Terminal auto-activates .venv!)

## Running Tests

### Test Explorer
1. Click Testing icon in sidebar
2. VSCode discovers tests
3. Click ▶️ to run

### Debug Tests
1. Open test file
2. Click "Debug Test" above function
3. Set breakpoints

## Available Tasks

Access via `Cmd/Ctrl+Shift+P → Tasks: Run Task`:

- Run Streamlit App
- Run Tests
- Run Tests with Coverage
- Format Code (Black)
- Lint Code (Flake8)
- Type Check (MyPy)
- Database: Start/Stop/Migrate/Seed

## Troubleshooting

### Wrong Python?
1. Reload: `Cmd/Ctrl+Shift+P → Developer: Reload Window`
2. Select: `Cmd/Ctrl+Shift+P → Python: Select Interpreter`

### Terminal doesn't activate venv?
Close and reopen terminal in VSCode

### Extensions not working?
Install Python extensions manually via Extensions panel

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Run/Debug | `F5` |
| Format Code | `Shift+Alt+F` |
| Open Terminal | ``Ctrl+` `` |
| Command Palette | `Cmd/Ctrl+Shift+P` |

## Benefits

✅ Consistent environment
✅ No ASDF conflicts
✅ Auto-formatting on save
✅ Easy debugging
✅ Integrated testing
✅ Quick tasks
