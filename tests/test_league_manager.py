"""
Unit tests for LeagueManager functionality.
Tests the league-related endpoints with mocked API responses.
"""

from datetime import datetime

import pytest
import responses

from tabletennis_api import TableTennisAPI, TableTennisAPIError
from tabletennis_api.models import APIResponse, League, PaginationInfo


class TestLeagueManager:
    """Test cases for LeagueManager"""

    @pytest.fixture
    def api_client(self):
        """Create API client instance for testing"""
        return TableTennisAPI(api_key="test-token")

    @pytest.fixture
    def mock_league_response(self):
        """Sample league API response data"""
        return {
            "success": 1,
            "pager": {"page": 1, "per_page": 100, "total": 1111},
            "results": [
                {
                    "id": "41155",
                    "name": "WTT Star Contender Foz do Iguacu MD Quals",
                    "cc": None,
                    "has_leaguetable": 1,
                    "has_toplist": 0,
                },
                {
                    "id": "39354",
                    "name": "Czechia Liga Pro",
                    "cc": "cz",
                    "has_leaguetable": 0,
                    "has_toplist": 1,
                },
                {
                    "id": "38414",
                    "name": "Czech Liga Pro (2023)",
                    "cc": "cz",
                    "has_leaguetable": 1,
                    "has_toplist": 0,
                },
            ],
        }

    @pytest.fixture
    def mock_empty_response(self):
        """Empty API response for edge case testing"""
        return {
            "success": 1,
            "pager": {"page": 1, "per_page": 100, "total": 0},
            "results": [],
        }

    @responses.activate
    def test_list_leagues_success(self, api_client, mock_league_response):
        """Test successful league listing"""
        # Mock the API response
        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/league",
            json=mock_league_response,
            status=200,
            headers={
                "X-Ratelimit-Limit": "3600",
                "X-Ratelimit-Remaining": "3599",
                "X-Ratelimit-Reset": "1753815600",
            },
        )

        # Call the method
        response = api_client.leagues.list()

        # Verify the response structure
        assert isinstance(response, APIResponse)
        assert len(response.results) == 3
        assert response.count == 3

        # Verify pagination info
        assert response.pagination is not None
        assert response.pagination.page == 1
        assert response.pagination.per_page == 100
        assert response.pagination.total == 1111
        assert response.pagination.total_pages == 12
        assert response.pagination.has_next_page is True
        assert response.pagination.has_previous_page is False

        # Verify league objects
        first_league = response.results[0]
        assert isinstance(first_league, League)
        assert first_league.id == "41155"
        assert first_league.name == "WTT Star Contender Foz do Iguacu MD Quals"
        assert first_league.country_code is None
        assert first_league.supports_standings is True
        assert first_league.supports_rankings is False

        # Verify Czech league
        czech_league = response.results[1]
        assert czech_league.country_code == "cz"
        assert czech_league.supports_rankings is True

        # Verify API call was made correctly
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert "token=test-token" in request.url
        assert "sport_id=92" in request.url
        assert "page=1" in request.url

    @responses.activate
    def test_list_leagues_with_country_filter(self, api_client, mock_league_response):
        """Test league listing with country code filter"""
        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/league",
            json=mock_league_response,
            status=200,
        )

        response = api_client.leagues.list(country_code="CZ")

        # Verify the API call included country filter
        request = responses.calls[0].request
        assert "cc=cz" in request.url  # Should be lowercase

    @responses.activate
    def test_list_leagues_with_pagination(self, api_client, mock_league_response):
        """Test league listing with specific page"""
        # Modify response for page 2
        page2_response = mock_league_response.copy()
        page2_response["pager"]["page"] = 2

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/league",
            json=page2_response,
            status=200,
        )

        response = api_client.leagues.list(page=2)

        # Verify pagination
        assert response.pagination.page == 2
        assert response.pagination.has_previous_page is True
        assert response.pagination.has_next_page is True

        # Verify API call
        request = responses.calls[0].request
        assert "page=2" in request.url

    @responses.activate
    def test_list_leagues_empty_response(self, api_client, mock_empty_response):
        """Test handling of empty league response"""
        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/league",
            json=mock_empty_response,
            status=200,
        )

        response = api_client.leagues.list()

        assert len(response.results) == 0
        assert response.count == 0
        assert response.pagination.total == 0
        assert response.pagination.total_pages == 0

    def test_list_leagues_invalid_page(self, api_client):
        """Test error handling for invalid page number"""
        with pytest.raises(ValueError, match="Page number must be >= 1"):
            api_client.leagues.list(page=0)

        with pytest.raises(ValueError, match="Page number must be >= 1"):
            api_client.leagues.list(page=-1)

    @responses.activate
    def test_list_leagues_api_error(self, api_client):
        """Test handling of API errors"""
        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/league",
            json={"success": 0, "error": "Invalid token"},
            status=200,
        )

        with pytest.raises(TableTennisAPIError, match="API error: Invalid token"):
            api_client.leagues.list()

    @responses.activate
    def test_list_leagues_http_error(self, api_client):
        """Test handling of HTTP errors"""
        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/league",
            json={"error": "Unauthorized"},
            status=401,
        )

        with pytest.raises(TableTennisAPIError, match="Invalid API token"):
            api_client.leagues.list()

    @responses.activate
    def test_list_all_leagues_single_page(self, api_client):
        """Test list_all with single page of results"""
        single_page_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 100, "total": 50},
            "results": [
                {
                    "id": "1",
                    "name": "League 1",
                    "cc": None,
                    "has_leaguetable": 1,
                    "has_toplist": 0,
                }
                for _ in range(50)
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/league",
            json=single_page_response,
            status=200,
        )

        all_leagues = api_client.leagues.list_all()

        assert len(all_leagues) == 50
        assert len(responses.calls) == 1  # Only one API call needed

    @responses.activate
    def test_list_all_leagues_multiple_pages(self, api_client):
        """Test list_all with multiple pages"""
        # Page 1 response
        page1_response = {
            "success": 1,
            "pager": {"page": 1, "per_page": 2, "total": 5},
            "results": [
                {
                    "id": "1",
                    "name": "League 1",
                    "cc": None,
                    "has_leaguetable": 1,
                    "has_toplist": 0,
                },
                {
                    "id": "2",
                    "name": "League 2",
                    "cc": None,
                    "has_leaguetable": 1,
                    "has_toplist": 0,
                },
            ],
        }

        # Page 2 response
        page2_response = {
            "success": 1,
            "pager": {"page": 2, "per_page": 2, "total": 5},
            "results": [
                {
                    "id": "3",
                    "name": "League 3",
                    "cc": None,
                    "has_leaguetable": 1,
                    "has_toplist": 0,
                },
                {
                    "id": "4",
                    "name": "League 4",
                    "cc": None,
                    "has_leaguetable": 1,
                    "has_toplist": 0,
                },
            ],
        }

        # Page 3 response (final page)
        page3_response = {
            "success": 1,
            "pager": {"page": 3, "per_page": 2, "total": 5},
            "results": [
                {
                    "id": "5",
                    "name": "League 5",
                    "cc": None,
                    "has_leaguetable": 1,
                    "has_toplist": 0,
                }
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/league",
            json=page1_response,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/league",
            json=page2_response,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/league",
            json=page3_response,
            status=200,
        )

        all_leagues = api_client.leagues.list_all()

        assert len(all_leagues) == 5
        assert len(responses.calls) == 3  # Three API calls for three pages
        assert all_leagues[0].id == "1"
        assert all_leagues[4].id == "5"

    @responses.activate
    def test_rate_limit_tracking(self, api_client, mock_league_response):
        """Test that rate limit information is properly tracked"""
        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/league",
            json=mock_league_response,
            status=200,
            headers={
                "X-Ratelimit-Limit": "3600",
                "X-Ratelimit-Remaining": "3595",
                "X-Ratelimit-Reset": "1753815600",
            },
        )

        api_client.leagues.list()

        # Verify rate limit info was updated
        assert api_client.rate_limit == 3600
        assert api_client.rate_limit_remaining == 3595
        assert api_client.rate_limit_reset == datetime.fromtimestamp(1753815600)

        # Test rate limit info property
        rate_info = api_client.rate_limit_info
        assert rate_info["limit"] == 3600
        assert rate_info["remaining"] == 3595

        # Test rate limit warning
        assert api_client.is_rate_limited() is False  # 3595 > 10

    @responses.activate
    def test_get_table_method(self, api_client):
        """Test get_table method"""
        table_response = {
            "success": 1,
            "results": [
                {"team": "Team 1", "points": 10},
                {"team": "Team 2", "points": 8},
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/league/table",
            json=table_response,
            status=200,
        )

        result = api_client.leagues.get_table("12345")

        assert len(result) == 2
        assert result[0]["team"] == "Team 1"

        # Verify API call
        request = responses.calls[0].request
        assert "league_id=12345" in request.url

    @responses.activate
    def test_get_rankings_method(self, api_client):
        """Test get_rankings method"""
        rankings_response = {
            "success": 1,
            "results": [
                {"player": "Player 1", "ranking": 1},
                {"player": "Player 2", "ranking": 2},
            ],
        }

        responses.add(
            responses.GET,
            "https://api.b365api.com/v1/league/toplist",
            json=rankings_response,
            status=200,
        )

        result = api_client.leagues.get_rankings(67890)

        assert len(result) == 2
        assert result[0]["player"] == "Player 1"

        # Verify API call
        request = responses.calls[0].request
        assert "league_id=67890" in request.url
