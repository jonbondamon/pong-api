.PHONY: help install test test-unit test-integration lint format clean setup-dev

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
	pip install -r requirements.txt
	pip install -e .

setup-dev: install
	pre-commit install
	@echo "Development environment setup complete!"
	@echo "Pre-commit hooks will now run automatically before each commit."

test:
	python -m pytest tests/ -v --tb=short

test-unit:
	python -m pytest tests/ -v --tb=short -k "not integration"

test-integration:
	python -m pytest tests/test_integration_*.py -v --tb=short -k "not performance"

lint:
	black --check --diff tabletennis_api/ tests/
	isort --check-only --diff tabletennis_api/ tests/
	flake8 tabletennis_api/ tests/ --max-line-length=88 --extend-ignore=E203,W503

format:
	black tabletennis_api/ tests/
	isort tabletennis_api/ tests/

coverage:
	python -m pytest tests/ --cov=tabletennis_api --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/"

clean:
	rm -rf __pycache__/ .pytest_cache/ htmlcov/ *.egg-info/ .coverage
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete