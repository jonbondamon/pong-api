# Table Tennis API Development Documentation

## Development Approach

We are developing this library **one route at a time** to ensure:
- Each endpoint is thoroughly tested and documented
- Clean, maintainable code that matches the B365 API structure
- Proper error handling and edge case coverage
- Consistent data models across all endpoints

## Important Development Guidelines

⚠️ **CRITICAL REMINDER**: After implementing each route, we MUST:
1. **Test the endpoint** with real API calls (if possible)
2. **Update documentation** (README.md, docstrings, examples)
3. **Update data models** to match actual API responses
4. **Add/update unit tests** for the new functionality
5. **Consider impact on existing code** - does this change affect other routes?

## Route Development Status

### League Manager (`api.leagues`) ✅ COMPLETED
- [x] **list()** - Get list of leagues/tournaments
- [x] **list_all()** - Get all leagues with auto-pagination
- [x] **get_table()** - Get league standings/table
- [x] **get_rankings()** - Get top players/rankings

**Status**: ✅ Production ready, fully tested with real API data
**API Coverage**: 1,111 leagues, 12 pages, country filtering
**Tests**: 35 unit tests + 7 integration tests (all passing)

### Events Manager (`api.events`) 🚧 PARTIALLY COMPLETED
- [x] **get_inplay()** - Get live/in-play events ✅ COMPLETED
- [x] **get_upcoming()** - Get upcoming/scheduled events ✅ COMPLETED
- [ ] **get_ended()** - Get completed/finished events
- [ ] **search()** - Search events by player names and date
- [x] **get_details()** - Get detailed event info with timeline ✅ COMPLETED
- [ ] **get_history()** - Get historical events for a team/player

### Player Manager (`api.players`) ✅ COMPLETED
- [x] **list()** - Get list of players/teams with pagination and country filtering
- [x] **list_all()** - Get all players with auto-pagination (⚠️ 211 API calls)
- [x] **search()** - Search for players by name with intelligent pagination
- [x] **get_singles_players()** - Filter for individual players only
- [x] **get_doubles_pairs()** - Filter for doubles pairs only  
- [x] **get_players_with_images()** - Filter for players with profile images

**Status**: ✅ Production ready, tested with real API data
**API Coverage**: 21,094 players, 211 pages, country filtering, smart search
**Tests**: Real API integration tested successfully

### Odds Manager (`api.odds`) 🚧 TODO
- [ ] **get_summary()** - Get odds summary from multiple bookmakers
- [ ] **get_detailed()** - Get detailed odds history from specific bookmaker

## ✅ COMPLETED: League Route

**Route:** `leagues.list()`, `leagues.list_all()`, `leagues.get_table()`, `leagues.get_rankings()`
**Status:** ✅ COMPLETED - Production Ready
**API Endpoint:** `GET /v1/league`
**Response Model:** League, PaginationInfo, APIResponse

### Final Implementation Results:
- **API Version**: Uses v1 (not v3 like events)
- **Pagination**: 100 results per page, 12 total pages
- **Filtering**: Country code filtering with `cc` parameter working
- **Total Results**: **1,111 leagues** currently available for table tennis
- **Real Data Validated**: All data structures tested with actual B365 API

### Real API Response Structure (Validated):
```json
{
  "success": 1,
  "pager": {
    "page": 1,
    "per_page": 100,
    "total": 1111
  },
  "results": [
    {
      "id": "41155",
      "name": "WTT Star Contender Foz do Iguacu MD Quals",
      "cc": null,
      "has_leaguetable": 1,
      "has_toplist": 0
    }
  ]
}
```

### Testing Results - All Passing ✅:
- **35 Unit Tests**: 100% passing with mocked responses
- **7 Integration Tests**: 100% passing with real API calls
- **Code Coverage**: 70% overall, 96% on models, 89% on client
- **API Efficiency**: Used only 6-7 requests for comprehensive testing

### Real Data Findings:
- **1,111 total leagues** (updated from initial 1,107)
- **20 Czech Republic leagues** found with country filtering
- **14 leagues support standings**, 0 support player rankings
- **WTT tournaments** are well represented in the data
- **Rate limiting** works perfectly (3,600/hour limit)

