"""Data models for Table Tennis API"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


@dataclass
class Player:
    """Represents a table tennis player or doubles pair from B365 API"""

    id: str
    name: str
    country_code: Optional[str] = None  # "cc" field, can be null
    image_id: Optional[str] = None  # Profile image ID, can be null

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        """Create Player instance from B365 API response dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            country_code=data.get("cc"),
            image_id=data.get("image_id") if data.get("image_id", 0) != 0 else None,
        )

    @property
    def is_doubles_pair(self) -> bool:
        """Check if this represents a doubles pair (contains '/')"""
        return "/" in self.name

    @property
    def has_image(self) -> bool:
        """Check if player has a profile image"""
        return self.image_id is not None

    @property
    def player_names(self) -> List[str]:
        """Get individual player names (splits doubles pairs)"""
        if self.is_doubles_pair:
            return [name.strip() for name in self.name.split("/")]
        return [self.name]

    @property
    def display_name(self) -> str:
        """Get formatted display name"""
        return self.name


@dataclass
class TimelineEntry:
    """Represents a single point/score change in match timeline"""

    id: str
    game: str  # Game number (1, 2, 3, etc.)
    team: str  # Team that scored (0=home, 1=away)
    score: str  # Current score in format "home-away"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimelineEntry":
        """Create TimelineEntry from API timeline data"""
        return cls(id=data["id"], game=data["gm"], team=data["te"], score=data["ss"])

    @property
    def home_score(self) -> int:
        """Get home team score from score string"""
        return int(self.score.split("-")[0])

    @property
    def away_score(self) -> int:
        """Get away team score from score string"""
        return int(self.score.split("-")[1])

    @property
    def scoring_team(self) -> str:
        """Get which team scored (home/away)"""
        return "home" if self.team == "0" else "away"


@dataclass
class StadiumData:
    """Represents stadium/venue information"""

    id: str
    name: str
    city: Optional[str] = None
    country: Optional[str] = None
    capacity: Optional[int] = None
    coordinates: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StadiumData":
        """Create StadiumData from API data"""
        return cls(
            id=data["id"],
            name=data["name"],
            city=data.get("city"),
            country=data.get("country"),
            capacity=data.get("capacity"),
            coordinates=data.get("googlecoords"),
        )


@dataclass
class EventExtra:
    """Extra event information like best-of-sets and stadium data"""

    best_of_sets: str
    stadium_data: Optional[StadiumData] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventExtra":
        """Create EventExtra from API data"""
        stadium_data = None
        if "stadium_data" in data and data["stadium_data"]:
            stadium_data = StadiumData.from_dict(data["stadium_data"])

        return cls(best_of_sets=data["bestofsets"], stadium_data=stadium_data)


