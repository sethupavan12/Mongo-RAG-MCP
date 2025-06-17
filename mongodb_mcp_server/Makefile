# MongoDB Vector RAG MCP Server - Makefile

.PHONY: install test lint format clean demo help setup-dev

# Default target
help:
	@echo "MongoDB Vector RAG MCP Server - Development Commands"
	@echo "=================================================="
	@echo ""
	@echo "Setup:"
	@echo "  setup-dev    - Setup development environment"
	@echo "  install      - Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting (ruff)"
	@echo "  format       - Format code (black)"
	@echo "  typecheck    - Run type checking (mypy)"
	@echo ""
	@echo "Demo:"
	@echo "  demo         - Run basic demo script"
	@echo "  pdf-demo     - Run PDF contract analysis demo"
	@echo "  multi-demo   - Run multi-collection architecture demo"
	@echo "  clean        - Clean up temporary files"
	@echo ""

# Setup development environment
setup-dev:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	@echo "Development environment setup complete!"
	@echo "Activate with: source venv/bin/activate"

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	pytest tests/ -v --tb=short

# Run tests with coverage
test-cov:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

# Run linting
lint:
	ruff check .

# Format code
format:
	black .
	ruff check --fix .

# Type checking
typecheck:
	mypy . --ignore-missing-imports

# Run all quality checks
quality: format lint typecheck test

# Run demo
demo:
	@echo "Running MongoDB MCP Server Demo..."
	@echo "Make sure you have configured .env file first!"
	python demo.py

# Run PDF contract analysis demo
pdf-demo:
	@echo "Running PDF Contract Analysis Demo..."
	@echo "Make sure you have configured .env file first!"
	@echo "Processing examples/Sample_contract_public.pdf..."
	python examples/pdf_demo.py

# Run multi-collection architecture demo
multi-demo:
	@echo "Running Multi-Collection Architecture Demo..."
	@echo "This demo explains collection strategies for production use..."
	python examples/multi_collection_demo.py

# Start the MCP server
server:
	@echo "Starting MongoDB MCP Server..."
	@echo "Make sure you have configured .env file first!"
	python main.py

# Clean temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf build/
	rm -rf dist/
	@echo "Cleaned up temporary files"

# Install package in development mode
install-dev:
	pip install -e .

# Build package
build:
	python setup.py sdist bdist_wheel

# Check package
check-package:
	python setup.py check
	twine check dist/*

# Example usage targets
examples:
	@echo "Example Usage:"
	@echo ""
	@echo "1. Setup:"
	@echo "   make setup-dev"
	@echo "   source venv/bin/activate"
	@echo "   cp .env.example .env"
	@echo "   # Edit .env with your credentials"
	@echo ""
	@echo "2. Run tests:"
	@echo "   make test"
	@echo ""
	@echo "3. Run demo:"
	@echo "   make demo"
	@echo ""
	@echo "4. Start server:"
	@echo "   make server" 