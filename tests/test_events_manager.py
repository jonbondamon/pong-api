"""
Unit tests for EventsManager class
"""

from datetime import datetime

import pytest
import responses

from tabletennis_api.client import TableTennisAPI
from tabletennis_api.exceptions import TableTennisAPIError
from tabletennis_api.managers import EventsManager
from tabletennis_api.models import (APIResponse, Event, EventSummary,
                                    PaginationInfo)


class TestEventsManager:
    """Test cases for EventsManager class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.api = TableTennisAPI(api_key="test-token")
        self.events_manager = self.api.events

    @responses.activate
    def test_get_inplay_success(self):
        """Test successful get_inplay request"""
        # Mock API response
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 1000, "total": 2},
            "results": [
                {
                    "id": "10380220",
                    "sport_id": "92",
                    "time": "1753811400",
                    "time_status": "2",
                    "league": {"id": "22307", "name": "Setka Cup", "cc": None},
                    "home": {
                        "id": "326189",
                        "name": "Maksym Mrykh",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "1131605",
                        "name": "Vitalii S Marushchak",
                        "image_id": 0,
                        "cc": None,
                    },
                    "ss": "3-2",
                    "scores": {
                        "1": {"home": "11", "away": "3"},
                        "2": {"home": "10", "away": "12"},
                    },
                    "bet365_id": "178677145",
                },
                {
                    "id": "10380702",
                    "sport_id": "92",
                    "time": "1753811400",
                    "time_status": "1",
                    "league": {"id": "29128", "name": "TT Elite Series", "cc": None},
                    "home": {
                        "id": "878509",
                        "name": "Michal Olbrycht",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "319111",
                        "name": "Krzysztof Kapik",
                        "image_id": 0,
                        "cc": None,
                    },
                    "ss": "12-14",
                    "scores": {"1": {"home": "13", "away": "11"}},
                    "bet365_id": "178665573",
                },
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/inplay",
            json=mock_response,
            status=200,
        )

        # Execute test
        result = self.events_manager.get_inplay()

        # Assertions
        assert isinstance(result, APIResponse)
        assert len(result.results) == 2
        assert result.pagination.total == 2
        assert result.pagination.page == 1

        # Check first event
        event1 = result.results[0]
        assert isinstance(event1, EventSummary)
        assert event1.id == "10380220"
        assert event1.home_player.name == "Maksym Mrykh"
        assert event1.away_player.name == "Vitalii S Marushchak"
        assert event1.league_name == "Setka Cup"
        assert event1.current_score == "3-2"
        assert event1.is_live  # time_status "2"
        assert not event1.is_scheduled
        assert not event1.is_finished

        # Check second event
        event2 = result.results[1]
        assert event2.id == "10380702"
        assert event2.home_player.name == "Michal Olbrycht"
        assert event2.is_scheduled  # time_status "1"
        assert not event2.is_live

    @responses.activate
    def test_get_inplay_with_league_filter(self):
        """Test get_inplay with league ID filter"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 1000, "total": 1},
            "results": [
                {
                    "id": "10385512",
                    "sport_id": "92",
                    "time": "1753811700",
                    "time_status": "3",
                    "league": {"id": "29097", "name": "TT Cup", "cc": "cz"},
                    "home": {
                        "id": "704817",
                        "name": "Jan Kocab",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "910936",
                        "name": "Jan Benak",
                        "image_id": 0,
                        "cc": None,
                    },
                    "ss": "3-0",
                    "scores": {},
                    "bet365_id": "178737920",
                }
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/inplay",
            json=mock_response,
            status=200,
        )

        # Execute test with league filter
        result = self.events_manager.get_inplay(league_id="29097")

        # Verify request parameters
        assert len(responses.calls) == 1
        request_params = responses.calls[0].request.url
        assert "league_id=29097" in request_params

        # Verify response
        assert len(result.results) == 1
        event = result.results[0]
        assert event.league_id == "29097"
        assert event.league_name == "TT Cup"
        assert event.league_country_code == "cz"
        assert event.is_finished  # time_status "3"

    @responses.activate
    def test_get_inplay_with_o_home_field(self):
        """Test get_inplay handles o_home field correctly"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 1000, "total": 1},
            "results": [
                {
                    "id": "10378028",
                    "sport_id": "92",
                    "time": "1753812000",
                    "time_status": "1",
                    "league": {"id": "22742", "name": "Czech Liga Pro", "cc": "cz"},
                    "home": {
                        "id": "568875",
                        "name": "Rostyslav Kliucuk",
                        "image_id": 0,
                        "cc": None,
                    },
                    "o_home": {
                        "id": "688991",
                        "name": "Rostyslav Kliuchuk",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "741786",
                        "name": "Ondrej Svacha",
                        "image_id": 0,
                        "cc": "cz",
                    },
                    "ss": "9-10",
                    "scores": {},
                    "bet365_id": "178661047",
                }
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/inplay",
            json=mock_response,
            status=200,
        )

        result = self.events_manager.get_inplay()

        # Should use o_home name instead of home name
        event = result.results[0]
        assert event.home_player.name == "Rostyslav Kliuchuk"  # From o_home
        assert event.home_player.id == "688991"  # From o_home

    @responses.activate
    def test_get_inplay_pagination(self):
        """Test get_inplay with pagination"""
        mock_response = {
            "success": 1,
            "pager": {"page": 2, "per_page": 50, "total": 100},
            "results": [],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/inplay",
            json=mock_response,
            status=200,
        )

        result = self.events_manager.get_inplay(page=2)

        # Verify request parameters
        request_params = responses.calls[0].request.url
        assert "page=2" in request_params

        # Verify pagination
        assert result.pagination.page == 2
        assert result.pagination.per_page == 50
        assert result.pagination.total == 100
        assert result.pagination.total_pages == 2
        assert not result.pagination.has_next_page
        assert result.pagination.has_previous_page

    def test_get_inplay_invalid_page(self):
        """Test get_inplay with invalid page number"""
        with pytest.raises(ValueError, match="Page number must be >= 1"):
            self.events_manager.get_inplay(page=0)

        with pytest.raises(ValueError, match="Page number must be >= 1"):
            self.events_manager.get_inplay(page=-1)

    @responses.activate
    def test_get_inplay_api_error(self):
        """Test get_inplay handles API errors"""
        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/inplay",
            json={"success": 0, "error": "Invalid token"},
            status=401,
        )

        with pytest.raises(TableTennisAPIError):
            self.events_manager.get_inplay()

    @responses.activate
    def test_get_inplay_empty_results(self):
        """Test get_inplay with empty results"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 1000, "total": 0},
            "results": [],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/inplay",
            json=mock_response,
            status=200,
        )

        result = self.events_manager.get_inplay()

        assert len(result.results) == 0
        assert result.pagination.total == 0
        assert result.pagination.total_pages == 0

    @responses.activate
    def test_get_details_single_event(self):
        """Test get_details with single event ID"""
        mock_response = {
            "success": 1,
            "results": [
                {
                    "id": "10385512",
                    "sport_id": "92",
                    "time": "1753811700",
                    "time_status": "3",
                    "league": {"id": "29097", "name": "TT Cup", "cc": "cz"},
                    "home": {
                        "id": "704817",
                        "name": "Jan Kocab",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "910936",
                        "name": "Jan Benak",
                        "image_id": 0,
                        "cc": None,
                    },
                    "ss": "3-0",
                    "scores": {
                        "1": {"home": "11", "away": "6"},
                        "2": {"home": "11", "away": "4"},
                        "3": {"home": "11", "away": "7"},
                    },
                    "timeline": [
                        {"id": "254604195", "gm": "1", "te": "0", "ss": "1-0"},
                        {"id": "254604214", "gm": "1", "te": "0", "ss": "2-0"},
                    ],
                    "extra": {
                        "bestofsets": "5",
                        "stadium_data": {
                            "id": "69585",
                            "name": "Czech 6",
                            "city": "Prague",
                            "country": "Czechia",
                            "capacity": None,
                            "googlecoords": None,
                        },
                    },
                    "inplay_created_at": "1753811088",
                    "inplay_updated_at": "1753812652",
                    "confirmed_at": "1753813011",
                    "bet365_id": "178737920",
                }
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/event/view",
            json=mock_response,
            status=200,
        )

        result = self.events_manager.get_details("10385512")

        # Verify request parameters
        request_params = responses.calls[0].request.url
        assert "event_id=10385512" in request_params

        # Verify response
        assert len(result) == 1
        event = result[0]
        assert isinstance(event, Event)
        assert event.id == "10385512"
        assert event.home_player.name == "Jan Kocab"
        assert event.away_player.name == "Jan Benak"
        assert event.final_score == "3-0"
        assert len(event.timeline) == 2
        assert event.extra is not None
        assert event.extra.stadium_data.name == "Czech 6"
        assert event.is_finished
        assert event.winner.name == "Jan Kocab"

    @responses.activate
    def test_get_details_multiple_events(self):
        """Test get_details with multiple event IDs"""
        mock_response = {
            "success": 1,
            "results": [
                {
                    "id": "10385512",
                    "sport_id": "92",
                    "time": "1753811700",
                    "time_status": "3",
                    "league": {"id": "29097", "name": "TT Cup", "cc": "cz"},
                    "home": {
                        "id": "704817",
                        "name": "Jan Kocab",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "910936",
                        "name": "Jan Benak",
                        "image_id": 0,
                        "cc": None,
                    },
                    "ss": "3-0",
                    "scores": {},
                    "timeline": [],
                    "bet365_id": "178737920",
                },
                {
                    "id": "10382865",
                    "sport_id": "92",
                    "time": "1753800600",
                    "time_status": "3",
                    "league": {"id": "29097", "name": "TT Cup", "cc": "cz"},
                    "home": {
                        "id": "682070",
                        "name": "Zdenek Zahradka",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "788338",
                        "name": "Jakub Dvorak",
                        "image_id": 0,
                        "cc": None,
                    },
                    "ss": "3-0",
                    "scores": {},
                    "timeline": [],
                    "bet365_id": "178714423",
                },
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/event/view",
            json=mock_response,
            status=200,
        )

        result = self.events_manager.get_details(["10385512", "10382865"])

        # Verify request parameters
        request_params = responses.calls[0].request.url
        assert "event_id=10385512%2C10382865" in request_params

        # Verify response
        assert len(result) == 2
        assert result[0].id == "10385512"
        assert result[1].id == "10382865"

    def test_get_details_too_many_ids(self):
        """Test get_details with too many event IDs"""
        event_ids = [str(i) for i in range(11)]  # 11 IDs

        with pytest.raises(
            ValueError, match="Maximum 10 event IDs allowed per request"
        ):
            self.events_manager.get_details(event_ids)

    @responses.activate
    def test_get_details_integer_ids(self):
        """Test get_details handles integer IDs correctly"""
        mock_response = {
            "success": 1,
            "results": [
                {
                    "id": "10385512",
                    "sport_id": "92",
                    "time": "1753811700",
                    "time_status": "3",
                    "league": {"id": "29097", "name": "TT Cup", "cc": "cz"},
                    "home": {
                        "id": "704817",
                        "name": "Jan Kocab",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "910936",
                        "name": "Jan Benak",
                        "image_id": 0,
                        "cc": None,
                    },
                    "ss": "3-0",
                    "scores": {},
                    "timeline": [],
                    "bet365_id": "178737920",
                }
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/event/view",
            json=mock_response,
            status=200,
        )

        # Test with integer ID
        result = self.events_manager.get_details(10385512)

        # Verify request parameters - should convert to string
        request_params = responses.calls[0].request.url
        assert "event_id=10385512" in request_params

        assert len(result) == 1
        assert result[0].id == "10385512"

    @responses.activate
    def test_search_success(self):
        """Test successful search request (if it worked)"""
        # Mock a hypothetical successful response
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 1000, "total": 1},
            "results": [
                {
                    "id": "10380220",
                    "sport_id": "92",
                    "time": "1753811400",
                    "time_status": "3",
                    "league": {"id": "22307", "name": "Setka Cup", "cc": None},
                    "home": {
                        "id": "326189",
                        "name": "Jan Novak",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "610334",
                        "name": "Petr Svoboda",
                        "image_id": 0,
                        "cc": None,
                    },
                    "ss": "3-1",
                }
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/events/search",
            json=mock_response,
            status=200,
        )

        result = self.events_manager.search(
            home="Jan Kocab", away="Jan Benak", time="20250729"
        )

        # Verify request parameters
        request_params = responses.calls[0].request.url
        assert "home=Jan+Kocab" in request_params
        assert "away=Jan+Benak" in request_params
        assert "time=20250729" in request_params
        assert "token=test-token" in request_params
        assert "sport_id=92" in request_params

        # Verify response
        assert len(result.results) == 1
        assert result.results[0].home_player.name == "Jan Novak"
        assert result.pagination.total == 1

    @responses.activate
    def test_search_param_required_error(self):
        """Test search with PARAM_REQUIRED error (current real behavior)"""
        mock_response = {"success": 0, "error": "PARAM_REQUIRED"}

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/events/search",
            json=mock_response,
            status=200,
        )

        with pytest.raises(TableTennisAPIError, match="API error: PARAM_REQUIRED"):
            self.events_manager.search(
                home="Jan Kocab", away="Jan Benak", time="20250729"
            )

    def test_search_no_criteria_error(self):
        """Test search with missing required parameters raises ValueError"""
        with pytest.raises(ValueError, match="All three parameters .* are required"):
            self.events_manager.search()

        with pytest.raises(ValueError, match="All three parameters .* are required"):
            self.events_manager.search(home="Jan Kocab")

        with pytest.raises(ValueError, match="All three parameters .* are required"):
            self.events_manager.search(home="Jan Kocab", away="Jan Benak")

    def test_search_invalid_page_error(self):
        """Test search with invalid page number raises ValueError"""
        with pytest.raises(ValueError, match="Page number must be >= 1"):
            self.events_manager.search(
                home="Jan Kocab", away="Jan Benak", time="20250729", page=0
            )

    @responses.activate
    def test_search_datetime_conversion(self):
        """Test search converts datetime objects to string format"""
        mock_response = {
            "success": 0,
            "error": "PARAM_REQUIRED",  # Expected current behavior
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/events/search",
            json=mock_response,
            status=200,
        )

        # Test with datetime object
        search_date = datetime(2025, 1, 15, 14, 30)

        with pytest.raises(TableTennisAPIError):
            self.events_manager.search(
                home="Jan Kocab", away="Jan Benak", time=search_date
            )

        # Verify datetime was converted to YYYYMMDD format
        request_params = responses.calls[0].request.url
        assert "time=20250115" in request_params

    @responses.activate
    def test_search_string_date(self):
        """Test search with string date format"""
        mock_response = {
            "success": 0,
            "error": "PARAM_REQUIRED",  # Expected current behavior
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/events/search",
            json=mock_response,
            status=200,
        )

        with pytest.raises(TableTennisAPIError):
            self.events_manager.search(
                home="Jan Kocab", away="Jan Benak", time="20250115"
            )

        # Verify string date passed through correctly
        request_params = responses.calls[0].request.url
        assert "time=20250115" in request_params

    @responses.activate
    def test_get_history_success(self):
        """Test successful get_history request with real structure"""
        # Mock response based on actual API structure from research
        mock_response = {
            "success": 1,
            "results": {
                "h2h": [
                    {
                        "id": "10380220",
                        "sport_id": "92",
                        "time": "1753811400",
                        "time_status": "3",
                        "league": {"id": "22307", "name": "TT Cup", "cc": "cz"},
                        "home": {
                            "id": "704817",
                            "name": "Jan Kocab",
                            "image_id": 0,
                            "cc": None,
                        },
                        "away": {
                            "id": "910936",
                            "name": "Jan Benak",
                            "image_id": 0,
                            "cc": None,
                        },
                        "ss": "3-1",
                    }
                ],
                "home": [
                    {
                        "id": "10380221",
                        "sport_id": "92",
                        "time": "1753811500",
                        "time_status": "3",
                        "league": {"id": "22307", "name": "TT Cup", "cc": "cz"},
                        "home": {
                            "id": "704817",
                            "name": "Jan Kocab",
                            "image_id": 0,
                            "cc": None,
                        },
                        "away": {
                            "id": "610334",
                            "name": "Petr Svoboda",
                            "image_id": 0,
                            "cc": None,
                        },
                        "ss": "3-0",
                    }
                ],
                "away": [
                    {
                        "id": "10380222",
                        "sport_id": "92",
                        "time": "1753811600",
                        "time_status": "3",
                        "league": {"id": "22307", "name": "TT Cup", "cc": "cz"},
                        "home": {
                            "id": "610334",
                            "name": "Petr Svoboda",
                            "image_id": 0,
                            "cc": None,
                        },
                        "away": {
                            "id": "704817",
                            "name": "Jan Kocab",
                            "image_id": 0,
                            "cc": None,
                        },
                        "ss": "1-3",
                    }
                ],
            },
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/event/history",
            json=mock_response,
            status=200,
        )

        result = self.events_manager.get_history("10385512", qty=10)

        # Verify request parameters
        request_params = responses.calls[0].request.url
        assert "event_id=10385512" in request_params
        assert "qty=10" in request_params
        assert "token=test-token" in request_params
        assert "sport_id=92" in request_params

        # Verify response structure
        assert isinstance(result, dict)
        assert "h2h" in result
        assert "home" in result
        assert "away" in result

        # Verify data parsing
        assert len(result["h2h"]) == 1
        assert len(result["home"]) == 1
        assert len(result["away"]) == 1

        # Verify event objects
        assert result["h2h"][0].home_player.name == "Jan Kocab"
        assert result["h2h"][0].away_player.name == "Jan Benak"

    @responses.activate
    def test_get_history_api_error(self):
        """Test get_history with API error"""
        mock_response = {"success": 0, "error": "INVALID_EVENT_ID"}

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/event/history",
            json=mock_response,
            status=200,
        )

        with pytest.raises(TableTennisAPIError, match="API error: INVALID_EVENT_ID"):
            self.events_manager.get_history("invalid_id")

    def test_get_history_empty_event_id_error(self):
        """Test get_history with empty event_id raises ValueError"""
        with pytest.raises(ValueError, match="event_id cannot be empty"):
            self.events_manager.get_history("")

    def test_get_history_invalid_qty_error(self):
        """Test get_history with invalid qty raises ValueError"""
        with pytest.raises(ValueError, match="qty must be between 1 and 20"):
            self.events_manager.get_history("10385512", qty=0)

        with pytest.raises(ValueError, match="qty must be between 1 and 20"):
            self.events_manager.get_history("10385512", qty=25)

    @responses.activate
    def test_get_history_integer_id(self):
        """Test get_history handles integer event IDs correctly"""
        mock_response = {"success": 1, "results": {"h2h": [], "home": [], "away": []}}

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/event/history",
            json=mock_response,
            status=200,
        )

        result = self.events_manager.get_history(10385512)  # Integer ID

        # Verify integer was converted to string
        request_params = responses.calls[0].request.url
        assert "event_id=10385512" in request_params

        # Verify response structure
        assert isinstance(result, dict)
        assert len(result["h2h"]) == 0

    @responses.activate
    def test_get_history_qty_parameter(self):
        """Test get_history qty parameter handling"""
        mock_response = {"success": 1, "results": {"h2h": [], "home": [], "away": []}}

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/event/history",
            json=mock_response,
            status=200,
        )

        result = self.events_manager.get_history("10385512", qty=15)

        # Verify qty parameter passed through
        request_params = responses.calls[0].request.url
        assert "qty=15" in request_params

        # Verify response structure
        assert isinstance(result, dict)

    @responses.activate
    def test_get_upcoming_success(self):
        """Test successful get_upcoming request"""
        # Mock API response
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 50, "total": 765},
            "results": [
                {
                    "id": "10384885",
                    "sport_id": "92",
                    "time": "1753809000",
                    "time_status": "0",
                    "league": {"id": "29097", "name": "TT Cup", "cc": "cz"},
                    "home": {
                        "id": "708148",
                        "name": "Pablo Heredia",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "942977",
                        "name": "Hector Puerto",
                        "image_id": 0,
                        "cc": None,
                    },
                    "ss": None,
                },
                {
                    "id": "10384634",
                    "sport_id": "92",
                    "time": "1753810200",
                    "time_status": "0",
                    "league": {"id": "29128", "name": "TT Elite Series", "cc": None},
                    "home": {
                        "id": "1051287",
                        "name": "Artur Kubiak",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "1027765",
                        "name": "Adam Staniczek",
                        "image_id": 0,
                        "cc": None,
                    },
                    "ss": None,
                },
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/upcoming",
            json=mock_response,
            status=200,
        )

        # Execute test
        result = self.events_manager.get_upcoming()

        # Assertions
        assert isinstance(result, APIResponse)
        assert len(result.results) == 2
        assert result.pagination.total == 765
        assert result.pagination.page == 1

        # Check first event
        event1 = result.results[0]
        assert isinstance(event1, EventSummary)
        assert event1.id == "10384885"
        assert event1.home_player.name == "Pablo Heredia"
        assert event1.away_player.name == "Hector Puerto"
        assert event1.league_name == "TT Cup"
        assert event1.current_score is None
        assert event1.is_scheduled  # time_status "0"
        assert not event1.is_live
        assert not event1.is_finished
        assert event1.status_description == "Upcoming"

        # Check second event
        event2 = result.results[1]
        assert event2.id == "10384634"
        assert event2.home_player.name == "Artur Kubiak"
        assert event2.is_scheduled  # time_status "0"
        assert event2.status_description == "Upcoming"

    @responses.activate
    def test_get_upcoming_with_league_filter(self):
        """Test get_upcoming with league ID filter"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 50, "total": 1},
            "results": [
                {
                    "id": "10384885",
                    "sport_id": "92",
                    "time": "1753809000",
                    "time_status": "0",
                    "league": {"id": "29097", "name": "TT Cup", "cc": "cz"},
                    "home": {
                        "id": "708148",
                        "name": "Pablo Heredia",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "942977",
                        "name": "Hector Puerto",
                        "image_id": 0,
                        "cc": None,
                    },
                    "ss": None,
                }
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/upcoming",
            json=mock_response,
            status=200,
        )

        # Execute test with league filter
        result = self.events_manager.get_upcoming(league_id="29097")

        # Verify request parameters
        assert len(responses.calls) == 1
        request_params = responses.calls[0].request.url
        assert "league_id=29097" in request_params

        # Verify response
        assert len(result.results) == 1
        event = result.results[0]
        assert event.league_id == "29097"
        assert event.league_name == "TT Cup"
        assert event.is_scheduled

    def test_get_upcoming_invalid_page(self):
        """Test get_upcoming with invalid page number"""
        with pytest.raises(ValueError, match="Page number must be >= 1"):
            self.events_manager.get_upcoming(page=0)

        with pytest.raises(ValueError, match="Page number must be >= 1"):
            self.events_manager.get_upcoming(page=-1)

    @responses.activate
    def test_get_upcoming_api_error(self):
        """Test get_upcoming handles API errors"""
        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/upcoming",
            json={"success": 0, "error": "Invalid token"},
            status=401,
        )

        with pytest.raises(TableTennisAPIError):
            self.events_manager.get_upcoming()

    @responses.activate
    def test_get_upcoming_empty_results(self):
        """Test get_upcoming with empty results"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 50, "total": 0},
            "results": [],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/upcoming",
            json=mock_response,
            status=200,
        )

        result = self.events_manager.get_upcoming()

        assert len(result.results) == 0
        assert result.pagination.total == 0
        assert result.pagination.total_pages == 0

    @responses.activate
    def test_get_ended_success(self):
        """Test successful get_ended request"""
        # Mock API response
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 50, "total": 1722538},
            "results": [
                {
                    "id": "10390123",
                    "sport_id": "92",
                    "time": "1753811700",
                    "time_status": "3",
                    "league": {"id": "29128", "name": "TT Elite Series", "cc": None},
                    "home": {
                        "id": "878509",
                        "name": "Adrian Fabis",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "319111",
                        "name": "Krzysztof Pawlowski",
                        "image_id": 0,
                        "cc": None,
                    },
                    "ss": "3-1",
                    "scores": {
                        "1": {"home": "11", "away": "9"},
                        "2": {"home": "8", "away": "11"},
                        "3": {"home": "11", "away": "6"},
                        "4": {"home": "11", "away": "3"},
                    },
                    "bet365_id": "178677201",
                },
                {
                    "id": "10390124",
                    "sport_id": "92",
                    "time": "1753811400",
                    "time_status": "3",
                    "league": {"id": "22307", "name": "Setka Cup", "cc": None},
                    "home": {
                        "id": "326189",
                        "name": "Volodymyr Okopnyi",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "1131605",
                        "name": "Volodymyr Kaidakov",
                        "image_id": 0,
                        "cc": None,
                    },
                    "ss": "3-0",
                    "scores": {
                        "1": {"home": "11", "away": "8"},
                        "2": {"home": "11", "away": "5"},
                        "3": {"home": "11", "away": "7"},
                    },
                    "bet365_id": "178677202",
                },
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/ended",
            json=mock_response,
            status=200,
        )

        # Execute test
        result = self.events_manager.get_ended()

        # Assertions
        assert isinstance(result, APIResponse)
        assert len(result.results) == 2
        assert result.pagination.total == 1722538
        assert result.pagination.page == 1

        # Check first event
        event1 = result.results[0]
        assert isinstance(event1, EventSummary)
        assert event1.id == "10390123"
        assert event1.home_player.name == "Adrian Fabis"
        assert event1.away_player.name == "Krzysztof Pawlowski"
        assert event1.league_name == "TT Elite Series"
        assert event1.current_score == "3-1"
        assert event1.is_finished  # time_status "3"
        assert not event1.is_live
        assert not event1.is_scheduled
        assert event1.status_description == "Finished"

        # Check second event
        event2 = result.results[1]
        assert event2.id == "10390124"
        assert event2.home_player.name == "Volodymyr Okopnyi"
        assert event2.current_score == "3-0"
        assert event2.is_finished

    @responses.activate
    def test_get_ended_with_league_filter(self):
        """Test get_ended with league ID filter"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 50, "total": 1250},
            "results": [
                {
                    "id": "10390150",
                    "sport_id": "92",
                    "time": "1753810800",
                    "time_status": "3",
                    "league": {"id": "29097", "name": "TT Cup", "cc": "cz"},
                    "home": {
                        "id": "704817",
                        "name": "Lukasz Latala",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "910936",
                        "name": "Wiekiera Arkadiusz",
                        "image_id": 0,
                        "cc": None,
                    },
                    "ss": "1-3",
                    "scores": {
                        "1": {"home": "11", "away": "6"},
                        "2": {"home": "9", "away": "11"},
                        "3": {"home": "7", "away": "11"},
                        "4": {"home": "5", "away": "11"},
                    },
                    "bet365_id": "178677250",
                }
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/ended",
            json=mock_response,
            status=200,
        )

        # Execute test with league filter
        result = self.events_manager.get_ended(league_id="29097")

        # Verify request parameters
        assert len(responses.calls) == 1
        request_params = responses.calls[0].request.url
        assert "league_id=29097" in request_params

        # Verify response
        assert len(result.results) == 1
        event = result.results[0]
        assert event.league_id == "29097"
        assert event.league_name == "TT Cup"
        assert event.league_country_code == "cz"
        assert event.is_finished
        assert event.current_score == "1-3"

    @responses.activate
    def test_get_ended_pagination(self):
        """Test get_ended with pagination"""
        mock_response = {
            "success": 1,
            "pager": {"page": 5, "per_page": 50, "total": 1722538},
            "results": [
                {
                    "id": "10390500",
                    "sport_id": "92",
                    "time": "1753800000",
                    "time_status": "3",
                    "league": {"id": "22307", "name": "Setka Cup", "cc": None},
                    "home": {
                        "id": "1001",
                        "name": "Test Player",
                        "image_id": 0,
                        "cc": None,
                    },
                    "away": {
                        "id": "1002",
                        "name": "Another Player",
                        "image_id": 0,
                        "cc": None,
                    },
                    "ss": "3-2",
                    "scores": {},
                    "bet365_id": "178677300",
                }
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/ended",
            json=mock_response,
            status=200,
        )

        result = self.events_manager.get_ended(page=5)

        # Verify request parameters
        request_params = responses.calls[0].request.url
        assert "page=5" in request_params

        # Verify pagination
        assert result.pagination.page == 5
        assert result.pagination.per_page == 50
        assert result.pagination.total == 1722538
        assert result.pagination.total_pages == 34451  # ceil(1722538/50)
        assert result.pagination.has_previous_page
        assert result.pagination.has_next_page

    def test_get_ended_invalid_page(self):
        """Test get_ended with invalid page number"""
        with pytest.raises(ValueError, match="Page number must be >= 1"):
            self.events_manager.get_ended(page=0)

        with pytest.raises(ValueError, match="Page number must be >= 1"):
            self.events_manager.get_ended(page=-1)

    @responses.activate
    def test_get_ended_api_error(self):
        """Test get_ended handles API errors"""
        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/ended",
            json={"success": 0, "error": "Invalid token"},
            status=401,
        )

        with pytest.raises(TableTennisAPIError):
            self.events_manager.get_ended()

    @responses.activate
    def test_get_ended_empty_results(self):
        """Test get_ended with empty results"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 50, "total": 0},
            "results": [],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/ended",
            json=mock_response,
            status=200,
        )

        result = self.events_manager.get_ended()

        assert len(result.results) == 0
        assert result.pagination.total == 0
        assert result.pagination.total_pages == 0