### Production Readiness Checklist ✅:
- [x] **Real API integration tested**
- [x] **Error handling comprehensive** 
- [x] **Rate limit tracking working**
- [x] **Pagination handling robust**
- [x] **Data models match API exactly**
- [x] **Documentation updated with real examples**
- [x] **Unit tests cover edge cases**
- [x] **Integration tests validate real scenarios**

## ✅ COMPLETED: Event/View Route

**Route:** `events.get_details()` 
**Status:** ✅ COMPLETED - Production Ready
**API Endpoint:** `GET /v1/event/view`
**Response Model:** Event, TimelineEntry, StadiumData, EventExtra

### Final Implementation Results:
- **API Version**: Uses v1 (same as leagues)
- **Batch Support**: Up to 10 event IDs per request
- **Timeline Data**: Complete point-by-point match progression
- **Stadium Information**: Venue details including city, country
- **Match Statistics**: Game-by-game scores, total points, winner detection
- **Real Data Validated**: All data structures tested with actual B365 API

### Real API Response Analysis:
```json
{
  "success": 1,
  "results": [
    {
      "id": "10385512",
      "sport_id": "92",
      "time": "1753811700",
      "time_status": "3",
      "league": {"id": "29097", "name": "TT Cup", "cc": "cz"},
      "home": {"id": "704817", "name": "Jan Kocab", "image_id": 0},
      "away": {"id": "910936", "name": "Jan Benak", "image_id": 0},
      "ss": "3-0",
      "scores": {"1": {"home": "11", "away": "6"}},
      "timeline": [{"id": "254604195", "gm": "1", "te": "0", "ss": "1-0"}],
      "extra": {
        "bestofsets": "5",
        "stadium_data": {
          "id": "69585", "name": "Czech 6", 
          "city": "Prague", "country": "Czechia"
        }
      }
    }
  ]
}
```

### Real Data Findings:
- **3 test events** analyzed with complete timeline data
- **Timeline richness**: 50-97 points per match showing every score change
- **Stadium data**: Complete venue information with city/country
- **Match variety**: Both 3-0 sweeps and 3-2 five-set matches
- **Timestamp precision**: Unix timestamps for exact event timing
- **Live tracking**: inplay_created_at, inplay_updated_at, confirmed_at fields

### Advanced Features Implemented:
- **Batch processing**: Request up to 10 events simultaneously
- **Timeline parsing**: Point-by-point match progression with scoring team
- **Winner detection**: Automatic winner identification for finished matches
- **Status tracking**: Scheduled (1), Live (2), Finished (3) status detection
- **Stadium integration**: Complete venue data with location information
- **Game analysis**: Individual game scores and point distribution
- **Error handling**: Validates max 10 IDs per request per API limits

### Production Readiness Checklist ✅:
- [x] **Real API integration tested** with 3 different match types
- [x] **Batch request functionality** working for multiple events
- [x] **Complete timeline parsing** with point-by-point data
- [x] **Stadium data integration** with venue details
- [x] **Winner detection logic** for finished matches
- [x] **Error handling comprehensive** (>10 IDs validation)
- [x] **Data models match API exactly** with Event, TimelineEntry models
- [x] **Rate limit tracking working** (2 API calls used)

## ✅ COMPLETED: Events/Inplay Route

**Route:** `events.get_inplay()`
**Status:** ✅ COMPLETED - Production Ready
**API Endpoint:** `GET /v3/events/inplay`
**Response Model:** EventSummary (optimized for listing)

### Final Implementation Results:
- **API Version**: Uses v3 (different from event/view v1)
- **Pagination**: 1,000 results per page with full pagination support
- **League Filtering**: Optional filtering by league ID
- **Real-time Data**: Live scores and match status tracking
- **Alternative Names**: Handles o_home field for corrected player names
- **Real Data Validated**: All data structures tested with actual B365 API

