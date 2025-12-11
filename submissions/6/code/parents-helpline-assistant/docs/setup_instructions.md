# Setup Instructions

## Prerequisites

- [ ] Python 3.10+
- [ ] Docker Desktop
- [ ] Anthropic API key
- [ ] 5 GB free disk space

## Quick Setup (5 minutes)

### 1. Install UV (Fast Package Manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone & Setup

```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e ".[dev]"
```

### 3. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use any editor
```

Add this line to `.env`:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 4. Start Database

```bash
make db-start
```

Wait for "Database is ready!" message.

### 5. Initialize Database

```bash
make db-migrate  # Create tables
make db-seed     # Add home remedies
```

### 6. Run Application

```bash
make run
```

App opens at `http://localhost:8501` 🎉

## Troubleshooting

### Docker not running?
1. Open Docker Desktop
2. Wait for whale icon in menu bar
3. Verify: `docker ps`

### VSCode using wrong Python?
```
Cmd/Ctrl+Shift+P → Developer: Reload Window
```

### Import errors?
```bash
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Database errors?
```bash
make clean
make db-start
make db-migrate
make db-seed
```

### Port already in use?
```bash
lsof -ti:8501 | xargs kill -9  # macOS/Linux
```

## Verification

After setup, verify:

```bash
# Check Python version
python --version  # Should be 3.10+

# Check database
docker ps  # Should show postgres container

# Run tests
make test
```

## Next Steps

1. Test the app with a sample conversation
2. Review code in `src/`
3. Run tests: `make test`
4. Read documentation in `docs/`

## Make Commands

```bash
make help              # Show all commands
make setup             # Setup environment
make install           # Install dependencies
make db-start          # Start database
make db-migrate        # Run migrations
make db-seed           # Seed data
make run               # Run app
make test              # Run tests
make clean             # Clean everything
```