class TestEventSummaryModel:
    """Test cases for EventSummary model"""

    def test_event_summary_from_dict(self):
        """Test EventSummary creation from dictionary"""
        data = {
            "id": "10380220",
            "sport_id": "92",
            "time": "1753811400",
            "time_status": "2",
            "league": {"id": "22307", "name": "Setka Cup", "cc": None},
            "home": {"id": "326189", "name": "Maksym Mrykh", "image_id": 0, "cc": None},
            "away": {
                "id": "1131605",
                "name": "Vitalii S Marushchak",
                "image_id": 0,
                "cc": None,
            },
            "ss": "3-2",
            "scores": {
                "1": {"home": "11", "away": "3"},
                "2": {"home": "10", "away": "12"},
            },
            "bet365_id": "178677145",
        }

        event = EventSummary.from_dict(data)

        assert event.id == "10380220"
        assert event.sport_id == "92"
        assert event.time == "1753811400"
        assert event.time_status == "2"
        assert event.league_id == "22307"
        assert event.league_name == "Setka Cup"
        assert event.league_country_code is None
        assert event.home_player.name == "Maksym Mrykh"
        assert event.away_player.name == "Vitalii S Marushchak"
        assert event.current_score == "3-2"
        assert event.bet365_id == "178677145"

    def test_event_summary_properties(self):
        """Test EventSummary properties"""
        # Create event with time_status "2" (live)
        event = EventSummary(
            id="123",
            sport_id="92",
            time="1753811400",
            time_status="2",
            league_id="456",
            league_name="Test League",
            league_country_code="cz",
            home_player=None,
            away_player=None,
            current_score="3-2",
            game_scores={},
        )

        # Test status properties
        assert event.is_live
        assert not event.is_scheduled
        assert not event.is_finished
        assert event.status_description == "Live"

        # Test datetime conversion
        expected_datetime = datetime.fromtimestamp(1753811400)
        assert event.event_datetime == expected_datetime

        # Test sets score parsing
        assert event.sets_score == (3, 2)

        # Test current game score
        assert event.current_game_score == "3-2"

    def test_event_summary_with_o_home(self):
        """Test EventSummary handles o_home field correctly"""
        data = {
            "id": "10378028",
            "sport_id": "92",
            "time": "1753812000",
            "time_status": "1",
            "league": {"id": "22742", "name": "Czech Liga Pro", "cc": "cz"},
            "home": {
                "id": "568875",
                "name": "Rostyslav Kliucuk",
                "image_id": 0,
                "cc": None,
            },
            "o_home": {
                "id": "688991",
                "name": "Rostyslav Kliuchuk",
                "image_id": 0,
                "cc": None,
            },
            "away": {
                "id": "741786",
                "name": "Ondrej Svacha",
                "image_id": 0,
                "cc": "cz",
            },
            "ss": "9-10",
            "scores": {},
            "bet365_id": "178661047",
        }

        event = EventSummary.from_dict(data)

        # Should use o_home instead of home
        assert event.home_player.name == "Rostyslav Kliuchuk"
        assert event.home_player.id == "688991"


