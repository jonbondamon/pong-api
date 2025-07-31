.PHONY: help install test test-unit test-integration lint format clean setup-dev

# Use python3 explicitly since python might not be available
PYTHON := python3

help:
	@echo "Available commands:"
	@echo "  install      - Install package and dependencies"
	@echo "  setup-dev    - Set up development environment with pre-commit hooks"
	@echo "  test         - Run all tests"
	@echo "  test-unit    - Run unit tests only"
	@echo "  test-integration - Run integration tests (needs API key)"
	@echo "  lint         - Run linting (flake8, black check, isort check)"
	@echo "  format       - Format code (black, isort)"
	@echo "  coverage     - Run tests with coverage report"
	@echo "  clean        - Clean up temporary files"

install:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e .

setup-dev: install
	$(PYTHON) -m pre_commit install
	@echo "Development environment setup complete!"
	@echo "Pre-commit hooks will now run automatically before each commit."

test:
	$(PYTHON) -m pytest tests/ -v --tb=short

test-unit:
	$(PYTHON) -m pytest tests/ -v --tb=short -k "not integration"

test-integration:
	$(PYTHON) -m pytest tests/test_integration_*.py -v --tb=short -k "not performance"

lint:
	$(PYTHON) -m black --check --diff tabletennis_api/ tests/
	$(PYTHON) -m isort --check-only --diff tabletennis_api/ tests/
	$(PYTHON) -m flake8 tabletennis_api/ tests/ --max-line-length=88 --extend-ignore=E203,W503

format:
	$(PYTHON) -m black tabletennis_api/ tests/
	$(PYTHON) -m isort tabletennis_api/ tests/

coverage:
	$(PYTHON) -m pytest tests/ --cov=tabletennis_api --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/"

clean:
	rm -rf __pycache__/ .pytest_cache/ htmlcov/ *.egg-info/ .coverage
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete