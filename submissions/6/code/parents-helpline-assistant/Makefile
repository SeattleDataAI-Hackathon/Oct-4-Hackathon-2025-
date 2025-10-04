.PHONY: help setup db-start db-stop db-migrate db-seed run test test-coverage clean logs install

# Default target
help:
	@echo "Parents Healthline Assistant - Available Commands:"
	@echo ""
	@echo "  make setup           - Set up development environment with uv"
	@echo "  make install         - Install dependencies with uv"
	@echo "  make db-start        - Start PostgreSQL database container"
	@echo "  make db-stop         - Stop PostgreSQL database container"
	@echo "  make db-migrate      - Run database migrations"
	@echo "  make db-seed         - Seed database with home remedies"
	@echo "  make run             - Run the Streamlit application"
	@echo "  make test            - Run all tests"
	@echo "  make test-coverage   - Run tests with coverage report"
	@echo "  make clean           - Clean up containers, cache, and generated files"
	@echo "  make logs            - View application logs"
	@echo ""

# Setup development environment with uv
setup:
	@echo "Setting up development environment with uv..."
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	@echo "Creating virtual environment with uv..."
	@uv venv
	@echo ""
	@echo "Virtual environment created!"
	@echo "Next steps:"
	@echo "  1. Activate: source .venv/bin/activate (or .venv\\Scripts\\activate on Windows)"
	@echo "  2. Install dependencies: make install"
	@echo "  3. Copy .env.example to .env and add your ANTHROPIC_API_KEY"
	@echo "  4. Run 'make db-start' to start the database"
	@echo "  5. Run 'make db-migrate' to set up database schema"
	@echo "  6. Run 'make db-seed' to populate home remedies"
	@echo "  7. Run 'make run' to start the application"

# Install dependencies with uv
install:
	@echo "Installing dependencies with uv..."
	@uv pip install -e ".[dev]"
	@echo "Dependencies installed!"

# Start database
db-start:
	@echo "Starting PostgreSQL container..."
	@docker compose up -d postgres || docker-compose up -d postgres
	@echo "Waiting for database to be ready..."
	@sleep 5
	@echo "Database is ready!"

# Stop database
db-stop:
	@echo "Stopping PostgreSQL container..."
	@docker compose down || docker-compose down

# Run database migrations
db-migrate:
	@echo "Running database migrations..."
	@alembic upgrade head
	@echo "Migrations completed!"

# Create initial migration (for development)
db-migration-create:
	@echo "Creating new migration..."
	@alembic revision --autogenerate -m "$(msg)"

# Seed database with home remedies
db-seed:
	@echo "Seeding database with home remedies..."
	@python scripts/seed_home_remedies.py
	@echo "Database seeded!"

# Run the application
run:
	@echo "Starting Parents Healthline Assistant..."
	@streamlit run src/ui/app.py --server.port 8501

# Run tests
test:
	@echo "Running tests..."
	@pytest tests/ -v

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	@pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

# Clean up
clean:
	@echo "Cleaning up..."
	@docker compose down -v 2>/dev/null || docker-compose down -v 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf .pytest_cache htmlcov .coverage 2>/dev/null || true
	@echo "Cleanup complete!"

# View logs
logs:
	@echo "Application logs:"
	@tail -f logs/app.log 2>/dev/null || echo "No logs found. Run the application first."

# Sync dependencies (alternative to install)
sync:
	@echo "Syncing dependencies with uv..."
	@uv pip sync
	@echo "Dependencies synced!"

# Format code with black
format:
	@echo "Formatting code with black..."
	@black src/ tests/
	@echo "Code formatted!"

# Lint code
lint:
	@echo "Linting code with flake8..."
	@flake8 src/ tests/ --max-line-length=120
	@echo "Linting complete!"

# Type check
typecheck:
	@echo "Type checking with mypy..."
	@mypy src/
	@echo "Type checking complete!"

# Full setup (for first time)
first-time-setup: setup install db-start db-migrate db-seed
	@echo ""
	@echo "========================================="
	@echo "Setup complete! 🎉"
	@echo "========================================="
	@echo ""
	@echo "To start the application:"
	@echo "  1. Activate virtual environment: source .venv/bin/activate"
	@echo "  2. Ensure .env file has your ANTHROPIC_API_KEY"
	@echo "  3. Run: make run"
	@echo ""
