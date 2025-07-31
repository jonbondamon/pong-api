"""
Unit tests for PlayerManager class
"""

import pytest
import responses
from tabletennis_api.managers import PlayerManager
from tabletennis_api.models import Player, PaginationInfo, APIResponse
from tabletennis_api.client import TableTennisAPI
from tabletennis_api.exceptions import TableTennisAPIError


class TestPlayerManager:
    """Test cases for PlayerManager class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.api = TableTennisAPI(api_key="test-token")
        self.player_manager = self.api.players
    
    @responses.activate
    def test_list_success(self):
        """Test successful list request"""
        # Mock API response
        mock_response = {
            "success": 1,
            "pager": {
                "page": 1,
                "per_page": 100,
                "total": 21094
            },
            "results": [
                {
                    "id": "1168738",
                    "name": "Jiri Karlik",
                    "cc": None,
                    "image_id": None
                },
                {
                    "id": "1166996",
                    "name": "Fuentes/Orencel",
                    "cc": "ar",
                    "image_id": "1264549"
                },
                {
                    "id": "1164532",
                    "name": "Takeshi Yamamoto",
                    "cc": "jp",
                    "image_id": "1256783"
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response,
            status=200
        )
        
        # Execute test
        result = self.player_manager.list()
        
        # Assertions
        assert isinstance(result, APIResponse)
        assert len(result.results) == 3
        assert result.pagination.total == 21094
        assert result.pagination.page == 1
        assert result.pagination.per_page == 100
        
        # Check first player (individual)
        player1 = result.results[0]
        assert isinstance(player1, Player)
        assert player1.id == "1168738"
        assert player1.name == "Jiri Karlik"
        assert player1.country_code is None
        assert player1.image_id is None
        assert not player1.is_doubles_pair
        assert not player1.has_image
        assert player1.player_names == ["Jiri Karlik"]
        
        # Check second player (doubles pair with image)
        player2 = result.results[1]
        assert player2.id == "1166996"
        assert player2.name == "Fuentes/Orencel"
        assert player2.country_code == "ar"
        assert player2.image_id == "1264549"
        assert player2.is_doubles_pair
        assert player2.has_image
        assert player2.player_names == ["Fuentes", "Orencel"]
        
        # Check third player (individual with image)
        player3 = result.results[2]
        assert player3.id == "1164532"
        assert player3.name == "Takeshi Yamamoto"
        assert player3.country_code == "jp"
        assert not player3.is_doubles_pair
        assert player3.has_image
    
    @responses.activate
    def test_list_with_country_filter(self):
        """Test list with country code filter"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 100, "total": 150},
            "results": [
                {
                    "id": "1001",
                    "name": "Jan Novak",
                    "cc": "cz",
                    "image_id": "12345"
                },
                {
                    "id": "1002",
                    "name": "Petr Svoboda",
                    "cc": "cz",
                    "image_id": None
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response,
            status=200
        )
        
        # Execute test with country filter
        result = self.player_manager.list(country_code="cz")
        
        # Verify request parameters
        assert len(responses.calls) == 1
        request_params = responses.calls[0].request.url
        assert "cc=cz" in request_params
        
        # Verify response
        assert len(result.results) == 2
        for player in result.results:
            assert player.country_code == "cz"
    
    @responses.activate
    def test_list_with_pagination(self):
        """Test list with pagination"""
        mock_response = {
            "success": 1,
            "pager": {"page": 3, "per_page": 100, "total": 21094},
            "results": [
                {
                    "id": "3001",
                    "name": "Test Player",
                    "cc": None,
                    "image_id": None
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response,
            status=200
        )
        
        result = self.player_manager.list(page=3)
        
        # Verify request parameters
        request_params = responses.calls[0].request.url
        assert "page=3" in request_params
        
        # Verify pagination
        assert result.pagination.page == 3
        assert result.pagination.per_page == 100
        assert result.pagination.total == 21094
        assert result.pagination.total_pages == 211
        assert result.pagination.has_previous_page
        assert result.pagination.has_next_page
    
    def test_list_invalid_page(self):
        """Test list with invalid page number"""
        with pytest.raises(ValueError, match="Page number must be >= 1"):
            self.player_manager.list(page=0)
        
        with pytest.raises(ValueError, match="Page number must be >= 1"):
            self.player_manager.list(page=-1)
    
    @responses.activate
    def test_list_api_error(self):
        """Test list handles API errors"""
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json={"success": 0, "error": "Invalid token"},
            status=401
        )
        
        with pytest.raises(TableTennisAPIError):
            self.player_manager.list()
    
    @responses.activate
    def test_list_empty_results(self):
        """Test list with empty results"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 100, "total": 0},
            "results": []
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response,
            status=200
        )
        
        result = self.player_manager.list()
        
        assert len(result.results) == 0
        assert result.pagination.total == 0
        assert result.pagination.total_pages == 0
    
    @responses.activate
    def test_search_success(self):
        """Test successful search functionality"""
        # Mock response for page 1
        mock_response_1 = {
            "success": 1,
            "pager": {"page": 1, "per_page": 100, "total": 300},
            "results": [
                {"id": "1", "name": "Jan Novak", "cc": "cz", "image_id": None},
                {"id": "2", "name": "John Smith", "cc": "us", "image_id": "123"},
                {"id": "3", "name": "Jane Doe", "cc": "gb", "image_id": None},
                {"id": "4", "name": "Johannes Mueller", "cc": "de", "image_id": "456"}
            ]
        }
        
        # Mock response for page 2 (in case search continues)
        mock_response_2 = {
            "success": 1,
            "pager": {"page": 2, "per_page": 100, "total": 300},
            "results": [
                {"id": "101", "name": "Janet Wilson", "cc": "ca", "image_id": None},
                {"id": "102", "name": "Janusz Kowalski", "cc": "pl", "image_id": "789"}
            ]
        }
        
        # Add responses for both pages
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response_1,
            status=200
        )
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response_2,
            status=200
        )
        
        # Execute search for "Jan"
        results = self.player_manager.search("Jan", limit=5)
        
        # Should find players with "Jan" in name (case insensitive)
        assert len(results) >= 4  # At minimum should find 4 matches from first page
        for player in results:
            assert "jan" in player.name.lower()
        
        # Check that we get some expected matches
        player_names = [p.name for p in results]
        assert "Jan Novak" in player_names
        # Johannes doesn't contain "Jan" as separate case-insensitive match - search looks for exact substring
        # So let's verify that the search found the correct matches
        expected_matches = {"Jan Novak", "Jane Doe", "Janet Wilson", "Janusz Kowalski"}
        actual_matches = set(player_names)
        assert len(expected_matches.intersection(actual_matches)) >= 2
    
    @responses.activate
    def test_search_with_country_filter(self):
        """Test search with country filter"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 100, "total": 50},
            "results": [
                {"id": "1", "name": "Jan Novak", "cc": "cz", "image_id": None},
                {"id": "2", "name": "Jana Svoboda", "cc": "cz", "image_id": "123"}
            ]
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response,
            status=200
        )
        
        results = self.player_manager.search("Jan", country_code="cz", limit=10)
        
        # Verify request includes country filter
        request_params = responses.calls[0].request.url
        assert "cc=cz" in request_params
        
        # All results should be from Czech Republic
        assert len(results) == 2
        for player in results:
            assert player.country_code == "cz"
            assert "jan" in player.name.lower()
    
    @responses.activate
    def test_search_limited_results(self):
        """Test search with limited results"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 100, "total": 100},
            "results": [
                {"id": "1", "name": "Jan A", "cc": None, "image_id": None},
                {"id": "2", "name": "Jan B", "cc": None, "image_id": None},
                {"id": "3", "name": "Other Player", "cc": None, "image_id": None}
            ]
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response,
            status=200
        )
        
        results = self.player_manager.search("Jan", limit=1)
        
        # Should only return 1 result even though 2 match
        assert len(results) == 1
        assert "jan" in results[0].name.lower()
    
    @responses.activate
    def test_get_singles_players(self):
        """Test get_singles_players method"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 100, "total": 100},
            "results": [
                {"id": "1", "name": "Individual Player", "cc": None, "image_id": None},
                {"id": "2", "name": "Player1/Player2", "cc": None, "image_id": None},
                {"id": "3", "name": "Another Single", "cc": "us", "image_id": "123"},
                {"id": "4", "name": "Double/Pair", "cc": "gb", "image_id": None}
            ]
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response,
            status=200
        )
        
        result = self.player_manager.get_singles_players()
        
        # Should only return players without "/" in name
        assert len(result.results) == 2
        for player in result.results:
            assert not player.is_doubles_pair
            assert "/" not in player.name
        
        # Check specific players
        singles_names = [p.name for p in result.results]
        assert "Individual Player" in singles_names
        assert "Another Single" in singles_names
    
    @responses.activate
    def test_get_doubles_pairs(self):
        """Test get_doubles_pairs method"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 100, "total": 100},
            "results": [
                {"id": "1", "name": "Individual Player", "cc": None, "image_id": None},
                {"id": "2", "name": "Player1/Player2", "cc": None, "image_id": None},
                {"id": "3", "name": "Another Single", "cc": "us", "image_id": "123"},
                {"id": "4", "name": "Double/Pair", "cc": "gb", "image_id": None}
            ]
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response,
            status=200
        )
        
        result = self.player_manager.get_doubles_pairs()
        
        # Should only return players with "/" in name
        assert len(result.results) == 2
        for player in result.results:
            assert player.is_doubles_pair
            assert "/" in player.name
        
        # Check specific pairs
        doubles_names = [p.name for p in result.results]
        assert "Player1/Player2" in doubles_names
        assert "Double/Pair" in doubles_names
        
        # Check player names parsing
        for player in result.results:
            assert len(player.player_names) == 2
    
    @responses.activate
    def test_get_players_with_images(self):
        """Test get_players_with_images method"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 100, "total": 100},
            "results": [
                {"id": "1", "name": "Player No Image", "cc": None, "image_id": None},
                {"id": "2", "name": "Player With Image", "cc": None, "image_id": "12345"},
                {"id": "3", "name": "Another No Image", "cc": "us", "image_id": 0},
                {"id": "4", "name": "Has Image Too", "cc": "gb", "image_id": "67890"}
            ]
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response,
            status=200
        )
        
        result = self.player_manager.get_players_with_images()
        
        # Should only return players with image_id not None 
        # (Player model now converts 0 to None in from_dict)
        assert len(result.results) == 2
        for player in result.results:
            assert player.has_image
            assert player.image_id is not None
        
        # Check specific players
        image_players = [p.name for p in result.results]
        assert "Player With Image" in image_players
        assert "Has Image Too" in image_players
    
    @responses.activate
    def test_get_singles_players_with_country_filter(self):
        """Test get_singles_players with country filter"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 100, "total": 50},
            "results": [
                {"id": "1", "name": "Czech Single", "cc": "cz", "image_id": None},
                {"id": "2", "name": "Czech1/Czech2", "cc": "cz", "image_id": None},
                {"id": "3", "name": "Another Czech", "cc": "cz", "image_id": "123"}
            ]
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response,
            status=200
        )
        
        result = self.player_manager.get_singles_players(country_code="cz")
        
        # Verify request includes country filter
        request_params = responses.calls[0].request.url
        assert "cc=cz" in request_params
        
        # Should only return singles players from Czech Republic
        assert len(result.results) == 2
        for player in result.results:
            assert not player.is_doubles_pair
            assert player.country_code == "cz"
        
        singles_names = [p.name for p in result.results]
        assert "Czech Single" in singles_names
        assert "Another Czech" in singles_names


class TestPlayerModel:
    """Test cases for Player model"""
    
    def test_player_from_dict_basic(self):
        """Test Player creation from basic dictionary"""
        data = {
            "id": "1168738",
            "name": "Jiri Karlik",
            "cc": None,
            "image_id": None
        }
        
        player = Player.from_dict(data)
        
        assert player.id == "1168738"
        assert player.name == "Jiri Karlik"
        assert player.country_code is None
        assert player.image_id is None
    
    def test_player_from_dict_complete(self):
        """Test Player creation from complete dictionary"""
        data = {
            "id": "1166996",
            "name": "Fuentes/Orencel",
            "cc": "ar",
            "image_id": "1264549"
        }
        
        player = Player.from_dict(data)
        
        assert player.id == "1166996"
        assert player.name == "Fuentes/Orencel"
        assert player.country_code == "ar"
        assert player.image_id == "1264549"
    
    def test_player_is_doubles_pair(self):
        """Test is_doubles_pair property"""
        # Individual player
        single_player = Player(id="1", name="John Doe")
        assert not single_player.is_doubles_pair
        
        # Doubles pair
        doubles_player = Player(id="2", name="Player1/Player2")
        assert doubles_player.is_doubles_pair
    
    def test_player_has_image(self):
        """Test has_image property"""
        # No image
        no_image = Player(id="1", name="Test", image_id=None)
        assert not no_image.has_image
        
        # Has image
        with_image = Player(id="2", name="Test", image_id="12345")
        assert with_image.has_image
    
    def test_player_names_property(self):
        """Test player_names property"""
        # Individual player
        single = Player(id="1", name="John Doe")
        assert single.player_names == ["John Doe"]
        
        # Doubles pair
        doubles = Player(id="2", name="Player One/Player Two")
        assert doubles.player_names == ["Player One", "Player Two"]
        
        # Complex doubles name
        complex_doubles = Player(id="3", name="José María García / Ana Isabel Ruiz")
        assert complex_doubles.player_names == ["José María García", "Ana Isabel Ruiz"]
    
    def test_player_display_name(self):
        """Test display_name property"""
        player = Player(id="1", name="Test Player")
        assert player.display_name == "Test Player"
    
    def test_player_image_id_zero_handling(self):
        """Test that image_id of 0 is treated as None"""
        # This tests the from_dict method handling of image_id: 0
        data = {
            "id": "123",
            "name": "Test Player",
            "cc": None,
            "image_id": 0  # Should be converted to None
        }
        
        player = Player.from_dict(data)
        assert player.image_id is None
        assert not player.has_image


class TestPlayerManagerIntegration:
    """Integration tests for PlayerManager"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.api = TableTennisAPI(api_key="test-token")
        self.player_manager = self.api.players
    
    @responses.activate
    def test_list_all_method_single_page(self):
        """Test list_all with single page result"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 100, "total": 50},
            "results": [
                {"id": "1", "name": "Player 1", "cc": None, "image_id": None},
                {"id": "2", "name": "Player 2", "cc": None, "image_id": None}
            ]
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response,
            status=200
        )
        
        result = self.player_manager.list_all()
        
        # Should make only one API call
        assert len(responses.calls) == 1
        assert len(result) == 2
        assert all(isinstance(p, Player) for p in result)
    
    @responses.activate
    def test_search_no_matches(self):
        """Test search when no matches found"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 100, "total": 100},
            "results": [
                {"id": "1", "name": "Player A", "cc": None, "image_id": None},
                {"id": "2", "name": "Player B", "cc": None, "image_id": None}
            ]
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response,
            status=200
        )
        
        results = self.player_manager.search("XYZ", limit=5)
        
        # Should return empty list when no matches
        assert len(results) == 0
    
    @responses.activate 
    def test_search_error_handling(self):
        """Test search handles API errors gracefully"""
        # First page succeeds
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json={
                "success": 1,
                "pager": {"page": 1, "per_page": 100, "total": 200},
                "results": [
                    {"id": "1", "name": "Jan Test", "cc": None, "image_id": None}
                ]
            },
            status=200
        )
        
        # Second page fails
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json={"success": 0, "error": "Rate limit"},
            status=429
        )
        
        results = self.player_manager.search("Jan", limit=5)
        
        # Should return results from successful page, stop on error
        assert len(results) == 1
        assert results[0].name == "Jan Test"
    
    @responses.activate
    def test_mixed_content_filtering(self):
        """Test that filtering methods work correctly with mixed content"""
        mock_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 100, "total": 100},
            "results": [
                {"id": "1", "name": "Single Player", "cc": "us", "image_id": "123"},
                {"id": "2", "name": "Double/Pair", "cc": "gb", "image_id": None},
                {"id": "3", "name": "Another Single", "cc": "cz", "image_id": None},
                {"id": "4", "name": "Pair/Two", "cc": "de", "image_id": "456"}
            ]
        }
        
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response,
            status=200
        )
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response,
            status=200
        )
        responses.add(
            responses.GET,
            "https://api.b365api.com/v2/team",
            json=mock_response,
            status=200
        )
        
        # Test all filtering methods
        singles = self.player_manager.get_singles_players()
        doubles = self.player_manager.get_doubles_pairs()
        with_images = self.player_manager.get_players_with_images()
        
        # Verify filtering results
        assert len(singles.results) == 2
        assert len(doubles.results) == 2
        assert len(with_images.results) == 2
        
        # Verify content
        singles_names = [p.name for p in singles.results]
        doubles_names = [p.name for p in doubles.results]
        image_names = [p.name for p in with_images.results]
        
        assert "Single Player" in singles_names
        assert "Another Single" in singles_names
        assert "Double/Pair" in doubles_names
        assert "Pair/Two" in doubles_names
        assert "Single Player" in image_names
        assert "Pair/Two" in image_names