class TestEventSummaryModelExtended:
    """Additional test cases for EventSummary model with upcoming status"""

    def test_event_summary_upcoming_status(self):
        """Test EventSummary with upcoming status (0)"""
        event = EventSummary(
            id="123",
            sport_id="92",
            time="1753815300",
            time_status="0",  # Upcoming
            league_id="456",
            league_name="Test League",
            league_country_code="cz",
            home_player=None,
            away_player=None,
            current_score=None,
            game_scores={},
        )

        # Test status properties
        assert event.is_scheduled  # Should be True for "0"
        assert not event.is_live
        assert not event.is_finished
        assert event.status_description == "Upcoming"

        # Test null score handling
        assert event.current_score is None
        assert event.current_game_score is None

    def test_event_summary_with_o_away(self):
        """Test EventSummary handles both o_home and o_away fields correctly"""
        data = {
            "id": "10380039",
            "sport_id": "92",
            "time": "1753815300",
            "time_status": "0",
            "league": {"id": "22307", "name": "Setka Cup", "cc": None},
            "home": {"id": "355263", "name": "Oleg Gil", "image_id": 0, "cc": None},
            "o_home": {"id": "378311", "name": "Oleh Hil", "image_id": 0, "cc": None},
            "away": {
                "id": "339750",
                "name": "Mykolay Treschetka",
                "image_id": 0,
                "cc": None,
            },
            "o_away": {
                "id": "330138",
                "name": "Mykola Treshchetka",
                "image_id": 0,
                "cc": None,
            },
            "ss": None,
            "bet365_id": "178677157",
        }

        event = EventSummary.from_dict(data)

        # Should use o_home and o_away instead of home/away
        assert event.home_player.name == "Oleh Hil"
        assert event.home_player.id == "378311"
        assert event.away_player.name == "Mykola Treshchetka"
        assert event.away_player.id == "330138"