@dataclass
class EventSummary:
    """Represents a basic event summary from listing endpoints (inplay, upcoming, ended)"""

    id: str
    sport_id: str
    time: str  # Unix timestamp
    time_status: str  # "1"=scheduled, "2"=live, "3"=finished
    league_id: str
    league_name: str
    league_country_code: Optional[str]
    home_player: Player
    away_player: Player
    current_score: str  # Current live score like "3-2" or "11-9"
    game_scores: Dict[str, Dict[str, str]]  # Game-by-game scores
    bet365_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventSummary":
        """Create EventSummary instance from B365 API response dictionary"""
        # Parse league info
        league = data["league"]

        # Parse players - handle both regular and alternative names (o_home/o_away fields)
        home_data = data.get("o_home") or data["home"]  # Use o_home if available
        home_player = Player(
            id=home_data["id"],
            name=home_data["name"],
            country_code=home_data.get("cc"),
            image_id=(
                home_data.get("image_id") if home_data.get("image_id", 0) != 0 else None
            ),
        )

        away_data = data.get("o_away") or data["away"]  # Use o_away if available
        away_player = Player(
            id=away_data["id"],
            name=away_data["name"],
            country_code=away_data.get("cc"),
            image_id=(
                away_data.get("image_id") if away_data.get("image_id", 0) != 0 else None
            ),
        )

        return cls(
            id=data["id"],
            sport_id=data["sport_id"],
            time=data["time"],
            time_status=data["time_status"],
            league_id=league["id"],
            league_name=league["name"],
            league_country_code=league.get("cc"),
            home_player=home_player,
            away_player=away_player,
            current_score=data["ss"],
            game_scores=data.get("scores", {}),
            bet365_id=data.get("bet365_id"),
        )

    @property
    def event_datetime(self) -> datetime:
        """Convert time timestamp to datetime object"""
        return datetime.fromtimestamp(int(self.time))

    @property
    def is_scheduled(self) -> bool:
        """Check if event is scheduled (not started)"""
        return self.time_status in [
            "0",
            "1",
        ]  # "0" = upcoming, "1" = scheduled/about to start

    @property
    def is_live(self) -> bool:
        """Check if event is currently live"""
        return self.time_status == "2"

    @property
    def is_finished(self) -> bool:
        """Check if event is finished"""
        return self.time_status == "3"

    @property
    def status_description(self) -> str:
        """Get human-readable status"""
        status_map = {"0": "Upcoming", "1": "Scheduled", "2": "Live", "3": "Finished"}
        return status_map.get(self.time_status, "Unknown")

    @property
    def current_game_score(self) -> str:
        """Get current game score (for live matches)"""
        return self.current_score

    @property
    def sets_score(self) -> tuple[int, int]:
        """Get sets score as (home_sets, away_sets)"""
        if "-" in self.current_score:
            parts = self.current_score.split("-")
            return (int(parts[0]), int(parts[1]))
        return (0, 0)

    def is_winner(self, player_name: str) -> bool:
        """Check if the specified player won this match"""
        if not self.is_finished:
            return False

        # Get sets scores
        home_sets, away_sets = self.sets_score

        # Determine winner
        if home_sets > away_sets:
            return self.home_player.name == player_name
        elif away_sets > home_sets:
            return self.away_player.name == player_name
        else:
            return False  # Draw or incomplete data