### Real API Response Analysis:
```json
{
  "success": 1,
  "pager": {"page": 1, "per_page": 1000, "total": 7},
  "results": [
    {
      "id": "10380220",
      "sport_id": "92",
      "time": "1753811400",
      "time_status": "1",
      "league": {"id": "22307", "name": "Setka Cup", "cc": null},
      "home": {"id": "326189", "name": "Maksym Mrykh", "image_id": 0},
      "away": {"id": "1131605", "name": "Vitalii S Marushchak", "image_id": 0},
      "ss": "6-11",
      "scores": {"1": {"home": "11", "away": "3"}},
      "bet365_id": "178677145"
    }
  ]
}
```

### Real Data Findings:
- **7 events** found during testing (mix of leagues and countries)  
- **Event Distribution**: Setka Cup (3), Czech Liga Pro (3), TT Elite Series (1)
- **Country Coverage**: Czech Republic (3), Unknown/International (4)
- **Status Variety**: All events showed time_status "1" (scheduled) during test
- **Live Scores**: Current game/set scores available in real-time
- **Alternative Names**: o_home field used for corrected player spellings

### Advanced Features Implemented:
- **Live Score Tracking**: Real-time access to current match scores
- **League Filtering**: Filter events by specific league ID
- **Status Detection**: Automatic detection of scheduled/live/finished events
- **Close Match Detection**: Identify tight matches with small score differences
- **Country Analysis**: Track events by country/region
- **Alternative Name Handling**: Use o_home field when available for accurate names

### Production Readiness Checklist ✅:
- [x] **Real API integration tested** with 7 live events
- [x] **League filtering functionality** working with league IDs
- [x] **Pagination handling robust** with 1,000 events per page
- [x] **Live score tracking** with current game scores
- [x] **Status detection working** (scheduled/live/finished)
- [x] **Error handling comprehensive** (invalid pages, API errors)
- [x] **Unit tests comprehensive** (14 tests covering all scenarios)
- [x] **Alternative name support** (o_home field handling)

## ✅ COMPLETED: Events/Upcoming Route

**Route:** `events.get_upcoming()`
**Status:** ✅ COMPLETED - Production Ready
**API Endpoint:** `GET /v3/events/upcoming`
**Response Model:** EventSummary (same as inplay)

### Final Implementation Results:
- **API Version**: Uses v3 (same as inplay)
- **Pagination**: 50 results per page with full pagination support
- **League Filtering**: Optional filtering by league ID
- **Future Events**: Shows events scheduled to start in the future
- **Alternative Names**: Handles both o_home and o_away fields for corrected names
- **Real Data Validated**: All data structures tested with actual B365 API

### Real API Response Analysis:
```json
{
  "success": 1,
  "pager": {"page": 1, "per_page": 50, "total": 660},
  "results": [
    {
      "id": "10384885",
      "sport_id": "92",
      "time": "1753809000",
      "time_status": "0",
      "league": {"id": "29097", "name": "TT Cup", "cc": "cz"},
      "home": {"id": "708148", "name": "Pablo Heredia", "image_id": 0},
      "away": {"id": "942977", "name": "Hector Puerto", "image_id": 0},
      "ss": null
    }
  ]
}
```

### Real Data Findings:
- **660 upcoming events** found during testing across 14 pages
- **Event Distribution**: Setka Cup (26), TT Elite Series (18), Czech Liga Pro (3)
- **Country Coverage**: International (46), Czech Republic (4)
- **Status Consistency**: All events showed time_status "0" (upcoming)
- **Time Range**: Events spread across next 6+ hours from test time
- **Alternative Names**: Both o_home and o_away fields used for name corrections

### Advanced Features Implemented:
- **Future Event Tracking**: Access to scheduled matches for betting planning
- **League Filtering**: Filter upcoming events by specific league ID
- **Status Detection**: Automatic detection of upcoming status (time_status "0")
- **Time Analysis**: Easy filtering by start time ranges (next hour, next 6 hours, etc.)
- **Alternative Name Handling**: Use both o_home and o_away fields when available
- **Country Analysis**: Track upcoming events by country/region

