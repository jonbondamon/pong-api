"""
Unit tests for EventsManager bulk data collection methods.
Tests the new get_player_history method with comprehensive coverage.
"""

import pytest
import responses
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from tabletennis_api.managers import EventsManager
from tabletennis_api.client import TableTennisAPI
from tabletennis_api.exceptions import TableTennisAPIError
from tabletennis_api.models import PlayerMatchHistory, TournamentData


class TestEventsManagerBulkMethods:
    """Test cases for EventsManager bulk data collection methods"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.api = TableTennisAPI(api_key="test-token")
        self.events_manager = self.api.events
    
    def test_get_player_history_validation(self):
        """Test input validation for get_player_history"""
        
        # Test empty player name
        with pytest.raises(ValueError, match="player_name cannot be empty"):
            self.events_manager.get_player_history("")
        
        with pytest.raises(ValueError, match="player_name cannot be empty"):
            self.events_manager.get_player_history("   ")
        
        # Test invalid days
        with pytest.raises(ValueError, match="days must be between 1 and 365"):
            self.events_manager.get_player_history("Jan Kocab", days=0)
        
        with pytest.raises(ValueError, match="days must be between 1 and 365"):
            self.events_manager.get_player_history("Jan Kocab", days=366)
        
        # Test invalid max_pages
        with pytest.raises(ValueError, match="max_pages must be between 1 and 50"):
            self.events_manager.get_player_history("Jan Kocab", max_pages=0)
        
        with pytest.raises(ValueError, match="max_pages must be between 1 and 50"):
            self.events_manager.get_player_history("Jan Kocab", max_pages=51)
    
    @patch('tabletennis_api.managers.EventsManager._get_recent_player_matches')
    def test_get_player_history_basic_success(self, mock_get_matches):
        """Test successful get_player_history without H2H"""
        
        # Mock recent matches data
        home_player_1 = MagicMock()
        home_player_1.name = "Jan Kocab"
        away_player_1 = MagicMock()
        away_player_1.name = "Jan Benak"
        
        home_player_2 = MagicMock()
        home_player_2.name = "Petr Novak"
        away_player_2 = MagicMock()
        away_player_2.name = "Jan Kocab"
        
        mock_matches = [
            MagicMock(
                id="1001",
                home_player=home_player_1,
                away_player=away_player_1,
                league_name="TT Cup",
                event_datetime=datetime.now() - timedelta(days=1),
                is_finished=True,
                sets_score=(3, 1)
            ),
            MagicMock(
                id="1002", 
                home_player=home_player_2,
                away_player=away_player_2,
                league_name="WTT Tournament",
                event_datetime=datetime.now() - timedelta(days=5),
                is_finished=True,
                sets_score=(1, 3)
            )
        ]
        
        # Configure mock to return wins/losses correctly
        mock_matches[0].is_winner.return_value = True   # Jan Kocab wins
        mock_matches[1].is_winner.return_value = False  # Jan Kocab loses
        
        mock_get_matches.return_value = mock_matches
        
        # Test method call
        result = self.events_manager.get_player_history(
            player_name="Jan Kocab",
            days=30,
            include_h2h=False
        )
        
        # Verify result type and basic structure
        assert isinstance(result, PlayerMatchHistory)
        assert result.player_name == "Jan Kocab"
        assert result.total_matches == 2
        assert result.win_count == 1
        assert result.loss_count == 1
        assert result.win_rate == 0.5
        assert result.date_range_days == 30
        
        # Verify tournaments and opponents are extracted
        assert "TT Cup" in result.tournaments
        assert "WTT Tournament" in result.tournaments
        assert "Jan Benak" in result.opponents
        assert "Petr Novak" in result.opponents
        
        # Verify helper method was called correctly
        mock_get_matches.assert_called_once_with("Jan Kocab", 30, 10)
    
    @patch('tabletennis_api.managers.EventsManager._get_recent_player_matches')
    @patch('tabletennis_api.managers.EventsManager._get_h2h_matches')
    def test_get_player_history_with_h2h(self, mock_get_h2h, mock_get_matches):
        """Test get_player_history with H2H records enabled"""
        
        # Mock main matches
        home_player = MagicMock()
        home_player.name = "Jan Kocab"
        away_player = MagicMock()
        away_player.name = "Jan Benak"
        
        mock_matches = [
            MagicMock(
                id="1001",
                home_player=home_player,
                away_player=away_player,
                league_name="TT Cup",
                is_finished=True
            )
        ]
        mock_matches[0].is_winner.return_value = True
        mock_get_matches.return_value = mock_matches
        
        # Mock H2H matches
        mock_h2h_matches = [
            MagicMock(id="2001"),
            MagicMock(id="2002")
        ]
        mock_get_h2h.return_value = mock_h2h_matches
        
        # Test method call with H2H enabled
        result = self.events_manager.get_player_history(
            player_name="Jan Kocab",
            days=30,
            include_h2h=True,
            max_pages=5
        )
        
        # Verify H2H records are included
        assert len(result.h2h_records) > 0
        assert "Jan Benak" in result.h2h_records
        assert result.h2h_records["Jan Benak"] == mock_h2h_matches
        
        # Verify H2H method was called
        mock_get_h2h.assert_called_once_with("Jan Kocab", "Jan Benak", 60)  # days * 2
    
    @patch('tabletennis_api.managers.EventsManager._get_recent_player_matches')
    def test_get_player_history_no_matches(self, mock_get_matches):
        """Test get_player_history when no matches are found"""
        
        # Mock empty results
        mock_get_matches.return_value = []
        
        # Test method call
        result = self.events_manager.get_player_history("Unknown Player")
        
        # Verify empty result structure
        assert isinstance(result, PlayerMatchHistory)
        assert result.player_name == "Unknown Player"
        assert result.total_matches == 0
        assert result.win_count == 0
        assert result.loss_count == 0
        assert result.win_rate == 0.0
        assert len(result.tournaments) == 0
        assert len(result.opponents) == 0
        assert len(result.h2h_records) == 0
    
    @patch('tabletennis_api.managers.EventsManager._get_recent_player_matches')
    def test_get_player_history_exception_handling(self, mock_get_matches):
        """Test get_player_history handles exceptions gracefully"""
        
        # Mock exception in recent matches search
        mock_get_matches.side_effect = TableTennisAPIError("API Error")
        
        # Test method call - should not raise exception
        result = self.events_manager.get_player_history("Jan Kocab")
        
        # Should return empty result when search fails
        assert isinstance(result, PlayerMatchHistory)
        assert result.total_matches == 0
    
    @responses.activate
    def test_get_recent_player_matches_helper(self):
        """Test _get_recent_player_matches helper method"""
        
        # Mock API response for ended events
        mock_response = {
            "success": 1,
            "results": [
                {
                    "id": "10001",
                    "sport_id": "92",
                    "time": str(int((datetime.now() - timedelta(days=2)).timestamp())),
                    "time_status": "3",
                    "league": {"id": "29097", "name": "TT Cup", "cc": "cz"},
                    "home": {"id": "701", "name": "Jan Kocab", "cc": None},
                    "away": {"id": "702", "name": "Jan Benak", "cc": None},
                    "ss": "3-1"
                },
                {
                    "id": "10002", 
                    "sport_id": "92",
                    "time": str(int((datetime.now() - timedelta(days=40)).timestamp())),  # Too old
                    "time_status": "3",
                    "league": {"id": "29097", "name": "TT Cup", "cc": "cz"},
                    "home": {"id": "701", "name": "Jan Kocab", "cc": None},
                    "away": {"id": "783", "name": "Other Player", "cc": None},
                    "ss": "3-0"
                },
                {
                    "id": "10003",
                    "sport_id": "92", 
                    "time": str(int((datetime.now() - timedelta(days=1)).timestamp())),
                    "time_status": "3",
                    "league": {"id": "29098", "name": "WTT", "cc": "int"},
                    "home": {"id": "784", "name": "Other Player", "cc": None},
                    "away": {"id": "701", "name": "Jan Kocab", "cc": None},
                    "ss": "2-3"
                }
            ],
            "pager": {"page": 1, "per_page": 50, "total": 3}
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/ended",
            json=mock_response,
            status=200
        )
        
        # Test helper method
        matches = self.events_manager._get_recent_player_matches("Jan Kocab", 30, 5)
        
        # Should find 2 matches (1 too old should be filtered out)
        assert len(matches) == 2
        
        # Verify correct matches were found
        match_ids = [match.id for match in matches]
        assert "10001" in match_ids  # Recent match as home
        assert "10003" in match_ids  # Recent match as away
        assert "10002" not in match_ids  # Too old, should be filtered
    
    @patch('tabletennis_api.managers.EventsManager._get_recent_player_matches')
    def test_get_h2h_matches_helper(self, mock_get_matches):
        """Test _get_h2h_matches helper method"""
        
        # Mock matches for player1 
        jan_kocab = MagicMock()
        jan_kocab.name = "Jan Kocab"
        jan_benak = MagicMock()
        jan_benak.name = "Jan Benak"
        other_player = MagicMock()
        other_player.name = "Other Player"
        
        mock_matches = [
            MagicMock(
                id="h2h001",
                home_player=jan_kocab,
                away_player=jan_benak
            ),
            MagicMock(
                id="h2h002", 
                home_player=jan_kocab,
                away_player=other_player  # Different opponent
            ),
            MagicMock(
                id="h2h003",
                home_player=jan_benak,
                away_player=jan_kocab  # Reverse match
            )
        ]
        mock_get_matches.return_value = mock_matches
        
        # Test H2H method
        h2h_matches = self.events_manager._get_h2h_matches("Jan Kocab", "Jan Benak", 60)
        
        # Should find 2 matches (both orders)
        assert len(h2h_matches) == 2
        
        # Verify correct matches were found
        h2h_ids = [match.id for match in h2h_matches] 
        assert "h2h001" in h2h_ids  # Jan Kocab vs Jan Benak
        assert "h2h003" in h2h_ids  # Jan Benak vs Jan Kocab
        assert "h2h002" not in h2h_ids  # Different opponent
    
    def test_player_match_history_model_properties(self):
        """Test PlayerMatchHistory model properties and methods"""
        
        # Create mock matches with known outcomes
        mock_matches = []
        for i in range(5):
            match = MagicMock()
            match.id = f"match_{i}"
            match.league_name = f"Tournament_{i % 2}"  # 2 different tournaments
            match.home_player.name = "Jan Kocab" if i % 2 == 0 else f"Opponent_{i}"
            match.away_player.name = f"Opponent_{i}" if i % 2 == 0 else "Jan Kocab"
            match.event_datetime = datetime.now() - timedelta(days=i)
            match.is_winner.return_value = i < 3  # First 3 are wins
            mock_matches.append(match)
        
        # Create PlayerMatchHistory object
        history = PlayerMatchHistory.from_matches(
            player_name="Jan Kocab",
            matches=mock_matches,
            h2h_records={"Opponent_1": mock_matches[:2]},
            date_range_days=30
        )
        
        # Test properties
        assert history.total_matches == 5
        assert history.win_count == 3
        assert history.loss_count == 2
        assert history.win_rate == 0.6
        assert history.date_range_days == 30
        
        # Test tournaments extraction
        assert len(history.tournaments) == 2
        assert "Tournament_0" in history.tournaments
        assert "Tournament_1" in history.tournaments
        
        # Test opponents extraction  
        assert len(history.opponents) == 5  # All different opponents
        
        # Test H2H records
        assert len(history.h2h_records) == 1
        assert "Opponent_1" in history.h2h_records
        
        # Test recent form (should be boolean list)
        recent_form = history.recent_form
        assert isinstance(recent_form, list)
        assert len(recent_form) <= 10  # Max 10 recent matches
        assert all(isinstance(result, bool) for result in recent_form)


class TestTournamentCompleteMethods:
    """Test cases for get_tournament_complete method"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.api = TableTennisAPI(api_key="test-token")
        self.events_manager = self.api.events
    
    def test_get_tournament_complete_validation(self):
        """Test input validation for get_tournament_complete"""
        
        # Test empty tournament ID
        with pytest.raises(ValueError, match="tournament_id cannot be empty"):
            self.events_manager.get_tournament_complete("")
        
        with pytest.raises(ValueError, match="tournament_id cannot be empty"):
            self.events_manager.get_tournament_complete("   ")
        
        # Test invalid max_pages_per_type
        with pytest.raises(ValueError, match="max_pages_per_type must be between 1 and 20"):
            self.events_manager.get_tournament_complete("12345", max_pages_per_type=0)
        
        with pytest.raises(ValueError, match="max_pages_per_type must be between 1 and 20"):
            self.events_manager.get_tournament_complete("12345", max_pages_per_type=21)
    
    @patch('tabletennis_api.managers.EventsManager._get_tournament_matches')
    def test_get_tournament_complete_basic_success(self, mock_get_matches):
        """Test successful get_tournament_complete without odds"""
        
        # Mock tournament matches for different types
        ended_match = MagicMock()
        ended_match.id = "match_1"
        ended_match.league_name = "Test Tournament"
        ended_match.league_id = "12345"
        ended_match.is_finished = True
        ended_match.is_live = False
        ended_match.is_scheduled = False
        ended_match.home_player = MagicMock()
        ended_match.home_player.name = "Player A"
        ended_match.home_player.id = "player_a"
        ended_match.away_player = MagicMock()
        ended_match.away_player.name = "Player B"
        ended_match.away_player.id = "player_b"
        ended_match.event_datetime = datetime.now() - timedelta(days=1)
        
        upcoming_match = MagicMock()
        upcoming_match.id = "match_2"
        upcoming_match.league_name = "Test Tournament"
        upcoming_match.league_id = "12345"
        upcoming_match.is_finished = False
        upcoming_match.is_live = False
        upcoming_match.is_scheduled = True
        upcoming_match.home_player = MagicMock()
        upcoming_match.home_player.name = "Player C"
        upcoming_match.home_player.id = "player_c"
        upcoming_match.away_player = MagicMock()
        upcoming_match.away_player.name = "Player D"
        upcoming_match.away_player.id = "player_d"
        upcoming_match.event_datetime = datetime.now() + timedelta(days=1)
        
        live_match = MagicMock()
        live_match.id = "match_3"
        live_match.league_name = "Test Tournament"
        live_match.league_id = "12345"
        live_match.is_finished = False
        live_match.is_live = True
        live_match.is_scheduled = False
        live_match.home_player = MagicMock()
        live_match.home_player.name = "Player E"
        live_match.home_player.id = "player_e"
        live_match.away_player = MagicMock()
        live_match.away_player.name = "Player F"
        live_match.away_player.id = "player_f"
        live_match.event_datetime = datetime.now()
        
        # Configure mock to return different matches for different types
        def mock_side_effect(tournament_id, match_type, max_pages):
            if match_type == "ended":
                return [ended_match]
            elif match_type == "upcoming":
                return [upcoming_match]
            elif match_type == "live":
                return [live_match]
            return []
        
        mock_get_matches.side_effect = mock_side_effect
        
        # Test method call
        result = self.events_manager.get_tournament_complete(
            tournament_id="12345",
            include_odds=False
        )
        
        # Verify result type and basic structure
        assert isinstance(result, TournamentData)
        assert result.tournament_id == "12345"
        assert result.tournament_name == "Test Tournament"
        assert result.total_matches == 3
        assert result.completed_matches == 1
        assert result.live_matches == 1
        assert result.upcoming_matches == 1
        assert result.completion_rate == 1/3  # 1 completed out of 3 total
        assert not result.has_odds_data  # Odds not requested
        
        # Verify unique players extraction
        expected_players = ["Player A", "Player B", "Player C", "Player D", "Player E", "Player F"]
        assert len(result.unique_players) == 6
        for player in expected_players:
            assert player in result.unique_players
        
        # Verify helper method was called correctly for each match type
        assert mock_get_matches.call_count == 3
        mock_get_matches.assert_any_call("12345", "ended", 10)
        mock_get_matches.assert_any_call("12345", "upcoming", 10)
        mock_get_matches.assert_any_call("12345", "live", 10)
    
    @patch('tabletennis_api.managers.EventsManager._get_tournament_matches')
    def test_get_tournament_complete_with_odds(self, mock_get_matches):
        """Test get_tournament_complete with odds checking enabled"""
        
        # Mock tournament match
        match = MagicMock()
        match.id = "match_1"
        match.league_name = "Test Tournament"
        match.is_finished = True
        match.is_live = False
        match.is_scheduled = False
        match.home_player = MagicMock()
        match.home_player.name = "Player A"
        match.home_player.id = "player_a"
        match.away_player = MagicMock()
        match.away_player.name = "Player B"
        match.away_player.id = "player_b"
        match.event_datetime = datetime.now() - timedelta(days=1)
        
        mock_get_matches.return_value = [match]
        
        # Mock odds API to return odds data
        with patch.object(self.api, 'odds') as mock_odds:
            mock_odds.get_summary.return_value = {"Bet365": {"odds": "data"}}
        
            # Test method call with odds enabled
            result = self.events_manager.get_tournament_complete(
                tournament_id="12345",
                include_odds=True,
                max_pages_per_type=2
            )
            
            # Verify odds checking occurred
            assert result.has_odds_data == True
            mock_odds.get_summary.assert_called()
    
    @patch('tabletennis_api.managers.EventsManager._get_tournament_matches')
    def test_get_tournament_complete_no_matches(self, mock_get_matches):
        """Test get_tournament_complete when no matches are found"""
        
        # Mock empty results for all match types
        mock_get_matches.return_value = []
        
        # Test method call
        result = self.events_manager.get_tournament_complete("99999")
        
        # Verify empty result structure
        assert isinstance(result, TournamentData)
        assert result.tournament_id == "99999"
        assert result.tournament_name == "Tournament 99999"  # Fallback name
        assert result.total_matches == 0
        assert result.completed_matches == 0
        assert result.live_matches == 0
        assert result.upcoming_matches == 0
        assert result.completion_rate == 0.0
        assert len(result.unique_players) == 0
        assert not result.has_odds_data
    
    @patch('tabletennis_api.managers.EventsManager._get_tournament_matches')
    def test_get_tournament_complete_duplicate_removal(self, mock_get_matches):
        """Test get_tournament_complete removes duplicate matches across types"""
        
        # Create same match appearing in different types (should be deduplicated)
        duplicate_match = MagicMock()
        duplicate_match.id = "match_duplicate"
        duplicate_match.league_name = "Test Tournament"
        duplicate_match.is_finished = False
        duplicate_match.is_live = True
        duplicate_match.is_scheduled = False
        duplicate_match.home_player = MagicMock()
        duplicate_match.home_player.name = "Player A"
        duplicate_match.home_player.id = "player_a"
        duplicate_match.away_player = MagicMock()
        duplicate_match.away_player.name = "Player B"
        duplicate_match.away_player.id = "player_b"
        duplicate_match.event_datetime = datetime.now()
        
        unique_match = MagicMock()
        unique_match.id = "match_unique"
        unique_match.league_name = "Test Tournament"
        unique_match.is_finished = True
        unique_match.is_live = False
        unique_match.is_scheduled = False
        unique_match.home_player = MagicMock()
        unique_match.home_player.name = "Player C"
        unique_match.home_player.id = "player_c"
        unique_match.away_player = MagicMock()
        unique_match.away_player.name = "Player D"
        unique_match.away_player.id = "player_d"
        unique_match.event_datetime = datetime.now() - timedelta(days=1)
        
        # Configure mock to return duplicate match in multiple types
        def mock_side_effect(tournament_id, match_type, max_pages):
            if match_type == "ended":
                return [unique_match]
            elif match_type == "upcoming":
                return [duplicate_match]
            elif match_type == "live":
                return [duplicate_match]  # Same match in multiple types
            return []
        
        mock_get_matches.side_effect = mock_side_effect
        
        # Test method call
        result = self.events_manager.get_tournament_complete("12345")
        
        # Should only have 2 unique matches despite 3 being returned
        assert result.total_matches == 2
        
        # Verify the matches are correctly identified
        match_ids = [match.id for match in result.matches]
        assert "match_duplicate" in match_ids
        assert "match_unique" in match_ids
        assert len(set(match_ids)) == 2  # All unique
    
    @patch('tabletennis_api.managers.EventsManager._get_tournament_matches')
    def test_get_tournament_complete_exception_handling(self, mock_get_matches):
        """Test get_tournament_complete handles exceptions gracefully"""
        
        # Mock exception for ended matches, success for others
        def mock_side_effect(tournament_id, match_type, max_pages):
            if match_type == "ended":
                raise TableTennisAPIError("API Error")
            elif match_type == "upcoming":
                match = MagicMock()
                match.id = "match_1"
                match.league_name = "Test Tournament"
                match.is_finished = False
                match.is_live = False
                match.is_scheduled = True
                match.home_player = MagicMock()
                match.home_player.name = "Player A"
                match.away_player = MagicMock()
                match.away_player.name = "Player B"
                return [match]
            return []
        
        mock_get_matches.side_effect = mock_side_effect
        
        # Test method call - should not raise exception
        result = self.events_manager.get_tournament_complete("12345")
        
        # Should have results from successful calls only
        assert isinstance(result, TournamentData)
        assert result.total_matches == 1  # Only upcoming match
        assert result.completed_matches == 0  # Ended matches failed
        assert result.upcoming_matches == 1
    
    @responses.activate
    def test_get_tournament_matches_helper(self):
        """Test _get_tournament_matches helper method"""
        
        # Mock API response for ended events
        mock_response = {
            "success": 1,
            "results": [
                {
                    "id": "10001",
                    "sport_id": "92",
                    "time": "1722556800",
                    "time_status": "3",
                    "league": {"id": "12345", "name": "Test Tournament", "cc": "test"},
                    "home": {"id": "701", "name": "Player A", "cc": None},
                    "away": {"id": "702", "name": "Player B", "cc": None},
                    "ss": "3-1"
                },
                {
                    "id": "10002", 
                    "sport_id": "92",
                    "time": "1722556800",
                    "time_status": "3",
                    "league": {"id": "54321", "name": "Other Tournament", "cc": "test"},  # Different tournament
                    "home": {"id": "703", "name": "Player C", "cc": None},
                    "away": {"id": "704", "name": "Player D", "cc": None},
                    "ss": "3-0"
                },
                {
                    "id": "10003",
                    "sport_id": "92",
                    "time": "1722556800", 
                    "time_status": "3",
                    "league": {"id": "12345", "name": "Test Tournament", "cc": "test"},  # Same tournament
                    "home": {"id": "705", "name": "Player E", "cc": None},
                    "away": {"id": "706", "name": "Player F", "cc": None},
                    "ss": "3-2"
                }
            ],
            "pager": {"page": 1, "per_page": 50, "total": 3}
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v3/events/ended",
            json=mock_response,
            status=200
        )
        
        # Test helper method
        matches = self.events_manager._get_tournament_matches("12345", "ended", 5)
        
        # Should find 2 matches from tournament 12345 (filtering out 54321)
        assert len(matches) == 2
        
        # Verify correct matches were found
        match_ids = [match.id for match in matches]
        assert "10001" in match_ids  # From tournament 12345
        assert "10003" in match_ids  # From tournament 12345
        assert "10002" not in match_ids  # From different tournament 54321
    
    def test_tournament_data_model_properties(self):
        """Test TournamentData model properties and methods"""
        
        # Create mock matches with different statuses
        matches = []
        for i in range(10):
            match = MagicMock()
            match.id = f"match_{i}"
            match.league_name = "Test Tournament"
            match.home_player = MagicMock()
            match.home_player.id = f"player_{i*2}"
            match.home_player.name = f"Player {i*2}"
            match.away_player = MagicMock() 
            match.away_player.id = f"player_{i*2+1}"
            match.away_player.name = f"Player {i*2+1}"
            match.event_datetime = datetime.now() - timedelta(days=i)
            
            # Set status: first 6 finished, next 2 live, last 2 upcoming
            if i < 6:
                match.is_finished = True
                match.is_live = False
                match.is_scheduled = False
            elif i < 8:
                match.is_finished = False
                match.is_live = True
                match.is_scheduled = False
            else:
                match.is_finished = False
                match.is_live = False
                match.is_scheduled = True
                
            matches.append(match)
        
        # Create TournamentData object
        tournament = TournamentData.from_matches(
            tournament_id="12345",
            tournament_name="Test Tournament",
            matches=matches,
            has_odds_data=True
        )
        
        # Test basic properties
        assert tournament.tournament_id == "12345"
        assert tournament.tournament_name == "Test Tournament"
        assert tournament.total_matches == 10
        assert tournament.completed_matches == 6
        assert tournament.live_matches == 2
        assert tournament.upcoming_matches == 2
        assert tournament.has_odds_data == True
        
        # Test calculated properties
        assert tournament.completion_rate == 0.6  # 6/10 completed
        
        # Test unique players extraction
        unique_players = tournament.unique_players
        assert len(unique_players) == 20  # 10 matches * 2 players each, all unique
        assert "Player 0" in unique_players
        assert "Player 19" in unique_players
        
        # Test date range calculation
        assert tournament.date_range[0] is not None  # Start date
        assert tournament.date_range[1] is not None  # End date
        assert tournament.date_range[0] <= tournament.date_range[1]  # Proper ordering


