"""Main client for Table Tennis API wrapper"""

from datetime import datetime
from typing import Any, Dict, Optional

import requests

from .exceptions import (AuthenticationError, RateLimitError, ServerError,
                         TableTennisAPIError)
from .managers import EventsManager, LeagueManager, OddsManager, PlayerManager


class TableTennisAPI:
    """Client for interacting with B365 Table Tennis API"""

    SPORT_ID = 92  # Table Tennis sport ID

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize the Table Tennis API client.

        Args:
            api_key: API authentication token (required)
            base_url: Base URL for the API (defaults to B365 API v3)
        """
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url or "https://api.b365api.com/v3/"
        self.session = requests.Session()

        # Rate limiting info (updated from response headers)
        self.rate_limit = None
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

        # Initialize endpoint managers
        self.events = EventsManager(self)
        self.leagues = LeagueManager(self)
        self.players = PlayerManager(self)
        self.odds = OddsManager(self)

    def _make_request(
        self, method: str, endpoint: str, version: str = "v3", **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request to the API with automatic token injection and rate limit tracking.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            version: API version (v1, v2, v3)
            **kwargs: Additional request parameters

        Returns:
            API response as dictionary
        """
        # Build full URL with version
        base_url = self.base_url.rstrip("/").rsplit("/", 1)[
            0
        ]  # Remove version if present
        url = f"{base_url}/{version}/{endpoint.lstrip('/')}"

        # Add token to params
        if "params" not in kwargs:
            kwargs["params"] = {}
        kwargs["params"]["token"] = self.api_key

        # Add sport_id for endpoints that need it
        endpoints_needing_sport_id = ["events/", "event/", "league", "team"]
        if "sport_id" not in kwargs["params"] and any(
            endpoint.startswith(ep) for ep in endpoints_needing_sport_id
        ):
            kwargs["params"]["sport_id"] = self.SPORT_ID

        try:
            response = self.session.request(method, url, **kwargs)

            # Update rate limit info from headers
            self._update_rate_limit_info(response.headers)

            response.raise_for_status()
            data = response.json()

            # Check for API-level errors
            if data.get("success") != 1:
                error_msg = data.get("error", "Unknown API error")
                raise TableTennisAPIError(f"API error: {error_msg}")

            return data

        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise AuthenticationError("Invalid API token")
            elif response.status_code == 429:
                raise RateLimitError(
                    f"Rate limit exceeded. Resets at: {self.rate_limit_reset}"
                )
            elif response.status_code >= 500:
                raise ServerError(f"API server error: {e}")
            else:
                raise TableTennisAPIError(f"API request failed: {e}")
        except requests.exceptions.RequestException as e:
            raise TableTennisAPIError(f"Request error: {e}")

    def _update_rate_limit_info(self, headers: dict):
        """Update rate limit information from response headers"""
        if "X-Ratelimit-Limit" in headers:
            self.rate_limit = int(headers["X-Ratelimit-Limit"])
        if "X-Ratelimit-Remaining" in headers:
            self.rate_limit_remaining = int(headers["X-Ratelimit-Remaining"])
        if "X-Ratelimit-Reset" in headers:
            self.rate_limit_reset = datetime.fromtimestamp(
                int(headers["X-Ratelimit-Reset"])
            )

    @property
    def rate_limit_info(self) -> Dict[str, Any]:
        """Get current rate limit information"""
        return {
            "limit": self.rate_limit,
            "remaining": self.rate_limit_remaining,
            "reset_time": self.rate_limit_reset,
        }

    def is_rate_limited(self) -> bool:
        """Check if rate limit is close to being exceeded"""
        if self.rate_limit_remaining is None:
            return False
        return self.rate_limit_remaining < 10  # Warn when < 10 requests remaining
