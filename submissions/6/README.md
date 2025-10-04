# BabyCareAssistant 👶

Parenting is the most important — and arguably the hardest — job in the world, yet it comes with no training. When babies get sick, parents often face long wait times on nurse helplines, delayed doctor appointments, and little immediate guidance. They're left overwhelmed, worried, and helpless, not knowing whether to act or simply let their baby's immune system recover.

Parents and their babies need help now — not hours or days later — and they need quality, trustworthy care.

**BabyCareAssistant** is available 24/7, guiding parents through symptom checks, providing safe and practical next steps, and offering comfort in stressful moments. When needed, it seamlessly escalates to healthcare professionals — ensuring parents get the right support, at the right time.

---

## 🚀 Quick Start

```bash
# 1. Setup (one-time)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Install uv (fast package manager)
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# 2. Configure
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here

# 3. Start database & run
make db-start
make db-migrate
make db-seed
make run
```

Access at `http://localhost:8501`

---

## ✨ Features

- 🤖 **AI-Powered Chat** - Empathetic conversations using Claude 3.5 Sonnet
- 📋 **Symptom Tracking** - Structured intake with parent verification
- 🏠 **Home Remedies** - 19 pre-approved, age-appropriate remedies
- ⚠️ **Safety First** - Red flag detection for emergencies
- 💾 **Context Retention** - Conversations saved across sessions
- 🔒 **Secure** - HIPAA-like data privacy considerations

---

## 🛠 Tech Stack

- **Python 3.10+** | **Streamlit** | **PostgreSQL** | **Claude AI** | **Docker**
- **SQLAlchemy** | **Alembic** | **pytest** | **UV** (package manager)

---

## 📖 Documentation

- **README.md** (this file) - Quick start & overview
- **CLAUDE.md** - Development commands & architecture
- **SECURITY.md** - API key protection & best practices

---

## 🧪 Development

```bash
make help              # Show all commands
make test              # Run tests
make test-coverage     # Coverage report
make format            # Format code with black
make lint              # Lint with flake8
```

---

## 📋 Available Make Commands

```bash
make setup            # Set up venv with uv
make install          # Install dependencies
make db-start         # Start PostgreSQL
make db-stop          # Stop PostgreSQL
make db-migrate       # Run migrations
make db-seed          # Seed home remedies
make run              # Run Streamlit app
make test             # Run tests
make clean            # Clean everything
```

---

## 🏗 Architecture

```
Streamlit UI → Health Agent (Claude AI) → Services → PostgreSQL
```

**Key Components:**
- `src/ui/` - Streamlit web interface
- `src/agents/` - Claude AI integration
- `src/services/` - Business logic
- `src/database/` - SQLAlchemy models
- `tests/` - pytest test suite

---

## 🔒 Security

- ✅ `.env` file protected (in `.gitignore`)
- ✅ Password hashing (bcrypt)
- ✅ JWT tokens for sessions
- ✅ SQL injection protection (SQLAlchemy ORM)

**See SECURITY.md for details**

---

## 📝 Database Schema

- `users` - User accounts
- `sessions` - User/anonymous sessions
- `conversations` - Chat threads
- `messages` - Chat messages
- `symptoms` - Reported symptoms
- `diagnoses` - AI diagnoses
- `recommendations` - Treatment suggestions
- `home_remedies` - Pre-approved remedies

---

## 🐛 Troubleshooting

### VSCode using wrong Python?
Reload window: `Cmd/Ctrl+Shift+P → Developer: Reload Window`

### Database connection errors?
```bash
make clean && make db-start && make db-migrate && make db-seed
```

### Import errors?
```bash
source .venv/bin/activate
uv pip install -e ".[dev]"
```

---

## 📄 License

See LICENSE file.

---

**Built for hackathon - helping parents help their babies** ❤️
