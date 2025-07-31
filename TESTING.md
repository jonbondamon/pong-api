# Testing & CI/CD Setup

This project includes comprehensive automated testing that runs on every push and pull request.

## 🚀 Quick Start

### Running Tests Locally

```bash
# Run all unit tests (no API key needed)
make test-unit

# Run all tests including integration (needs API key)
make test

# Run with coverage reporting
make coverage

# Run linting and formatting checks
make lint
make format
```

### Setting Up Development Environment

```bash
# Install dependencies and set up pre-commit hooks
make setup-dev

# This will:
# - Install all dependencies
# - Set up pre-commit hooks that run before each commit
# - Automatically run tests, linting, and formatting checks
```

## 🔧 CI/CD Pipeline

### GitHub Actions Workflow

The repository includes a comprehensive GitHub Actions workflow (`.github/workflows/test.yml`) that:

**✅ On Every Push/PR:**
- Tests across Python 3.9, 3.10, 3.11, 3.12
- Runs all 134+ unit tests
- Runs integration tests (if API key available)
- Performs code quality checks (black, isort, flake8)
- Generates coverage reports

**📊 Test Coverage:**
- Unit tests: 134 tests covering all functionality
- Integration tests: 12 tests with real API calls
- Bulk methods: 25 specialized tests for betting analysis features

### Setting up CI/CD

1. **Push to GitHub**: The workflow runs automatically
2. **Add API Key** (optional): Add `B365_API_TOKEN` as a repository secret for integration tests
3. **Enable Branch Protection**: Require CI to pass before merging

```bash
# To set up repository secrets in GitHub:
# 1. Go to Settings > Secrets and Variables > Actions
# 2. Add new repository secret:
#    Name: B365_API_TOKEN
#    Value: your-api-token-here
```

## 🛡️ Pre-commit Hooks

Automatic code quality checks run before each commit:

- **Black**: Code formatting
- **isort**: Import sorting  
- **flake8**: Style guide enforcement
- **pytest**: All unit tests must pass

```bash
# Manual hook execution
pre-commit run --all-files

# Skip hooks (not recommended)
git commit --no-verify -m "message"
```

## 📈 Test Structure

```
tests/
├── test_bulk_events_manager.py      # 25 tests - Bulk data collection
├── test_events_manager.py           # 40 tests - Events API
├── test_player_manager.py           # 25 tests - Players API  
├── test_league_manager.py           # 15 tests - Leagues API
├── test_odds_manager.py             # 10 tests - Odds API
├── test_models.py                   # 15 tests - Data models
├── test_client.py                   # 9 tests - API client
├── test_integration_bulk_events.py  # 12 tests - Real API bulk methods
├── test_integration_leagues.py      # 8 tests - Real API leagues
└── test_integration_odds.py         # 6 tests - Real API odds
```

## 🎯 Testing Commands

| Command | Description | API Key Required |
|---------|-------------|------------------|
| `make test-unit` | Unit tests only | ❌ No |
| `make test-integration` | Integration tests | ✅ Yes |
| `make test` | All tests | ✅ Yes (optional) |
| `make coverage` | Tests + coverage report | ❌ No |
| `make lint` | Code quality checks | ❌ No |

## 🚦 Test Status

- **Unit Tests**: ✅ 134 tests passing
- **Integration Tests**: ✅ 12 tests passing  
- **Code Coverage**: 📊 Generated in `htmlcov/`
- **CI/CD**: 🔄 Automated on push/PR

## 🔍 Debugging Failed Tests

```bash
# Run specific test file
python3 -m pytest tests/test_bulk_events_manager.py -v

# Run specific test
python3 -m pytest tests/test_bulk_events_manager.py::TestEventsManagerBulkMethods::test_get_player_history_basic_success -v

# Run with more verbose output
python3 -m pytest tests/ -v --tb=long

# Run integration tests with real API (needs token)
python3 -m pytest tests/test_integration_*.py -v -s
```