# UV Setup Guide

## What is UV?

UV is an extremely fast Python package installer and resolver written in Rust. It's **10-100x faster** than pip!

## Why UV for Hackathons?

- ⚡ **Lightning fast** - Install packages in seconds, not minutes
- 🔄 **Quick iterations** - Test dependencies rapidly
- 💪 **Reliable** - Better dependency resolution
- 🎯 **Drop-in replacement** - Works like pip

## Installation

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows (PowerShell)
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### With pip (if needed)
```bash
pip install uv
```

## Usage

### Create Virtual Environment
```bash
uv venv                      # Creates .venv
source .venv/bin/activate    # Activate
```

### Install Dependencies
```bash
# Install all (production + dev)
uv pip install -e ".[dev]"

# Install only production
uv pip install -e .

# Install from requirements.txt
uv pip install -r requirements.txt
```

### Add New Package
```bash
uv pip install package-name
```

### List Packages
```bash
uv pip list
```

## Speed Comparison

| Task | pip | uv | Speedup |
|------|-----|-----|---------|
| Fresh install | 45s | 1.5s | **30x** |
| Cached install | 15s | 0.5s | **30x** |

## Project Setup

This project supports **both pip and UV**:

### With UV (Recommended)
```bash
make setup    # Installs UV + creates venv
make install  # Installs dependencies with UV
```

### With pip (Traditional)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Benefits

✅ Saves time during development
✅ Perfect for hackathons (quick iterations)
✅ Better dependency resolution
✅ Drop-in pip replacement

## More Info

- [UV Documentation](https://github.com/astral-sh/uv)
- [Installation Guide](https://astral.sh/uv)
