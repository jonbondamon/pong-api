# Table Tennis API

A Python wrapper for the B365 Table Tennis API, designed for easy integration with betting applications and sports data analysis. This library provides clean, Pythonic access to table tennis leagues, events, players, and betting odds.

## 🏓 Current Status

**✅ Implemented & Tested:**
- **League Management**: Browse 1,100+ table tennis leagues and tournaments
- **Pagination Support**: Handle large datasets efficiently  
- **Rate Limit Tracking**: Monitor API usage automatically
- **Country Filtering**: Filter leagues by country code
- **Data Models**: Type-safe data structures for all API responses

**🚧 Coming Soon:**
- Events (live, upcoming, completed matches)
- Player statistics and search
- Betting odds from multiple bookmakers

## Installation

```bash
# Install from source (recommended during development)
git clone https://github.com/yourusername/pong-api.git
cd pong-api
pip install -e .

# Or install from PyPI (when published)
pip install tabletennis-api
```

## Quick Start

```python
from tabletennis_api import TableTennisAPI

# Initialize the client with your B365 API token
api = TableTennisAPI(api_key="your-b365-api-token")

# Get first page of leagues (100 results)
response = api.leagues.list()
print(f"Found {response.pagination.total} total leagues")

# Get leagues from a specific country
czech_leagues = api.leagues.list(country_code="cz")
print(f"Czech leagues: {len(czech_leagues.results)}")

# Check rate limit status
print(f"API calls remaining: {api.rate_limit_remaining}/{api.rate_limit}")
```

## 🏆 League Management Features

Our league functionality has been thoroughly tested with real B365 API data:

- **1,111 total leagues** available across all table tennis tournaments
- **Pagination support** for browsing large datasets (12 pages of results)
- **Country filtering** with support for international and national leagues
- **League capabilities** detection (standings, rankings support)

## 📖 Usage Examples

### Basic League Operations

```python
from tabletennis_api import TableTennisAPI

api = TableTennisAPI(api_key="your-b365-api-token")

# Get first page of leagues
response = api.leagues.list()
print(f"Total leagues: {response.pagination.total}")  # 1111 leagues

# Browse through all leagues with pagination
for page in range(1, min(4, response.pagination.total_pages)):  # First 3 pages
    page_response = api.leagues.list(page=page)
    print(f"Page {page}: {len(page_response.results)} leagues")
```

### Country-Specific Leagues

```python
# Get Czech Republic leagues
cz_leagues = api.leagues.list(country_code="cz")
print(f"Czech leagues: {len(cz_leagues.results)}")  # ~20 leagues

# Show Czech league details
for league in cz_leagues.results[:5]:
    print(f"- {league.name} (ID: {league.id})")
    print(f"  Supports standings: {league.supports_standings}")
    print(f"  Supports rankings: {league.supports_rankings}")
```

### Advanced League Features

```python
# Find WTT (World Table Tennis) tournaments
response = api.leagues.list()
wtt_leagues = [l for l in response.results if "WTT" in l.name]
print(f"Found {len(wtt_leagues)} WTT tournaments")

# Find leagues that support standings
leagues_with_standings = [l for l in response.results if l.supports_standings]
print(f"Leagues with standings: {len(leagues_with_standings)}")

# Get ALL leagues (automatically handles pagination - use carefully!)
# This will make ~12 API calls to get all 1,111 leagues
all_leagues = api.leagues.list_all()
print(f"Retrieved all {len(all_leagues)} leagues")
```

### Rate Limit Monitoring

```python
# Check rate limit before making requests
api = TableTennisAPI(api_key="your-token")

print(f"Rate limit: {api.rate_limit_remaining}/{api.rate_limit}")
if api.is_rate_limited():
    print("⚠️ Approaching rate limit!")
    print(f"Resets at: {api.rate_limit_reset}")

# Make request and see updated limits
response = api.leagues.list()
print(f"After request: {api.rate_limit_remaining}/{api.rate_limit}")
```

### League Standings and Rankings

```python
# Get league table/standings (for leagues that support it)
league_id = "41155"  # WTT tournament that supports standings
try:
    standings = api.leagues.get_table(league_id)
    print(f"Standings: {len(standings)} entries")
except Exception as e:
    print(f"No standings available: {e}")

# Get player rankings (for leagues that support it)  
try:
    rankings = api.leagues.get_rankings(league_id)
    print(f"Rankings: {len(rankings)} players")
except Exception as e:
    print(f"No rankings available: {e}")
```

## 🚨 Error Handling

```python
from tabletennis_api import (
    TableTennisAPI, 
    TableTennisAPIError, 
    AuthenticationError, 
    RateLimitError
)

api = TableTennisAPI(api_key="your-api-key")

try:
    response = api.leagues.list()
except AuthenticationError:
    print("❌ Invalid API token")
except RateLimitError as e:
    print(f"⏱️ Rate limit exceeded: {e}")
except ValueError as e:
    print(f"📝 Invalid input: {e}")  # e.g., page < 1
except TableTennisAPIError as e:
    print(f"🔗 API error: {e}")
```

## 🧪 Testing

The library includes comprehensive unit and integration tests:

```bash
# Install development dependencies
pip install -e .
pip install pytest pytest-cov responses

# Run unit tests (fast, mocked)
pytest tests/test_*.py -v

# Run integration tests (real API calls)
pytest tests/test_integration_*.py -v -m integration

# Run with coverage
pytest --cov=tabletennis_api --cov-report=term-missing

# Run specific test categories
pytest -m "not integration"  # Unit tests only
pytest -m "integration"      # Integration tests only
```

**Test Results:**
- **✅ 35 unit tests** - All passing (mocked API responses)
- **✅ 7 integration tests** - All passing (real B365 API calls)
- **📊 70% code coverage** - High coverage on implemented features

## 🔧 Development Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/pong-api.git
cd pong-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env and add your B365_API_TOKEN

# Run tests to verify setup
python test_leagues.py
```

## 📊 API Usage & Rate Limits

- **Rate Limit**: 3,600 requests per hour
- **Efficient Usage**: Library tracks rate limits automatically
- **Pagination**: 100 results per page (optimal for most use cases)
- **Real Data**: Tested with 1,111+ actual table tennis leagues

## 🗺️ Roadmap

**Version 0.2.0 (Next):**
- [ ] Events API (live matches, upcoming, completed)
- [ ] Player search and statistics
- [ ] Betting odds integration

**Version 0.3.0:**
- [ ] Advanced filtering and search
- [ ] Caching layer for better performance
- [ ] Async support for high-throughput applications

**Version 1.0.0:**
- [ ] Complete B365 API coverage
- [ ] PyPI publication
- [ ] Production hardening

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Ensure all tests pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: Coming soon
- **Issues**: [GitHub Issues](https://github.com/yourusername/pong-api/issues)
- **B365 API**: [Official Documentation](https://docs.b365api.com)