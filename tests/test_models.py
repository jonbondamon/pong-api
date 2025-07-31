"""
Unit tests for data models.
Tests the League, PaginationInfo, and APIResponse models.
"""

import pytest

from tabletennis_api.models import APIResponse, League, PaginationInfo


class TestLeague:
    """Test cases for League model"""

    def test_league_from_dict_full_data(self):
        """Test creating League from complete dictionary"""
        data = {
            "id": "41155",
            "name": "WTT Star Contender Foz do Iguacu MD Quals",
            "cc": "br",
            "has_leaguetable": 1,
            "has_toplist": 0,
        }

        league = League.from_dict(data)

        assert league.id == "41155"
        assert league.name == "WTT Star Contender Foz do Iguacu MD Quals"
        assert league.country_code == "br"
        assert league.has_leaguetable is True
        assert league.has_toplist is False
        assert league.supports_standings is True
        assert league.supports_rankings is False

    def test_league_from_dict_null_country(self):
        """Test creating League with null country code"""
        data = {
            "id": "12345",
            "name": "International Tournament",
            "cc": None,
            "has_leaguetable": 0,
            "has_toplist": 1,
        }

        league = League.from_dict(data)

        assert league.country_code is None
        assert league.supports_standings is False
        assert league.supports_rankings is True

    def test_league_from_dict_missing_optional_fields(self):
        """Test creating League with missing optional fields"""
        data = {"id": "67890", "name": "Basic League"}

        league = League.from_dict(data)

        assert league.id == "67890"
        assert league.name == "Basic League"
        assert league.country_code is None
        assert league.has_leaguetable is False
        assert league.has_toplist is False

    def test_league_boolean_conversion(self):
        """Test that integer flags are properly converted to booleans"""
        data = {
            "id": "test",
            "name": "Test League",
            "has_leaguetable": 1,
            "has_toplist": 0,
        }

        league = League.from_dict(data)

        assert isinstance(league.has_leaguetable, bool)
        assert isinstance(league.has_toplist, bool)
        assert league.has_leaguetable is True
        assert league.has_toplist is False

    def test_league_properties(self):
        """Test League convenience properties"""
        league = League(
            id="test", name="Test League", has_leaguetable=True, has_toplist=False
        )

        assert league.supports_standings is True
        assert league.supports_rankings is False

        # Test opposite case
        league2 = League(
            id="test2", name="Test League 2", has_leaguetable=False, has_toplist=True
        )

        assert league2.supports_standings is False
        assert league2.supports_rankings is True


class TestPaginationInfo:
    """Test cases for PaginationInfo model"""

    def test_pagination_from_dict(self):
        """Test creating PaginationInfo from dictionary"""
        data = {"page": 2, "per_page": 100, "total": 1111}

        pagination = PaginationInfo.from_dict(data)

        assert pagination.page == 2
        assert pagination.per_page == 100
        assert pagination.total == 1111

    def test_pagination_total_pages_calculation(self):
        """Test total_pages property calculation"""
        # Exact division
        pagination = PaginationInfo(page=1, per_page=100, total=500)
        assert pagination.total_pages == 5

        # With remainder
        pagination = PaginationInfo(page=1, per_page=100, total=550)
        assert pagination.total_pages == 6

        # Single page
        pagination = PaginationInfo(page=1, per_page=100, total=50)
        assert pagination.total_pages == 1

        # Empty results
        pagination = PaginationInfo(page=1, per_page=100, total=0)
        assert pagination.total_pages == 0

    def test_pagination_has_next_page(self):
        """Test has_next_page property"""
        # Has next page
        pagination = PaginationInfo(page=2, per_page=100, total=500)
        assert pagination.has_next_page is True

        # Last page
        pagination = PaginationInfo(page=5, per_page=100, total=500)
        assert pagination.has_next_page is False

        # Single page
        pagination = PaginationInfo(page=1, per_page=100, total=50)
        assert pagination.has_next_page is False

    def test_pagination_has_previous_page(self):
        """Test has_previous_page property"""
        # First page
        pagination = PaginationInfo(page=1, per_page=100, total=500)
        assert pagination.has_previous_page is False

        # Middle page
        pagination = PaginationInfo(page=3, per_page=100, total=500)
        assert pagination.has_previous_page is True

        # Last page
        pagination = PaginationInfo(page=5, per_page=100, total=500)
        assert pagination.has_previous_page is True


class TestAPIResponse:
    """Test cases for APIResponse model"""

    def test_api_response_with_pagination(self):
        """Test APIResponse with pagination info"""
        leagues = [League(id="1", name="League 1"), League(id="2", name="League 2")]
        pagination = PaginationInfo(page=1, per_page=100, total=200)

        response = APIResponse(results=leagues, pagination=pagination)

        assert len(response.results) == 2
        assert response.count == 2
        assert response.pagination.total == 200

    def test_api_response_without_pagination(self):
        """Test APIResponse without pagination info"""
        leagues = [League(id="1", name="League 1")]

        response = APIResponse(results=leagues)

        assert len(response.results) == 1
        assert response.count == 1
        assert response.pagination is None

    def test_api_response_empty_results(self):
        """Test APIResponse with empty results"""
        response = APIResponse(results=[])

        assert len(response.results) == 0
        assert response.count == 0

    def test_api_response_count_property(self):
        """Test that count property reflects actual results length"""
        leagues = [League(id=str(i), name=f"League {i}") for i in range(5)]
        response = APIResponse(results=leagues)

        assert response.count == 5

        # Test with empty list
        empty_response = APIResponse(results=[])
        assert empty_response.count == 0


class TestModelIntegration:
    """Integration tests for models working together"""

    def test_full_api_response_simulation(self):
        """Test complete API response parsing simulation"""
        # Simulate raw API response data
        api_data = {
            "success": 1,
            "pager": {"page": 2, "per_page": 100, "total": 1111},
            "results": [
                {
                    "id": "41155",
                    "name": "WTT Star Contender",
                    "cc": "br",
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
            ],
        }

        # Parse the response (simulate what LeagueManager does)
        pagination = PaginationInfo.from_dict(api_data["pager"])
        leagues = [League.from_dict(league_data) for league_data in api_data["results"]]
        response = APIResponse(results=leagues, pagination=pagination)

        # Verify the complete response
        assert response.count == 2
        assert response.pagination.page == 2
        assert response.pagination.total == 1111
        assert response.pagination.has_previous_page is True
        assert response.pagination.has_next_page is True

        # Verify individual leagues
        wtt_league = response.results[0]
        assert wtt_league.name == "WTT Star Contender"
        assert wtt_league.country_code == "br"
        assert wtt_league.supports_standings is True

        czech_league = response.results[1]
        assert czech_league.name == "Czechia Liga Pro"
        assert czech_league.country_code == "cz"
        assert czech_league.supports_rankings is True