class TestEventsBulkMethod:
    """Test cases for get_events_bulk method"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.api = TableTennisAPI(api_key="test-token")
        self.events_manager = self.api.events
    
    def test_get_events_bulk_validation(self):
        """Test input validation for get_events_bulk"""
        
        # Test empty event IDs
        with pytest.raises(ValueError, match="event_ids cannot be empty"):
            self.events_manager.get_events_bulk([])
        
        # Test too many event IDs
        with pytest.raises(ValueError, match="Cannot request more than 100 events at once"):
            self.events_manager.get_events_bulk([str(i) for i in range(101)])
    
    @patch('tabletennis_api.managers.EventsManager.get_ended')
    @patch('tabletennis_api.managers.EventsManager.get_upcoming')
    @patch('tabletennis_api.managers.EventsManager.get_inplay')
    def test_get_events_bulk_basic_success(self, mock_inplay, mock_upcoming, mock_ended):
        """Test successful get_events_bulk without additional data"""
        
        # Create mock events
        event1 = MagicMock()
        event1.id = "12345"
        event1.home_player = MagicMock()
        event1.home_player.name = "Player A"
        event1.away_player = MagicMock()
        event1.away_player.name = "Player B"
        
        event2 = MagicMock()
        event2.id = "12346"
        event2.home_player = MagicMock()
        event2.home_player.name = "Player C"
        event2.away_player = MagicMock()
        event2.away_player.name = "Player D"
        
        event3 = MagicMock()
        event3.id = "12347"
        event3.home_player = MagicMock()
        event3.home_player.name = "Player E"
        event3.away_player = MagicMock()
        event3.away_player.name = "Player F"
        
        # Mock responses
        ended_response = MagicMock()
        ended_response.results = [event1]
        ended_response.pager = MagicMock()
        ended_response.pager.page = 1
        ended_response.pager.total = 50
        ended_response.pager.per_page = 50
        
        upcoming_response = MagicMock()
        upcoming_response.results = [event2]
        upcoming_response.pager = MagicMock()
        upcoming_response.pager.page = 1
        upcoming_response.pager.total = 50
        upcoming_response.pager.per_page = 50
        
        inplay_response = MagicMock()
        inplay_response.results = [event3]
        inplay_response.pager = MagicMock()
        inplay_response.pager.page = 1
        inplay_response.pager.total = 10
        inplay_response.pager.per_page = 50
        
        mock_ended.return_value = ended_response
        mock_upcoming.return_value = upcoming_response
        mock_inplay.return_value = inplay_response
        
        # Test method call
        result = self.events_manager.get_events_bulk(
            event_ids=["12345", "12346", "12347"],
            include_odds=False,
            include_view=False
        )
        
        # Verify results
        assert isinstance(result, dict)
        assert len(result) == 3
        assert "12345" in result
        assert "12346" in result
        assert "12347" in result
        
        assert result["12345"].home_player.name == "Player A"
        assert result["12346"].home_player.name == "Player C"
        assert result["12347"].home_player.name == "Player E"
        
        # Verify API calls
        mock_ended.assert_called_with(page=1)
        mock_upcoming.assert_called_with(page=1)
        mock_inplay.assert_called_with(page=1)
    
    @patch('tabletennis_api.managers.EventsManager.get_ended')
    def test_get_events_bulk_all_in_one_type(self, mock_ended):
        """Test get_events_bulk when all events are in one type"""
        
        # Create mock events
        events = []
        for i in range(3):
            event = MagicMock()
            event.id = f"1234{i}"
            event.home_player = MagicMock()
            event.home_player.name = f"Player {i*2}"
            event.away_player = MagicMock()
            event.away_player.name = f"Player {i*2+1}"
            events.append(event)
        
        # Mock response
        ended_response = MagicMock()
        ended_response.results = events
        ended_response.pager = None  # No pager
        
        mock_ended.return_value = ended_response
        
        # Test method call
        result = self.events_manager.get_events_bulk(["12340", "12341", "12342"])
        
        # Should find all events and not check other types
        assert len(result) == 3
        assert all(id in result for id in ["12340", "12341", "12342"])
        
        # Should only call ended endpoint
        mock_ended.assert_called_once_with(page=1)
    
    @patch('tabletennis_api.managers.EventsManager.get_ended')
    @patch('tabletennis_api.managers.EventsManager.get_upcoming')
    @patch('tabletennis_api.managers.EventsManager.get_details')
    def test_get_events_bulk_with_view_data(self, mock_get_details, mock_upcoming, mock_ended):
        """Test get_events_bulk with view data enabled"""
        
        # Create mock event
        event = MagicMock()
        event.id = "12345"
        event.home_player = MagicMock()
        event.home_player.name = "Player A"
        event.away_player = MagicMock()
        event.away_player.name = "Player B"
        
        # Mock responses
        ended_response = MagicMock()
        ended_response.results = [event]
        ended_response.pager = None
        
        mock_ended.return_value = ended_response
        mock_upcoming.return_value = MagicMock(results=[])
        
        # Mock view data
        view_data = [{"additional": "data"}]  # get_details returns a list
        mock_get_details.return_value = view_data
        
        # Test method call with view enabled
        result = self.events_manager.get_events_bulk(
            event_ids=["12345"],
            include_view=True
        )
        
        # Verify view data was fetched
        assert len(result) == 1
        assert "12345" in result
        assert hasattr(result["12345"], "_view_data")
        assert result["12345"]._view_data == view_data
        
        mock_get_details.assert_called_once_with("12345")
    
    @patch('tabletennis_api.managers.EventsManager.get_ended')
    def test_get_events_bulk_with_odds_data(self, mock_ended):
        """Test get_events_bulk with odds data enabled"""
        
        # Create mock event
        event = MagicMock()
        event.id = "12345"
        event.home_player = MagicMock()
        event.home_player.name = "Player A"
        event.away_player = MagicMock()
        event.away_player.name = "Player B"
        
        # Mock responses
        ended_response = MagicMock()
        ended_response.results = [event]
        ended_response.pager = None
        
        mock_ended.return_value = ended_response
        
        # Mock odds manager
        with patch.object(self.api, 'odds') as mock_odds:
            odds_data = {"Bet365": {"home": 1.5, "away": 2.5}}
            mock_odds.get_summary.return_value = odds_data
            
            # Test method call with odds enabled
            result = self.events_manager.get_events_bulk(
                event_ids=["12345"],
                include_odds=True
            )
            
            # Verify odds data was fetched
            assert len(result) == 1
            assert "12345" in result
            assert hasattr(result["12345"], "_odds_data")
            assert result["12345"]._odds_data == odds_data
            
            mock_odds.get_summary.assert_called_once_with("12345")
    
    @patch('tabletennis_api.managers.EventsManager.get_ended')
    @patch('tabletennis_api.managers.EventsManager.get_upcoming')
    @patch('tabletennis_api.managers.EventsManager.get_inplay')
    def test_get_events_bulk_partial_results(self, mock_inplay, mock_upcoming, mock_ended):
        """Test get_events_bulk when some events are not found"""
        
        # Create only one mock event
        event = MagicMock()
        event.id = "12345"
        event.home_player = MagicMock()
        event.home_player.name = "Player A"
        event.away_player = MagicMock()
        event.away_player.name = "Player B"
        
        # Mock responses
        ended_response = MagicMock()
        ended_response.results = [event]
        ended_response.pager = None
        
        mock_ended.return_value = ended_response
        mock_upcoming.return_value = MagicMock(results=[])
        mock_inplay.return_value = MagicMock(results=[])
        
        # Test method call - requesting 3 events but only 1 exists
        result = self.events_manager.get_events_bulk(
            event_ids=["12345", "99999", "88888"]
        )
        
        # Should find only 1 event
        assert len(result) == 1
        assert "12345" in result
        assert "99999" not in result
        assert "88888" not in result
    
    @patch('tabletennis_api.managers.EventsManager.get_ended')
    def test_get_events_bulk_pagination(self, mock_ended):
        """Test get_events_bulk searches through multiple pages"""
        
        # Create events spread across pages
        page1_events = []
        for i in range(2):
            event = MagicMock()
            event.id = f"1234{i}"
            event.home_player = MagicMock()
            event.home_player.name = f"Player {i}"
            event.away_player = MagicMock()
            event.away_player.name = f"Player {i+1}"
            page1_events.append(event)
        
        page2_event = MagicMock()
        page2_event.id = "12342"
        page2_event.home_player = MagicMock()
        page2_event.home_player.name = "Player X"
        page2_event.away_player = MagicMock()
        page2_event.away_player.name = "Player Y"
        
        # Mock responses for different pages
        page1_response = MagicMock()
        page1_response.results = page1_events
        page1_response.pager = MagicMock()
        page1_response.pager.page = 1
        page1_response.pager.total = 100
        page1_response.pager.per_page = 50
        
        page2_response = MagicMock()
        page2_response.results = [page2_event]
        page2_response.pager = MagicMock()
        page2_response.pager.page = 2
        page2_response.pager.total = 100
        page2_response.pager.per_page = 50
        
        # Configure mock to return different pages
        mock_ended.side_effect = [page1_response, page2_response]
        
        # Test method call
        result = self.events_manager.get_events_bulk(["12340", "12341", "12342"])
        
        # Should find all 3 events across 2 pages
        assert len(result) == 3
        assert all(id in result for id in ["12340", "12341", "12342"])
        
        # Should have made 2 API calls for pagination
        assert mock_ended.call_count == 2
        mock_ended.assert_any_call(page=1)
        mock_ended.assert_any_call(page=2)
    
    @patch('tabletennis_api.managers.EventsManager.get_ended')
    def test_get_events_bulk_exception_handling(self, mock_ended):
        """Test get_events_bulk handles exceptions gracefully"""
        
        # Mock exception
        mock_ended.side_effect = Exception("API Error")
        
        # Test method call - should not raise exception
        result = self.events_manager.get_events_bulk(["12345"])
        
        # Should return empty results when search fails
        assert isinstance(result, dict)
        assert len(result) == 0
    
    def test_get_events_bulk_mixed_id_types(self):
        """Test get_events_bulk handles mixed integer and string IDs"""
        
        with patch('tabletennis_api.managers.EventsManager.get_ended') as mock_ended:
            # Create mock event
            event = MagicMock()
            event.id = "12345"
            
            ended_response = MagicMock()
            ended_response.results = [event]
            ended_response.pager = None
            
            mock_ended.return_value = ended_response
            
            # Test with mixed ID types
            result = self.events_manager.get_events_bulk(
                event_ids=[12345, "12345", 12346]  # Mix of int and str
            )
            
            # Should convert all to strings internally
            assert "12345" in result