"""Table Tennis API - A Python wrapper for table tennis/ping pong sports APIs"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .client import TableTennisAPI
from .exceptions import (AuthenticationError, RateLimitError, ServerError,
                         TableTennisAPIError)
from .managers import EventsManager, LeagueManager, OddsManager, PlayerManager
from .models import (APIResponse, Event, EventExtra, EventSummary, League,
                     PaginationInfo, Player, PlayerMatchHistory, StadiumData,
                     TimelineEntry, TournamentData)

__all__ = [
    "TableTennisAPI",
    "TableTennisAPIError",
    "AuthenticationError",
    "RateLimitError",
    "ServerError",
    "EventsManager",
    "LeagueManager",
    "PlayerManager",
    "OddsManager",
    "League",
    "Player",
    "Event",
    "EventSummary",
    "TimelineEntry",
    "StadiumData",
    "EventExtra",
    "PaginationInfo",
    "APIResponse",
    "PlayerMatchHistory",
    "TournamentData",
]
