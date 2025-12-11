# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Quick Commands

```bash
# Setup
make setup && source .venv/bin/activate && make install

# Database
make db-start db-migrate db-seed

# Run
make run              # Streamlit app at http://localhost:8501

# Test
make test             # Run all tests
make test-coverage    # With coverage

# Code Quality
make format lint      # Format and lint
```

## Architecture

**Tech Stack:** Python 3.10 + Streamlit + Claude AI + PostgreSQL + Docker

**Flow:** UI → Agent (Claude) → Services → Database

**Key Directories:**
- `src/ui/` - Streamlit interface
- `src/agents/` - Claude AI integration
- `src/services/` - Business logic (auth, conversation, symptoms, diagnosis, remedies)
- `src/database/` - SQLAlchemy models + connection
- `tests/` - pytest suite (unit, integration)

## Database Schema

```
users → sessions → conversations → messages
                                 → symptoms
                                 → diagnoses → recommendations
home_remedies (standalone)
```

## Important Notes

**Security:**
- `.env` is gitignored (contains ANTHROPIC_API_KEY)
- Use `.env.example` as template
- Passwords hashed with bcrypt

**Development:**
- VSCode uses `.venv/bin/python` (configured in `.vscode/`)
- UV for fast package management
- Black formatter (120 char line length)
- Flake8 linting

**Healthcare Data:**
- HIPAA-like considerations
- Red flag detection for emergencies
- Age-appropriate home remedies (0-36 months)
- Safety disclaimers on all AI responses
- this application is for a hackathon project
- make changes please for this hackathon project