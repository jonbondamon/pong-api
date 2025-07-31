"""
Unit tests for TableTennisAPI client initialization and core functionality.
"""

from datetime import datetime

import pytest

from tabletennis_api import TableTennisAPI, TableTennisAPIError
from tabletennis_api.managers import (EventsManager, LeagueManager,
                                      OddsManager, PlayerManager)


class TestTableTennisAPI:
    """Test cases for TableTennisAPI client"""

    def test_client_initialization_with_token(self):
        """Test successful client initialization with API token"""
        api = TableTennisAPI(api_key="test-token")

        assert api.api_key == "test-token"
        assert api.base_url == "https://api.b365api.com/v3/"
        assert api.SPORT_ID == 92

        # Verify managers are initialized
        assert isinstance(api.leagues, LeagueManager)
        assert isinstance(api.events, EventsManager)
        assert isinstance(api.players, PlayerManager)
        assert isinstance(api.odds, OddsManager)

        # Verify rate limit tracking is initialized
        assert api.rate_limit is None
        assert api.rate_limit_remaining is None
        assert api.rate_limit_reset is None

    def test_client_initialization_without_token(self):
        """Test client initialization fails without API token"""
        with pytest.raises(ValueError, match="API key is required"):
            TableTennisAPI(api_key=None)

        with pytest.raises(ValueError, match="API key is required"):
            TableTennisAPI(api_key="")

    def test_client_initialization_custom_base_url(self):
        """Test client initialization with custom base URL"""
        custom_url = "https://custom-api.example.com/v2/"
        api = TableTennisAPI(api_key="test-token", base_url=custom_url)

        assert api.base_url == custom_url

    def test_rate_limit_info_property(self):
        """Test rate_limit_info property"""
        api = TableTennisAPI(api_key="test-token")

        # Initially should be None values
        rate_info = api.rate_limit_info
        assert rate_info["limit"] is None
        assert rate_info["remaining"] is None
        assert rate_info["reset_time"] is None

        # Set some test values
        api.rate_limit = 3600
        api.rate_limit_remaining = 3595
        api.rate_limit_reset = datetime(2025, 7, 30, 22, 0, 0)

        rate_info = api.rate_limit_info
        assert rate_info["limit"] == 3600
        assert rate_info["remaining"] == 3595
        assert rate_info["reset_time"] == datetime(2025, 7, 30, 22, 0, 0)

    def test_is_rate_limited_method(self):
        """Test is_rate_limited method"""
        api = TableTennisAPI(api_key="test-token")

        # Initially should return False (no data available)
        assert api.is_rate_limited() is False

        # Test with high remaining requests
        api.rate_limit_remaining = 100
        assert api.is_rate_limited() is False

        # Test with low remaining requests (should warn)
        api.rate_limit_remaining = 5
        assert api.is_rate_limited() is True

        # Test edge case
        api.rate_limit_remaining = 10
        assert api.is_rate_limited() is False  # Exactly 10 is not limited

        api.rate_limit_remaining = 9
        assert api.is_rate_limited() is True  # Less than 10 is limited

    def test_manager_access(self):
        """Test that all managers are accessible and properly initialized"""
        api = TableTennisAPI(api_key="test-token")

        # Test that managers have reference to client
        assert api.leagues.client is api
        assert api.events.client is api
        assert api.players.client is api
        assert api.odds.client is api

        # Test that _make_request is accessible through managers
        assert hasattr(api.leagues, "_make_request")
        assert hasattr(api.events, "_make_request")
        assert hasattr(api.players, "_make_request")
        assert hasattr(api.odds, "_make_request")


class TestClientPrivateMethods:
    """Test private methods of TableTennisAPI client"""

    def test_update_rate_limit_info(self):
        """Test _update_rate_limit_info method"""
        api = TableTennisAPI(api_key="test-token")

        # Test with all headers present
        headers = {
            "X-Ratelimit-Limit": "3600",
            "X-Ratelimit-Remaining": "3595",
            "X-Ratelimit-Reset": "1753815600",
        }

        api._update_rate_limit_info(headers)

        assert api.rate_limit == 3600
        assert api.rate_limit_remaining == 3595
        assert api.rate_limit_reset == datetime.fromtimestamp(1753815600)

    def test_update_rate_limit_info_partial_headers(self):
        """Test _update_rate_limit_info with missing headers"""
        api = TableTennisAPI(api_key="test-token")

        # Test with only some headers
        headers = {"X-Ratelimit-Remaining": "3500"}

        api._update_rate_limit_info(headers)

        assert api.rate_limit is None  # Not updated
        assert api.rate_limit_remaining == 3500  # Updated
        assert api.rate_limit_reset is None  # Not updated

    def test_update_rate_limit_info_empty_headers(self):
        """Test _update_rate_limit_info with empty headers"""
        api = TableTennisAPI(api_key="test-token")

        # Set initial values
        api.rate_limit = 3600
        api.rate_limit_remaining = 3595

        # Update with empty headers (should not change values)
        api._update_rate_limit_info({})

        assert api.rate_limit == 3600  # Unchanged
        assert api.rate_limit_remaining == 3595  # Unchanged
