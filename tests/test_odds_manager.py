"""
Unit tests for OddsManager class
"""

import pytest
import responses
from tabletennis_api.managers import OddsManager
from tabletennis_api.client import TableTennisAPI
from tabletennis_api.exceptions import TableTennisAPIError


class TestOddsManager:
    """Test cases for OddsManager class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.api = TableTennisAPI(api_key="test-token")
        self.odds_manager = self.api.odds
    
    @responses.activate
    def test_get_summary_success(self):
        """Test successful get_summary request"""
        # Mock API response based on research data
        mock_response = {
            "success": 1,
            "results": {
                "Bet365": {
                    "matching_dir": 1,
                    "odds_update": {},
                    "odds": {
                        "start": {
                            "92_1": {
                                "id": "110085545",
                                "home_od": "1.571",
                                "away_od": "2.250",
                                "ss": "0-0",
                                "add_time": "1753811094"
                            },
                            "92_2": {
                                "id": "57586658",
                                "home_od": "2.250",
                                "handicap": "-1.5",
                                "away_od": "1.571",
                                "ss": "0-0",
                                "add_time": "1753811094"
                            },
                            "92_3": {
                                "id": "51952191",
                                "over_od": "1.833",
                                "handicap": "75.5",
                                "under_od": "1.833",
                                "ss": "0-0",
                                "add_time": "1753811094"
                            }
                        },
                        "kickoff": {
                            "92_1": {
                                "id": "110085545",
                                "home_od": "1.571",
                                "away_od": "2.250",
                                "ss": "0-0",
                                "add_time": "1753811094"
                            }
                        },
                        "end": {
                            "92_1": {
                                "id": "110086866",
                                "home_od": "1.005",
                                "away_od": "17.000",
                                "ss": "11-6,11-4,10-7",
                                "add_time": "1753812584"
                            }
                        }
                    }
                },
                "DafaBet": {
                    "matching_dir": 1,
                    "odds_update": {},
                    "odds": {
                        "start": {},
                        "kickoff": {},
                        "end": {}
                    }
                }
            }
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/event/odds/summary",
            json=mock_response,
            status=200
        )
        
        result = self.odds_manager.get_summary("10385512")
        
        # Verify request parameters
        request_params = responses.calls[0].request.url
        assert "event_id=10385512" in request_params
        assert "token=test-token" in request_params
        assert "sport_id=92" in request_params
        
        # Verify response
        assert isinstance(result, dict)
        assert "Bet365" in result
        assert "DafaBet" in result
        
        # Verify Bet365 data structure
        bet365_data = result["Bet365"]
        assert "odds" in bet365_data
        assert "start" in bet365_data["odds"]
        assert "kickoff" in bet365_data["odds"]
        assert "end" in bet365_data["odds"]
        
        # Verify specific odds data
        start_odds = bet365_data["odds"]["start"]
        assert "92_1" in start_odds  # Match winner
        assert "92_2" in start_odds  # Handicap
        assert "92_3" in start_odds  # Over/Under
        
        # Verify match winner odds
        match_winner = start_odds["92_1"]
        assert match_winner["home_od"] == "1.571"
        assert match_winner["away_od"] == "2.250"
    
    @responses.activate
    def test_get_summary_api_error(self):
        """Test get_summary with API error"""
        mock_response = {
            "success": 0,
            "error": "EVENT_NOT_FOUND"
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/event/odds/summary",
            json=mock_response,
            status=200
        )
        
        with pytest.raises(TableTennisAPIError, match="API error: EVENT_NOT_FOUND"):
            self.odds_manager.get_summary("invalid_event_id")
    
    @responses.activate
    def test_get_summary_empty_results(self):
        """Test get_summary with empty results"""
        mock_response = {
            "success": 1,
            "results": {}
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/event/odds/summary",
            json=mock_response,
            status=200
        )
        
        result = self.odds_manager.get_summary("10385512")
        
        # Should return empty dict when no results
        assert result == {}
    
    @responses.activate
    def test_get_detailed_success(self):
        """Test successful get_detailed request"""
        # Mock API response based on research data (abbreviated for readability)
        mock_response = {
            "success": 1,
            "results": {
                "stats": {
                    "matching_dir": 1,
                    "odds_update": {}
                },
                "odds": {
                    "92_1": [
                        {
                            "id": "110086878",
                            "home_od": "-",
                            "away_od": "-",
                            "ss": "11-6,11-4,11-7",
                            "add_time": "1753812599"
                        },
                        {
                            "id": "110086866",
                            "home_od": "1.005",
                            "away_od": "17.000",
                            "ss": "11-6,11-4,10-7",
                            "add_time": "1753812584"
                        },
                        {
                            "id": "110085545",
                            "home_od": "1.571",
                            "away_od": "2.250",
                            "ss": "0-0",
                            "add_time": "1753811094"
                        }
                    ],
                    "92_2": [
                        {
                            "id": "57587168",
                            "home_od": "-",
                            "handicap": "-2.5",
                            "away_od": "-",
                            "ss": "11-6,10-4",
                            "add_time": "1753812288"
                        },
                        {
                            "id": "57586658",
                            "home_od": "2.250",
                            "handicap": "-1.5",
                            "away_od": "1.571",
                            "ss": "0-0",
                            "add_time": "1753811094"
                        }
                    ],
                    "92_3": [
                        {
                            "id": "51952671",
                            "over_od": "1.909",
                            "handicap": "54.5",
                            "under_od": "1.800",
                            "ss": "11-6,10-4",
                            "add_time": "1753812288"
                        },
                        {
                            "id": "51952191",
                            "over_od": "1.833",
                            "handicap": "75.5",
                            "under_od": "1.833",
                            "ss": "0-0",
                            "add_time": "1753811094"
                        }
                    ]
                }
            }
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/event/odds",
            json=mock_response,
            status=200
        )
        
        result = self.odds_manager.get_detailed("10385512", "bet365")
        
        # Verify request parameters
        request_params = responses.calls[0].request.url
        assert "event_id=10385512" in request_params
        assert "source=bet365" in request_params
        assert "token=test-token" in request_params
        assert "sport_id=92" in request_params
        
        # Verify response structure
        assert isinstance(result, dict)
        assert "stats" in result
        assert "odds" in result
        
        # Verify odds categories
        odds = result["odds"]
        assert "92_1" in odds  # Match winner
        assert "92_2" in odds  # Handicap
        assert "92_3" in odds  # Over/Under
        
        # Verify match winner odds history
        match_winner_history = odds["92_1"]
        assert len(match_winner_history) == 3
        
        # Verify final odds (first in list)
        final_odds = match_winner_history[0]
        assert final_odds["id"] == "110086878"
        assert final_odds["ss"] == "11-6,11-4,11-7"
        
        # Verify opening odds (last in list)
        opening_odds = match_winner_history[-1]
        assert opening_odds["home_od"] == "1.571"
        assert opening_odds["away_od"] == "2.250"
        assert opening_odds["ss"] == "0-0"
    
    @responses.activate
    def test_get_detailed_default_bookmaker(self):
        """Test get_detailed with default bookmaker parameter"""
        mock_response = {
            "success": 1,
            "results": {
                "stats": {"matching_dir": 1, "odds_update": {}},
                "odds": {"92_1": []}
            }
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/event/odds",
            json=mock_response,
            status=200
        )
        
        # Test without specifying bookmaker (should default to bet365)
        result = self.odds_manager.get_detailed("10385512")
        
        # Verify default bookmaker parameter
        request_params = responses.calls[0].request.url
        assert "source=bet365" in request_params
        
        assert isinstance(result, dict)
    
    @responses.activate
    def test_get_detailed_custom_bookmaker(self):
        """Test get_detailed with custom bookmaker"""
        mock_response = {
            "success": 1,
            "results": {
                "stats": {"matching_dir": 1, "odds_update": {}},
                "odds": {"92_1": []}
            }
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/event/odds",
            json=mock_response,
            status=200
        )
        
        result = self.odds_manager.get_detailed("10385512", "pinnacle")
        
        # Verify custom bookmaker parameter
        request_params = responses.calls[0].request.url
        assert "source=pinnacle" in request_params
        
        assert isinstance(result, dict)
    
    @responses.activate
    def test_get_detailed_api_error(self):
        """Test get_detailed with API error"""
        mock_response = {
            "success": 0,
            "error": "ODDS_NOT_AVAILABLE"
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/event/odds",
            json=mock_response,
            status=200
        )
        
        with pytest.raises(TableTennisAPIError, match="API error: ODDS_NOT_AVAILABLE"):
            self.odds_manager.get_detailed("invalid_event_id")
    
    @responses.activate
    def test_get_detailed_empty_results(self):
        """Test get_detailed with empty results"""
        mock_response = {
            "success": 1,
            "results": {}
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/event/odds",
            json=mock_response,
            status=200
        )
        
        result = self.odds_manager.get_detailed("10385512")
        
        # Should return empty dict when no results
        assert result == {}
    
    def test_odds_manager_inheritance(self):
        """Test that OddsManager inherits from BaseManager correctly"""
        from tabletennis_api.managers import BaseManager
        
        assert isinstance(self.odds_manager, BaseManager)
        assert hasattr(self.odds_manager, 'client')
        assert hasattr(self.odds_manager, '_make_request')
    
    @responses.activate
    def test_odds_integration_with_events(self):
        """Test integration between OddsManager and EventsManager"""
        # This test demonstrates how odds data relates to event data
        
        # Mock event data
        event_mock = {
            "success": 1,
            "results": [{
                "id": "10385512",
                "sport_id": "92",
                "time": "1753811700",
                "time_status": "3",
                "league": {"id": "29097", "name": "TT Cup", "cc": "cz"},
                "home": {"id": "704817", "name": "Jan Kocab", "image_id": 0, "cc": None},
                "away": {"id": "910936", "name": "Jan Benak", "image_id": 0, "cc": None},
                "ss": "3-0"
            }]
        }
        
        # Mock odds summary
        odds_mock = {
            "success": 1,
            "results": {
                "Bet365": {
                    "odds": {
                        "start": {
                            "92_1": {
                                "home_od": "1.571",
                                "away_od": "2.250"
                            }
                        }
                    }
                }
            }
        }
        
        responses.add(responses.GET, "https://api.b365api.com/v1/event/view", json=event_mock)
        responses.add(responses.GET, "https://api.b365api.com/v2/event/odds/summary", json=odds_mock)
        
        # Get event details
        events = self.api.events.get_details("10385512")
        event = events[0]
        
        # Get odds for the same event
        odds = self.odds_manager.get_summary(event.id)
        
        # Verify integration
        assert event.id == "10385512"
        assert event.home_player.name == "Jan Kocab"
        assert event.away_player.name == "Jan Benak"
        assert "Bet365" in odds
        
        # Verify we can get odds data for the event
        bet365_odds = odds["Bet365"]["odds"]["start"]["92_1"]
        assert float(bet365_odds["home_od"]) < float(bet365_odds["away_od"])  # Home player was favorite