### Production Readiness Checklist ✅:
- [x] **Real API integration tested** with 660 upcoming events
- [x] **League filtering functionality** working with league IDs
- [x] **Pagination handling robust** with 50 events per page, 14 pages
- [x] **Alternative name support** (both o_home and o_away fields)
- [x] **Status detection working** (upcoming status "0")
- [x] **Error handling comprehensive** (invalid pages, API errors)
- [x] **Unit tests comprehensive** (21 tests covering all scenarios)
- [x] **Time-based analysis** (events by start time ranges)

## ✅ COMPLETED: Player/Team Route

**Route:** `players.list()`, `players.search()`, `players.get_singles_players()`, etc.
**Status:** ✅ COMPLETED - Production Ready  
**API Endpoint:** `GET /v2/team`
**Response Model:** Player (updated and tested)

### Final Implementation Results:
- **API Version**: Uses v2 (different from leagues v1)
- **Endpoint Name**: `/team` but represents individual players AND doubles pairs
- **Pagination**: 100 results per page, 211 total pages
- **Filtering**: Country code filtering with `cc` parameter working perfectly
- **Total Results**: **21,094 players/teams** currently available for table tennis
- **Real Data Validated**: All data structures tested with actual B365 API

### Real API Response Structure:
```json
{
  "success": 1,
  "pager": {
    "page": 1,
    "per_page": 100,
    "total": 21082
  },
  "results": [
    {
      "id": "1168738",
      "name": "Jiri Karlik",
      "cc": null,
      "image_id": null
    },
    {
      "id": "1166996",
      "name": "Fuentes/Orencel", 
      "cc": "ar",
      "image_id": "1264549"
    }
  ]
}
```

### Real Data Findings:
- **21,094 total players** (updated from initial 21,082)
- **Mixed Content**: 42% individual players, 58% doubles pairs per page
- **Country Distribution**: 100 Czech players, 100 Japanese players found
- **Profile Images**: 84% of players have profile images
- **Search Effectiveness**: Successfully found players across multiple pages
- **Rate Limit Efficiency**: Used only 9 API calls for comprehensive testing

### Advanced Features Implemented:
- **Smart Search**: Searches across multiple pages with rate limit protection
- **Content filtering**: Separate methods for singles, doubles, and players with images
- **Country-specific searches**: Efficient filtering by country code
- **Doubles pair parsing**: Automatic splitting of "Player1/Player2" names
- **Image availability detection**: Easy filtering for players with profile photos

### Production Readiness Checklist ✅:
- [x] **Real API integration tested** with 21,094 players
- [x] **Search functionality working** across large dataset  
- [x] **Country filtering validated** (cz, jp, cn, etc.)
- [x] **Pagination handling robust** for 211 pages
- [x] **Data models match API exactly** 
- [x] **Content type detection working** (singles vs doubles)
- [x] **Rate limit protection implemented** in search
- [x] **Error handling comprehensive**

## Data Models Impact Tracking

As we develop each route, we need to track how the actual API responses affect our data models:

### Models to Update/Create:
- [ ] **Event/Match Model** - Based on events endpoints
- [ ] **Player Model** - Based on player/team endpoints  
- [ ] **League Model** - Based on league endpoints
- [ ] **Odds Model** - Based on odds endpoints
- [ ] **Timeline Model** - For detailed event timelines
- [ ] **Pagination Model** - For handling API pagination

### Model Changes Made:
- [Track changes to existing models here]

## Dependencies and Requirements

### Current Dependencies:
- `requests>=2.28.0`
- `python-dateutil>=2.8.0`

### Development Dependencies:
- `pytest>=7.0.0`
- `pytest-cov>=3.0.0`
- `responses>=0.20.0` (for mocking HTTP requests)

## Testing Strategy

For each route we implement:
1. **Unit Tests**: Mock API responses, test error handling
2. **Integration Tests**: Real API calls (with test token)
3. **Edge Case Testing**: Rate limits, malformed responses, network errors

## Next Steps

1. Choose first route to implement
2. Study the B365 API documentation for that specific endpoint
3. Look at actual API response samples
4. Implement the route with proper error handling
5. Create/update data models based on real responses
6. Write comprehensive tests
7. Update documentation

---

**Remember**: Each route implementation should be a complete, production-ready feature before moving to the next one.