class TestEventModel:
    """Test cases for Event model (detailed event with timeline)"""

    def test_event_from_dict_complete(self):
        """Test Event creation from complete dictionary"""
        data = {
            "id": "10385512",
            "sport_id": "92",
            "time": "1753811700",
            "time_status": "3",
            "league": {"id": "29097", "name": "TT Cup", "cc": "cz"},
            "home": {"id": "704817", "name": "Jan Kocab", "image_id": 0, "cc": None},
            "away": {"id": "910936", "name": "Jan Benak", "image_id": 0, "cc": None},
            "ss": "3-0",
            "scores": {
                "1": {"home": "11", "away": "6"},
                "2": {"home": "11", "away": "4"},
                "3": {"home": "11", "away": "7"},
            },
            "timeline": [
                {"id": "254604195", "gm": "1", "te": "0", "ss": "1-0"},
                {"id": "254604214", "gm": "1", "te": "0", "ss": "2-0"},
                {"id": "254604232", "gm": "1", "te": "1", "ss": "2-1"},
            ],
            "extra": {
                "bestofsets": "5",
                "stadium_data": {
                    "id": "69585",
                    "name": "Czech 6",
                    "city": "Prague",
                    "country": "Czechia",
                    "capacity": None,
                    "googlecoords": None,
                },
            },
            "inplay_created_at": "1753811088",
            "inplay_updated_at": "1753812652",
            "confirmed_at": "1753813011",
            "bet365_id": "178737920",
        }

        from tabletennis_api.models import Event

        event = Event.from_dict(data)

        # Basic fields
        assert event.id == "10385512"
        assert event.sport_id == "92"
        assert event.time == "1753811700"
        assert event.time_status == "3"
        assert event.league_id == "29097"
        assert event.league_name == "TT Cup"
        assert event.league_country_code == "cz"
        assert event.final_score == "3-0"

        # Players
        assert event.home_player.name == "Jan Kocab"
        assert event.home_player.id == "704817"
        assert event.away_player.name == "Jan Benak"
        assert event.away_player.id == "910936"

        # Timeline
        assert len(event.timeline) == 3
        assert event.timeline[0].id == "254604195"
        assert event.timeline[0].game == "1"
        assert event.timeline[0].team == "0"
        assert event.timeline[0].score == "1-0"

        # Extra data
        assert event.extra is not None
        assert event.extra.best_of_sets == "5"
        assert event.extra.stadium_data is not None
        assert event.extra.stadium_data.name == "Czech 6"
        assert event.extra.stadium_data.city == "Prague"
        assert event.extra.stadium_data.country == "Czechia"

        # Timestamps
        assert event.inplay_created_at == "1753811088"
        assert event.inplay_updated_at == "1753812652"
        assert event.confirmed_at == "1753813011"
        assert event.bet365_id == "178737920"

    def test_event_properties(self):
        """Test Event properties and computed fields"""
        from datetime import datetime

        from tabletennis_api.models import Event, Player

        event = Event(
            id="123",
            sport_id="92",
            time="1753811700",
            time_status="3",
            league_id="456",
            league_name="Test League",
            league_country_code="cz",
            home_player=Player(id="1", name="Player A"),
            away_player=Player(id="2", name="Player B"),
            final_score="3-1",
            game_scores={},
            timeline=[],
        )

        # Status properties
        assert not event.is_scheduled
        assert not event.is_live
        assert event.is_finished
        assert event.status_description == "Finished"

        # Score properties
        assert event.home_sets_won == 3
        assert event.away_sets_won == 1

        # Winner detection
        winner = event.winner
        assert winner is not None
        assert winner.name == "Player A"

        # Datetime conversion
        expected_datetime = datetime.fromtimestamp(1753811700)
        assert event.event_datetime == expected_datetime

        # Timeline count
        assert event.total_points_played == 0

    def test_event_timeline_properties(self):
        """Test timeline entry properties"""
        from tabletennis_api.models import TimelineEntry

        timeline_entry = TimelineEntry(id="254604195", game="1", team="0", score="5-3")

        assert timeline_entry.home_score == 5
        assert timeline_entry.away_score == 3
        assert timeline_entry.scoring_team == "home"

        # Test away team scoring
        away_entry = TimelineEntry(id="254604232", game="1", team="1", score="2-1")

        assert away_entry.home_score == 2
        assert away_entry.away_score == 1
        assert away_entry.scoring_team == "away"

    def test_stadium_data_model(self):
        """Test StadiumData model"""
        from tabletennis_api.models import StadiumData

        data = {
            "id": "69585",
            "name": "Czech 6",
            "city": "Prague",
            "country": "Czechia",
            "capacity": 1000,
            "googlecoords": "50.0755,14.4378",
        }

        stadium = StadiumData.from_dict(data)

        assert stadium.id == "69585"
        assert stadium.name == "Czech 6"
        assert stadium.city == "Prague"
        assert stadium.country == "Czechia"
        assert stadium.capacity == 1000
        assert stadium.coordinates == "50.0755,14.4378"

    def test_event_extra_model(self):
        """Test EventExtra model"""
        from tabletennis_api.models import EventExtra

        data = {
            "bestofsets": "5",
            "stadium_data": {
                "id": "69585",
                "name": "Czech 6",
                "city": "Prague",
                "country": "Czechia",
                "capacity": None,
                "googlecoords": None,
            },
        }

        extra = EventExtra.from_dict(data)

        assert extra.best_of_sets == "5"
        assert extra.stadium_data is not None
        assert extra.stadium_data.name == "Czech 6"

    def test_event_extra_without_stadium(self):
        """Test EventExtra model without stadium data"""
        from tabletennis_api.models import EventExtra

        data = {"bestofsets": "3"}

        extra = EventExtra.from_dict(data)

        assert extra.best_of_sets == "3"
        assert extra.stadium_data is None

    def test_event_winner_detection(self):
        """Test winner detection for different scenarios"""
        from tabletennis_api.models import Event, Player

        home_player = Player(id="1", name="Home Player")
        away_player = Player(id="2", name="Away Player")

        # Test home player wins
        home_wins = Event(
            id="1",
            sport_id="92",
            time="123",
            time_status="3",
            league_id="1",
            league_name="Test",
            league_country_code=None,
            home_player=home_player,
            away_player=away_player,
            final_score="3-1",
            game_scores={},
            timeline=[],
        )

        assert home_wins.winner == home_player

        # Test away player wins
        away_wins = Event(
            id="2",
            sport_id="92",
            time="123",
            time_status="3",
            league_id="1",
            league_name="Test",
            league_country_code=None,
            home_player=home_player,
            away_player=away_player,
            final_score="1-3",
            game_scores={},
            timeline=[],
        )

        assert away_wins.winner == away_player

        # Test live match (no winner yet)
        live_match = Event(
            id="3",
            sport_id="92",
            time="123",
            time_status="2",
            league_id="1",
            league_name="Test",
            league_country_code=None,
            home_player=home_player,
            away_player=away_player,
            final_score="2-1",
            game_scores={},
            timeline=[],
        )

        assert live_match.winner is None
        assert live_match.is_live

        # Test scheduled match (no winner yet)
        scheduled_match = Event(
            id="4",
            sport_id="92",
            time="123",
            time_status="1",
            league_id="1",
            league_name="Test",
            league_country_code=None,
            home_player=home_player,
            away_player=away_player,
            final_score="0-0",
            game_scores={},
            timeline=[],
        )

        assert scheduled_match.winner is None
        assert scheduled_match.is_scheduled