@dataclass
class Event:
    """Represents a detailed table tennis event/match from B365 API"""

    id: str
    sport_id: str
    time: str  # Unix timestamp
    time_status: str  # "1"=scheduled, "2"=live, "3"=finished
    league_id: str
    league_name: str
    league_country_code: Optional[str]
    home_player: Player
    away_player: Player
    final_score: str  # Format like "3-0", "3-2"
    game_scores: Dict[str, Dict[str, str]]  # Game-by-game scores
    timeline: List[TimelineEntry]
    extra: Optional[EventExtra] = None
    inplay_created_at: Optional[str] = None
    inplay_updated_at: Optional[str] = None
    confirmed_at: Optional[str] = None
    bet365_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create Event instance from B365 API response dictionary"""
        # Parse league info
        league = data["league"]

        # Parse players
        home_player = Player(
            id=data["home"]["id"],
            name=data["home"]["name"],
            country_code=data["home"].get("cc"),
            image_id=(
                data["home"].get("image_id")
                if data["home"].get("image_id", 0) != 0
                else None
            ),
        )

        away_player = Player(
            id=data["away"]["id"],
            name=data["away"]["name"],
            country_code=data["away"].get("cc"),
            image_id=(
                data["away"].get("image_id")
                if data["away"].get("image_id", 0) != 0
                else None
            ),
        )

        # Parse timeline
        timeline = []
        for timeline_data in data.get("timeline", []):
            timeline.append(TimelineEntry.from_dict(timeline_data))

        # Parse extra data
        extra = None
        if "extra" in data and data["extra"]:
            extra = EventExtra.from_dict(data["extra"])

        return cls(
            id=data["id"],
            sport_id=data["sport_id"],
            time=data["time"],
            time_status=data["time_status"],
            league_id=league["id"],
            league_name=league["name"],
            league_country_code=league.get("cc"),
            home_player=home_player,
            away_player=away_player,
            final_score=data["ss"],
            game_scores=data.get("scores", {}),
            timeline=timeline,
            extra=extra,
            inplay_created_at=data.get("inplay_created_at"),
            inplay_updated_at=data.get("inplay_updated_at"),
            confirmed_at=data.get("confirmed_at"),
            bet365_id=data.get("bet365_id"),
        )

    @property
    def event_datetime(self) -> datetime:
        """Convert time timestamp to datetime object"""
        return datetime.fromtimestamp(int(self.time))

    @property
    def is_scheduled(self) -> bool:
        """Check if event is scheduled (not started)"""
        return self.time_status == "1"

    @property
    def is_live(self) -> bool:
        """Check if event is currently live"""
        return self.time_status == "2"

    @property
    def is_finished(self) -> bool:
        """Check if event is finished"""
        return self.time_status == "3"

    @property
    def status_description(self) -> str:
        """Get human-readable status"""
        status_map = {"1": "Scheduled", "2": "Live", "3": "Finished"}
        return status_map.get(self.time_status, "Unknown")

    @property
    def home_sets_won(self) -> int:
        """Get number of sets won by home player"""
        return int(self.final_score.split("-")[0])

    @property
    def away_sets_won(self) -> int:
        """Get number of sets won by away player"""
        return int(self.final_score.split("-")[1])

    @property
    def winner(self) -> Optional[Player]:
        """Get the winning player (None if not finished)"""
        if not self.is_finished:
            return None
        return (
            self.home_player
            if self.home_sets_won > self.away_sets_won
            else self.away_player
        )

    @property
    def total_points_played(self) -> int:
        """Get total number of points played in the match"""
        return len(self.timeline)


@dataclass
class Match:
    """Represents a table tennis match"""

    id: str
    date: datetime
    league_id: str
    league_name: str
    player1: Player
    player2: Player
    status: str  # "scheduled", "live", "finished"
    score: Optional[Dict[str, Any]] = None
    venue: Optional[str] = None
    round: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Match":
        """Create Match instance from dictionary"""
        return cls(
            id=data["id"],
            date=datetime.fromisoformat(data["date"]),
            league_id=data["league_id"],
            league_name=data["league_name"],
            player1=Player.from_dict(data["player1"]),
            player2=Player.from_dict(data["player2"]),
            status=data["status"],
            score=data.get("score"),
            venue=data.get("venue"),
            round=data.get("round"),
        )


@dataclass
class Odds:
    """Represents betting odds for a match"""

    bookmaker: str
    match_id: str
    player1_odds: float
    player2_odds: float
    updated_at: datetime
    market_type: str = "moneyline"  # "moneyline", "handicap", "total_games"
    handicap: Optional[float] = None
    total: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Odds":
        """Create Odds instance from dictionary"""
        return cls(
            bookmaker=data["bookmaker"],
            match_id=data["match_id"],
            player1_odds=data["player1_odds"],
            player2_odds=data["player2_odds"],
            updated_at=datetime.fromisoformat(data["updated_at"]),
            market_type=data.get("market_type", "moneyline"),
            handicap=data.get("handicap"),
            total=data.get("total"),
        )


@dataclass
class PaginationInfo:
    """Pagination information from B365 API responses"""

    page: int
    per_page: int
    total: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaginationInfo":
        """Create PaginationInfo from API pager object"""
        return cls(page=data["page"], per_page=data["per_page"], total=data["total"])

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages"""
        return (self.total + self.per_page - 1) // self.per_page

    @property
    def has_next_page(self) -> bool:
        """Check if there's a next page"""
        return self.page < self.total_pages

    @property
    def has_previous_page(self) -> bool:
        """Check if there's a previous page"""
        return self.page > 1


@dataclass
class APIResponse(Generic[T]):
    """Generic API response wrapper with pagination"""

    results: List[T]
    pagination: Optional[PaginationInfo] = None

    @property
    def count(self) -> int:
        """Number of results in this response"""
        return len(self.results)


@dataclass
class League:
    """Represents a table tennis league or tournament from B365 API"""

    id: str
    name: str
    country_code: Optional[str] = None  # "cc" field, can be null
    has_leaguetable: bool = False  # Whether league has standings/table
    has_toplist: bool = False  # Whether league has player rankings

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "League":
        """Create League instance from B365 API response dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            country_code=data.get("cc"),
            has_leaguetable=bool(data.get("has_leaguetable", 0)),
            has_toplist=bool(data.get("has_toplist", 0)),
        )

    @property
    def supports_standings(self) -> bool:
        """Check if this league supports standings/table data"""
        return self.has_leaguetable

    @property
    def supports_rankings(self) -> bool:
        """Check if this league supports player rankings"""
        return self.has_toplist


@dataclass
class MatchStats:
    """Detailed statistics for a completed match"""

    match_id: str
    player1_stats: Dict[str, Any]
    player2_stats: Dict[str, Any]
    game_scores: List[Dict[str, int]]
    duration_minutes: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MatchStats":
        """Create MatchStats instance from dictionary"""
        return cls(
            match_id=data["match_id"],
            player1_stats=data["player1_stats"],
            player2_stats=data["player2_stats"],
            game_scores=data["game_scores"],
            duration_minutes=data.get("duration_minutes"),
        )


@dataclass
class PlayerMatchHistory:
    """Complete match history for a player with analysis metadata"""

    player_name: str
    matches: List[EventSummary]
    h2h_records: Dict[str, List[EventSummary]]  # opponent_name -> matches
    total_matches: int
    win_count: int
    loss_count: int
    date_range_days: int
    tournaments: List[str]  # Tournament names played in
    opponents: List[str]  # All opponents faced

    @property
    def win_rate(self) -> float:
        """Calculate overall win rate"""
        if self.total_matches == 0:
            return 0.0
        return self.win_count / self.total_matches

    @property
    def recent_form(self) -> List[bool]:
        """Get recent match results (True=win, False=loss) in chronological order"""
        # Sort matches by date and return win/loss pattern
        sorted_matches = sorted(
            self.matches, key=lambda m: m.event_datetime or datetime.min
        )
        return [
            match.is_winner(self.player_name) for match in sorted_matches[-10:]
        ]  # Last 10 matches

    @classmethod
    def from_matches(
        cls,
        player_name: str,
        matches: List[EventSummary],
        h2h_records: Dict[str, List[EventSummary]],
        date_range_days: int,
    ) -> "PlayerMatchHistory":
        """Create from list of matches with calculated metadata"""
        win_count = sum(1 for match in matches if match.is_winner(player_name))
        loss_count = len(matches) - win_count

        tournaments = list(
            set(match.league_name for match in matches if match.league_name)
        )
        opponents = list(
            set(
                (
                    match.away_player.name
                    if match.home_player.name == player_name
                    else match.home_player.name
                )
                for match in matches
            )
        )

        return cls(
            player_name=player_name,
            matches=matches,
            h2h_records=h2h_records,
            total_matches=len(matches),
            win_count=win_count,
            loss_count=loss_count,
            date_range_days=date_range_days,
            tournaments=tournaments,
            opponents=opponents,
        )


@dataclass
class TournamentData:
    """Complete tournament data with all matches and metadata"""

    tournament_id: str
    tournament_name: str
    matches: List[EventSummary]
    players: List[Player]
    total_matches: int
    completed_matches: int
    live_matches: int
    upcoming_matches: int
    date_range: tuple[Optional[datetime], Optional[datetime]]  # (start, end)
    has_odds_data: bool = False

    @property
    def completion_rate(self) -> float:
        """Calculate tournament completion percentage"""
        if self.total_matches == 0:
            return 0.0
        return self.completed_matches / self.total_matches

    @property
    def unique_players(self) -> List[str]:
        """Get list of unique player names in tournament"""
        player_names = set()
        for match in self.matches:
            player_names.add(match.home_player.name)
            player_names.add(match.away_player.name)
        return sorted(list(player_names))

    @classmethod
    def from_matches(
        cls,
        tournament_id: str,
        tournament_name: str,
        matches: List[EventSummary],
        has_odds_data: bool = False,
    ) -> "TournamentData":
        """Create from list of matches with calculated metadata"""
        completed = sum(1 for match in matches if match.is_finished)
        live = sum(1 for match in matches if match.is_live)
        upcoming = sum(1 for match in matches if match.is_scheduled)

        # Extract unique players
        players = []
        seen_player_ids = set()
        for match in matches:
            for player in [match.home_player, match.away_player]:
                if player.id not in seen_player_ids:
                    players.append(player)
                    seen_player_ids.add(player.id)

        # Calculate date range
        dates = [match.event_datetime for match in matches if match.event_datetime]
        date_range = (min(dates) if dates else None, max(dates) if dates else None)

        return cls(
            tournament_id=tournament_id,
            tournament_name=tournament_name,
            matches=matches,
            players=players,
            total_matches=len(matches),
            completed_matches=completed,
            live_matches=live,
            upcoming_matches=upcoming,
            date_range=date_range,
            has_odds_data=has_odds_data,
        )
