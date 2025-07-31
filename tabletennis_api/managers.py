"""Manager classes for different API endpoint groups"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from .models import (APIResponse, Event, EventSummary, League, PaginationInfo,
                     Player, PlayerMatchHistory, TournamentData)


class BaseManager:
    """Base class for API endpoint managers"""

    def __init__(self, client):
        self.client = client

    def _make_request(
        self, method: str, endpoint: str, version: str = "v3", **kwargs
    ) -> Dict[str, Any]:
        """Proxy to client's _make_request method"""
        return self.client._make_request(method, endpoint, version=version, **kwargs)


class EventsManager(BaseManager):
    """Manager for event-related endpoints"""

    def get_inplay(
        self, league_id: Optional[Union[str, int]] = None, page: int = 1
    ) -> APIResponse[EventSummary]:
        """
        Get live/in-play events for table tennis.

        This endpoint returns events that are currently being played or recently finished.
        Perfect for real-time betting applications and live score tracking.

        Args:
            league_id: Filter by specific league ID (optional)
            page: Page number for pagination (starts at 1)

        Returns:
            APIResponse containing list of EventSummary objects and pagination info

        Raises:
            TableTennisAPIError: If API request fails
            ValueError: If page number is invalid

        Examples:
            # Get all live events
            live_events = api.events.get_inplay()

            # Filter by specific league
            tt_cup_live = api.events.get_inplay(league_id="29097")

            # Access live scores
            for event in live_events.results:
                if event.is_live:
                    print(f"{event.home_player.name} vs {event.away_player.name}: {event.current_score}")
        """
        if page < 1:
            raise ValueError("Page number must be >= 1")

        params = {"page": page}
        if league_id:
            params["league_id"] = str(league_id)

        data = self._make_request("GET", "events/inplay", version="v3", params=params)

        # Parse pagination info
        pagination = None
        if "pager" in data:
            pagination = PaginationInfo.from_dict(data["pager"])

        # Parse event results
        events = []
        for event_data in data.get("results", []):
            events.append(EventSummary.from_dict(event_data))

        return APIResponse(results=events, pagination=pagination)

    def get_upcoming(
        self, league_id: Optional[Union[str, int]] = None, page: int = 1
    ) -> APIResponse[EventSummary]:
        """
        Get upcoming/scheduled events for table tennis.

        This endpoint returns events that are scheduled to start in the future.
        Perfect for planning betting strategies and tracking upcoming matches.

        Args:
            league_id: Filter by specific league ID (optional)
            page: Page number for pagination (starts at 1)

        Returns:
            APIResponse containing list of EventSummary objects and pagination info

        Raises:
            TableTennisAPIError: If API request fails
            ValueError: If page number is invalid

        Examples:
            # Get all upcoming events
            upcoming_events = api.events.get_upcoming()

            # Filter by specific league
            tt_cup_upcoming = api.events.get_upcoming(league_id="29097")

            # Check upcoming matches
            for event in upcoming_events.results:
                print(f"Upcoming: {event.home_player.name} vs {event.away_player.name}")
                print(f"Start time: {event.event_datetime}")
        """
        if page < 1:
            raise ValueError("Page number must be >= 1")

        params = {"page": page}
        if league_id:
            params["league_id"] = str(league_id)

        data = self._make_request("GET", "events/upcoming", version="v3", params=params)

        # Parse pagination info
        pagination = None
        if "pager" in data:
            pagination = PaginationInfo.from_dict(data["pager"])

        # Parse event results
        events = []
        for event_data in data.get("results", []):
            events.append(EventSummary.from_dict(event_data))

        return APIResponse(results=events, pagination=pagination)

    def get_ended(
        self, league_id: Optional[Union[str, int]] = None, page: int = 1
    ) -> APIResponse[EventSummary]:
        """
        Get completed/finished events for table tennis.

        This endpoint returns events that have finished/ended.
        Perfect for analyzing completed matches and historical data.

        Args:
            league_id: Filter by specific league ID (optional)
            page: Page number for pagination (starts at 1)

        Returns:
            APIResponse containing list of EventSummary objects and pagination info

        Raises:
            TableTennisAPIError: If API request fails
            ValueError: If page number is invalid

        Examples:
            # Get all ended events
            ended_events = api.events.get_ended()

            # Filter by specific league
            tt_cup_ended = api.events.get_ended(league_id="29097")

            # Analyze finished matches
            for event in ended_events.results:
                if event.is_finished:
                    print(f"Finished: {event.home_player.name} vs {event.away_player.name}: {event.current_score}")
        """
        if page < 1:
            raise ValueError("Page number must be >= 1")

        params = {"page": page}
        if league_id:
            params["league_id"] = str(league_id)

        data = self._make_request("GET", "events/ended", version="v3", params=params)

        # Parse pagination info
        pagination = None
        if "pager" in data:
            pagination = PaginationInfo.from_dict(data["pager"])

        # Parse event results
        events = []
        for event_data in data.get("results", []):
            events.append(EventSummary.from_dict(event_data))

        return APIResponse(results=events, pagination=pagination)

    def search(
        self,
        home: Optional[str] = None,
        away: Optional[str] = None,
        time: Optional[Union[str, datetime]] = None,
        page: int = 1,
    ) -> APIResponse[EventSummary]:
        """
        Search events by player names and date.

        This endpoint allows searching for specific events by filtering on player names
        and/or specific dates. Perfect for finding specific matches or tracking player performance.
        Based on research data, this endpoint DOES work for table tennis when using the correct parameters.

        Args:
            home: Home player name to search for (optional)
            away: Away player name to search for (optional)
            time: Date to search (YYYYMMDD format or datetime object, optional)
            page: Page number for pagination (starts at 1)

        Returns:
            APIResponse containing list of EventSummary objects and pagination info

        Raises:
            TableTennisAPIError: If API request fails
            ValueError: If page number is invalid or no search criteria provided

        Examples:
            # Search by home player
            events = api.events.search(home="Jan Kocab")

            # Search by both players (find specific matchups)
            events = api.events.search(home="Jan Kocab", away="Jan Benak")

            # Search by date
            from datetime import datetime
            events = api.events.search(time=datetime(2025, 7, 29))
            events = api.events.search(time="20250729")  # YYYYMMDD format

            # Combined search
            events = api.events.search(home="Jan Kocab", time="20250729")
        """
        if page < 1:
            raise ValueError("Page number must be >= 1")

        # For table tennis, all three parameters appear to be required for successful searches
        if not all([home, away, time]):
            raise ValueError(
                "All three parameters (home, away, and time) are required for table tennis event searches"
            )

        params = {"page": page}
        if home:
            params["home"] = home
        if away:
            params["away"] = away
        if time:
            if isinstance(time, datetime):
                params["time"] = time.strftime("%Y%m%d")  # YYYYMMDD format
            else:
                params["time"] = time

        data = self._make_request("GET", "events/search", version="v1", params=params)

        # Parse pagination info
        pagination = None
        if "pager" in data:
            pagination = PaginationInfo.from_dict(data["pager"])

        # Parse event results
        events = []
        for event_data in data.get("results", []):
            events.append(EventSummary.from_dict(event_data))

        return APIResponse(results=events, pagination=pagination)

    def get_details(
        self, event_ids: Union[str, int, List[Union[str, int]]]
    ) -> List[Event]:
        """
        Get detailed event information with timeline data.

        This is the main method for accessing comprehensive event data including:
        - Complete point-by-point timeline
        - Game-by-game scores
        - Stadium/venue information
        - Live tracking timestamps
        - Best-of-sets configuration

        Args:
            event_ids: Single event ID or list of event IDs (max 10 per request)

        Returns:
            List of Event objects with complete timeline and match data

        Raises:
            TableTennisAPIError: If API request fails
            ValueError: If more than 10 event IDs provided

        Examples:
            # Get single event details
            event = api.events.get_details("10385512")[0]

            # Get multiple events (batch request)
            events = api.events.get_details(["10385512", "10382865", "10380220"])

            # Access timeline data
            for point in event.timeline:
                print(f"Game {point.game}: {point.scoring_team} scored -> {point.score}")
        """
        # Handle single ID vs list
        if isinstance(event_ids, (str, int)):
            event_ids = [str(event_ids)]
        elif isinstance(event_ids, list):
            event_ids = [str(eid) for eid in event_ids]

        # Validate max 10 IDs per API documentation
        if len(event_ids) > 10:
            raise ValueError("Maximum 10 event IDs allowed per request")

        # Join IDs for API request
        event_ids_str = ",".join(event_ids)
        params = {"event_id": event_ids_str}

        data = self._make_request("GET", "event/view", version="v1", params=params)

        # Parse results into Event objects
        events = []
        for event_data in data.get("results", []):
            events.append(Event.from_dict(event_data))

        return events

    def get_history(
        self, event_id: Union[str, int], qty: int = 10
    ) -> Dict[str, List[EventSummary]]:
        """
        Get head-to-head match history for a specific event.

        This endpoint returns comprehensive match history related to a specific event,
        including head-to-head records between the players and their individual recent matches.
        Based on research data, this endpoint DOES work for table tennis.

        Args:
            event_id: Event ID to get history for (string or integer)
            qty: Number of historical matches to return per category (default: 10, max: 20)

        Returns:
            Dictionary with three keys:
            - 'h2h': List of head-to-head matches between the two players
            - 'home': List of recent matches for the home player
            - 'away': List of recent matches for the away player
            Each list contains EventSummary objects.

        Raises:
            TableTennisAPIError: If API request fails
            ValueError: If event_id is empty or qty is invalid

        Examples:
            # Get head-to-head history for a specific match
            history = api.events.get_history("10385512")

            # Access different history categories
            h2h_matches = history['h2h']  # Direct matchups between players
            home_recent = history['home']  # Home player's recent matches
            away_recent = history['away']  # Away player's recent matches

            # Analyze head-to-head record
            home_wins = sum(1 for match in h2h_matches if match.winner_id == match.home_player.id)
            away_wins = len(h2h_matches) - home_wins
            print(f"H2H Record: {home_wins}-{away_wins}")
        """
        if not event_id:
            raise ValueError("event_id cannot be empty")

        if qty < 1 or qty > 20:
            raise ValueError("qty must be between 1 and 20")

        params = {"event_id": str(event_id), "qty": qty}
        data = self._make_request("GET", "event/history", version="v1", params=params)

        # Parse the results structure
        results = data.get("results", {})
        history = {}

        # Parse each history category
        for category in ["h2h", "home", "away"]:
            events = []
            for event_data in results.get(category, []):
                events.append(EventSummary.from_dict(event_data))
            history[category] = events

        return history

    def get_player_history(
        self,
        player_name: str,
        days: int = 30,
        include_h2h: bool = True,
        max_pages: int = 10,
    ) -> PlayerMatchHistory:
        """
        Get complete match history for a player with analysis metadata.

        This is a bulk data collection method that efficiently gathers:
        - All recent matches for the player
        - Head-to-head records against opponents (if include_h2h=True)
        - Win/loss statistics and form analysis
        - Tournament participation and opponent lists

        Perfect for betting analysis workflows that need comprehensive player data.

        Args:
            player_name: Player name to search for (case-sensitive)
            days: Number of days back to search (default: 30)
            include_h2h: Whether to fetch head-to-head records (default: True)
            max_pages: Maximum pages to search to avoid excessive API calls (default: 10)

        Returns:
            PlayerMatchHistory object with matches, statistics, and analysis metadata

        Raises:
            TableTennisAPIError: If API request fails
            ValueError: If player_name is empty or days is invalid

        Examples:
            # Get 30 days of history for Jan Kocab
            history = api.events.get_player_history("Jan Kocab")
            print(f"Win rate: {history.win_rate:.2%}")
            print(f"Recent form: {history.recent_form}")

            # Get extended history without H2H (faster)
            history = api.events.get_player_history(
                "Jan Kocab",
                days=60,
                include_h2h=False
            )

            # Analyze tournament performance
            print(f"Tournaments: {history.tournaments}")
            print(f"Opponents faced: {len(history.opponents)}")
        """
        if not player_name or not player_name.strip():
            raise ValueError("player_name cannot be empty")

        if days < 1 or days > 365:
            raise ValueError("days must be between 1 and 365")

        if max_pages < 1 or max_pages > 50:
            raise ValueError("max_pages must be between 1 and 50")

        # Calculate date range for search
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        all_matches = []
        h2h_records = {}
        pages_searched = 0

        print(f"🔍 Searching for {player_name} matches in last {days} days...")

        # Since search API requires all 3 parameters, we'll use ended events instead
        print(f"   📊 Searching recent ended matches...")
        try:
            # Get recent ended events and filter for our player
            recent_matches = self._get_recent_player_matches(
                player_name, days, max_pages
            )
            all_matches.extend(recent_matches)
            print(f"   ✅ Found {len(recent_matches)} recent matches")
        except Exception as e:
            print(f"   ⚠️  Recent matches search failed: {e}")

        # Remove duplicates (in case player appears in both searches)
        unique_matches = {}
        for match in all_matches:
            unique_matches[match.id] = match
        all_matches = list(unique_matches.values())

        print(f"   📋 Total unique matches: {len(all_matches)}")

        # Get head-to-head records for each opponent
        if include_h2h and all_matches:
            print(f"   🤝 Fetching head-to-head records...")
            opponents = set()
            for match in all_matches:
                opponent = (
                    match.away_player.name
                    if match.home_player.name == player_name
                    else match.home_player.name
                )
                opponents.add(opponent)

            h2h_count = 0
            for opponent in list(opponents)[
                :10
            ]:  # Limit to top 10 opponents to avoid too many API calls
                try:
                    h2h_matches = self._get_h2h_matches(
                        player_name, opponent, days * 2
                    )  # Broader search for H2H
                    if h2h_matches:
                        h2h_records[opponent] = h2h_matches
                        h2h_count += len(h2h_matches)
                except Exception as e:
                    print(f"      ⚠️  H2H for {opponent} failed: {e}")

            print(
                f"   ✅ Found {h2h_count} H2H matches across {len(h2h_records)} opponents"
            )

        # Create PlayerMatchHistory object with metadata
        return PlayerMatchHistory.from_matches(
            player_name=player_name,
            matches=all_matches,
            h2h_records=h2h_records,
            date_range_days=days,
        )

    def _get_recent_player_matches(
        self, player_name: str, days: int, max_pages: int
    ) -> List[EventSummary]:
        """Helper method to get recent matches for a player from ended events"""
        matches = []
        cutoff_date = datetime.now() - timedelta(days=days)

        # Search through recent ended events to find player matches
        page = 1
        while page <= max_pages:
            try:
                response = self.get_ended(page=page)
                page_matches = []

                for event in response.results:
                    # Check if this player is in the match
                    if (
                        event.home_player.name == player_name
                        or event.away_player.name == player_name
                    ):

                        # Check if match is within our date range
                        if event.event_datetime and event.event_datetime >= cutoff_date:
                            page_matches.append(event)

                matches.extend(page_matches)

                # If we didn't find any matches in this page, likely no more recent matches
                if not page_matches and page > 1:
                    break

                # Continue to next page if available
                if not response.pagination or not response.pagination.has_next_page:
                    break

                page += 1

            except Exception as e:
                break

        return matches

    def _get_h2h_matches(
        self, player1: str, player2: str, days: int
    ) -> List[EventSummary]:
        """Helper method to get head-to-head matches between two players"""
        h2h_matches = []

        # Since search API requires all parameters, we'll use the event history API instead
        # This is more efficient for H2H analysis
        try:
            # Get recent matches for player1 and filter for matches against player2
            recent_matches = self._get_recent_player_matches(
                player1, days, 5
            )  # Limit to 5 pages

            for match in recent_matches:
                # Check if player2 is the opponent
                opponent = (
                    match.away_player.name
                    if match.home_player.name == player1
                    else match.home_player.name
                )
                if opponent == player2:
                    h2h_matches.append(match)

        except Exception:
            pass

        return h2h_matches

    def get_tournament_complete(
        self,
        tournament_id: Union[str, int],
        include_odds: bool = False,
        max_pages_per_type: int = 10,
    ) -> TournamentData:
        """
        Get complete tournament data with all matches across all statuses.

        This is a bulk data collection method that efficiently gathers:
        - All ended/completed matches in the tournament
        - All upcoming/scheduled matches
        - All live/in-play matches
        - Complete player roster and statistics
        - Tournament metadata and completion status

        Perfect for tournament analysis, bracket prediction, and comprehensive betting strategies.

        Args:
            tournament_id: Tournament/league ID (string or integer)
            include_odds: Whether to note if odds data is available (default: False)
            max_pages_per_type: Maximum pages to fetch per event type (default: 10)

        Returns:
            TournamentData object with complete tournament information and statistics

        Raises:
            TableTennisAPIError: If API request fails
            ValueError: If tournament_id is empty or max_pages is invalid

        Examples:
            # Get complete tournament data
            tournament = api.events.get_tournament_complete("29128")
            print(f"Completion: {tournament.completion_rate:.1%}")
            print(f"Players: {len(tournament.unique_players)}")

            # Include odds availability info
            tournament = api.events.get_tournament_complete(
                tournament_id="29128",
                include_odds=True
            )

            # Analyze tournament structure
            print(f"Total matches: {tournament.total_matches}")
            print(f"Completed: {tournament.completed_matches}")
            print(f"Live: {tournament.live_matches}")
            print(f"Upcoming: {tournament.upcoming_matches}")

            # Get player performance data
            for player in tournament.unique_players[:5]:
                player_matches = [m for m in tournament.matches
                                if m.home_player.name == player or m.away_player.name == player]
                print(f"{player}: {len(player_matches)} matches")
        """
        if not tournament_id or str(tournament_id).strip() == "":
            raise ValueError("tournament_id cannot be empty")

        if max_pages_per_type < 1 or max_pages_per_type > 20:
            raise ValueError("max_pages_per_type must be between 1 and 20")

        tournament_id = str(tournament_id)
        all_matches = []
        tournament_name = None

        print(f"🏓 Collecting complete tournament data for ID: {tournament_id}...")

        # Get ended matches
        print(f"   📊 Fetching completed matches...")
        try:
            ended_matches = self._get_tournament_matches(
                tournament_id, "ended", max_pages_per_type
            )
            all_matches.extend(ended_matches)

            # Extract tournament name from first match
            if ended_matches and not tournament_name:
                tournament_name = ended_matches[0].league_name

            print(f"   ✅ Found {len(ended_matches)} completed matches")
        except Exception as e:
            print(f"   ⚠️  Completed matches failed: {e}")

        # Get upcoming matches
        print(f"   📊 Fetching upcoming matches...")
        try:
            upcoming_matches = self._get_tournament_matches(
                tournament_id, "upcoming", max_pages_per_type
            )
            all_matches.extend(upcoming_matches)

            # Extract tournament name if not found yet
            if upcoming_matches and not tournament_name:
                tournament_name = upcoming_matches[0].league_name

            print(f"   ✅ Found {len(upcoming_matches)} upcoming matches")
        except Exception as e:
            print(f"   ⚠️  Upcoming matches failed: {e}")

        # Get live matches
        print(f"   📊 Fetching live matches...")
        try:
            live_matches = self._get_tournament_matches(
                tournament_id, "live", max_pages_per_type
            )
            all_matches.extend(live_matches)

            # Extract tournament name if not found yet
            if live_matches and not tournament_name:
                tournament_name = live_matches[0].league_name

            print(f"   ✅ Found {len(live_matches)} live matches")
        except Exception as e:
            print(f"   ⚠️  Live matches failed: {e}")

        # Remove duplicates (in case matches appear in multiple states)
        unique_matches = {}
        for match in all_matches:
            unique_matches[match.id] = match
        all_matches = list(unique_matches.values())

        print(f"   📋 Total unique matches: {len(all_matches)}")

        # Use tournament name from matches or fallback
        if not tournament_name:
            tournament_name = f"Tournament {tournament_id}"

        # Check for odds data if requested
        has_odds_data = False
        if include_odds and all_matches:
            print(f"   💰 Checking odds availability...")
            # Sample a few matches to see if odds are available
            sample_matches = all_matches[:3]
            odds_found = 0

            for match in sample_matches:
                try:
                    odds = self.client.odds.get_summary(match.id)
                    if odds:
                        odds_found += 1
                except Exception:
                    pass

            has_odds_data = odds_found > 0
            print(
                f"   💰 Odds available: {'Yes' if has_odds_data else 'No'} ({odds_found}/{len(sample_matches)} sample matches)"
            )

        # Create TournamentData object with metadata
        tournament_data = TournamentData.from_matches(
            tournament_id=tournament_id,
            tournament_name=tournament_name,
            matches=all_matches,
            has_odds_data=has_odds_data,
        )

        print(f"   🏆 Tournament Analysis Complete:")
        print(f"      Name: {tournament_data.tournament_name}")
        print(f"      Total matches: {tournament_data.total_matches}")
        print(f"      Completed: {tournament_data.completed_matches}")
        print(f"      Live: {tournament_data.live_matches}")
        print(f"      Upcoming: {tournament_data.upcoming_matches}")
        print(f"      Completion rate: {tournament_data.completion_rate:.1%}")
        print(f"      Unique players: {len(tournament_data.unique_players)}")

        return tournament_data

    def _get_tournament_matches(
        self, tournament_id: str, match_type: str, max_pages: int
    ) -> List[EventSummary]:
        """Helper method to get tournament matches by type"""
        matches = []
        page = 1

        while page <= max_pages:
            try:
                # Get matches by type
                if match_type == "ended":
                    response = self.get_ended(page=page)
                elif match_type == "upcoming":
                    response = self.get_upcoming(page=page)
                elif match_type == "live":
                    response = self.get_inplay(page=page)
                else:
                    break

                # Filter for our tournament
                tournament_matches = [
                    event
                    for event in response.results
                    if event.league_id == tournament_id
                ]

                matches.extend(tournament_matches)

                # If no matches found on this page, stop searching
                if not tournament_matches and page > 1:
                    break

                # Continue to next page if available
                if not response.pagination or not response.pagination.has_next_page:
                    break

                page += 1

            except Exception as e:
                break

        return matches

    def get_events_bulk(
        self,
        event_ids: List[Union[str, int]],
        include_odds: bool = False,
        include_view: bool = False,
    ) -> Dict[str, EventSummary]:
        """
        Get multiple events by their IDs in a single efficient operation.

        This method is useful when you need to retrieve specific events by ID,
        avoiding multiple individual API calls.

        Args:
            event_ids: List of event IDs to retrieve
            include_odds: Whether to fetch odds data for each event
            include_view: Whether to fetch detailed view data for each event

        Returns:
            Dictionary mapping event IDs to EventSummary objects

        Example:
            >>> # Get specific events
            >>> events = api.events.get_events_bulk(
            ...     event_ids=["12345", "12346", "12347"],
            ...     include_odds=True
            ... )
            >>> print(f"Found {len(events)} events")
            >>> for event_id, event in events.items():
            ...     print(f"{event.home_player.name} vs {event.away_player.name}")
        """
        # Input validation
        if not event_ids:
            raise ValueError("event_ids cannot be empty")

        if len(event_ids) > 100:
            raise ValueError("Cannot request more than 100 events at once")

        # Ensure all IDs are strings
        str_event_ids = [str(id) for id in event_ids]

        print(f"🏓 Fetching {len(str_event_ids)} events in bulk...")

        results = {}
        not_found = set(str_event_ids)

        # Strategy: Search through different event types to find the events
        # Most events will be in ended or upcoming, so check those first
        event_types = ["ended", "upcoming", "inplay"]

        for event_type in event_types:
            if not not_found:
                break  # All events found

            print(f"   📊 Searching in {event_type} events...")

            try:
                # Get events of this type
                method_map = {
                    "ended": self.get_ended,
                    "upcoming": self.get_upcoming,
                    "inplay": self.get_inplay,
                }

                # Search through pages to find our events
                for page in range(1, 6):  # Check up to 5 pages
                    response = method_map[event_type](page=page)

                    if not response.results:
                        break

                    # Check each event
                    for event in response.results:
                        if event.id in not_found:
                            results[event.id] = event
                            not_found.remove(event.id)

                            # Fetch additional data if requested
                            if include_view:
                                try:
                                    view_data = self.get_details(event.id)
                                    # Merge view data into event
                                    event._view_data = view_data
                                except Exception:
                                    pass  # View data is optional

                            if include_odds and hasattr(self.client, "odds"):
                                try:
                                    odds_data = self.client.odds.get_summary(event.id)
                                    event._odds_data = odds_data
                                except Exception:
                                    pass  # Odds data is optional

                    # Stop if we found all events
                    if not not_found:
                        break

                    # Stop if this was the last page
                    if (
                        not response.pager
                        or response.pager.page
                        >= response.pager.total // response.pager.per_page
                    ):
                        break

            except Exception as e:
                print(f"   ⚠️  Error searching {event_type} events: {e}")
                continue

        print(
            f"   ✅ Found {len(results)} out of {len(str_event_ids)} requested events"
        )

        if not_found:
            print(f"   ❌ Events not found: {', '.join(sorted(not_found))}")

        return results


class LeagueManager(BaseManager):
    """Manager for league-related endpoints"""

    def list(
        self, country_code: Optional[str] = None, page: int = 1
    ) -> APIResponse[League]:
        """
        Get list of leagues/tournaments for table tennis.

        Args:
            country_code: Filter by country code (e.g., 'cz', 'us', 'de')
            page: Page number for pagination (starts at 1)

        Returns:
            APIResponse containing list of League objects and pagination info

        Raises:
            TableTennisAPIError: If API request fails
            ValueError: If page number is invalid
        """
        if page < 1:
            raise ValueError("Page number must be >= 1")

        params = {"page": page}
        if country_code:
            params["cc"] = country_code.lower()

        data = self._make_request("GET", "league", version="v1", params=params)

        # Parse pagination info
        pagination = None
        if "pager" in data:
            pagination = PaginationInfo.from_dict(data["pager"])

        # Parse league results
        leagues = []
        for league_data in data.get("results", []):
            leagues.append(League.from_dict(league_data))

        return APIResponse(results=leagues, pagination=pagination)

    def list_all(self, country_code: Optional[str] = None) -> List[League]:
        """
        Get ALL leagues by automatically handling pagination.

        Args:
            country_code: Filter by country code (e.g., 'cz', 'us', 'de')

        Returns:
            Complete list of all League objects (handles pagination automatically)

        Note:
            This method makes multiple API calls. Use with caution due to rate limits.
            For table tennis, this could be ~11 API calls (1,107 total leagues).
        """
        all_leagues = []
        page = 1

        while True:
            response = self.list(country_code=country_code, page=page)
            all_leagues.extend(response.results)

            # Check if there are more pages
            if not response.pagination or not response.pagination.has_next_page:
                break

            page += 1

        return all_leagues

    def get_table(self, league_id: Union[str, int]) -> List[Dict[str, Any]]:
        """
        Get league standings/table for leagues with table format.

        Args:
            league_id: League ID (string or integer)

        Returns:
            List of league table entries

        Note:
            Only works for leagues where league.supports_standings is True
        """
        params = {"league_id": str(league_id)}
        data = self._make_request("GET", "league/table", version="v1", params=params)
        return data.get("results", [])

    def get_rankings(self, league_id: Union[str, int]) -> List[Dict[str, Any]]:
        """
        Get top players/rankings for leagues with rankings system.

        Args:
            league_id: League ID (string or integer)

        Returns:
            List of player rankings

        Note:
            Only works for leagues where league.supports_rankings is True
        """
        params = {"league_id": str(league_id)}
        data = self._make_request("GET", "league/toplist", version="v1", params=params)
        return data.get("results", [])


class PlayerManager(BaseManager):
    """Manager for player/team-related endpoints"""

    def list(
        self, country_code: Optional[str] = None, page: int = 1
    ) -> APIResponse[Player]:
        """
        Get list of players/teams for table tennis.

        Args:
            country_code: Filter by country code (e.g., 'cz', 'jp', 'cn')
            page: Page number for pagination (starts at 1)

        Returns:
            APIResponse containing list of Player objects and pagination info

        Raises:
            TableTennisAPIError: If API request fails
            ValueError: If page number is invalid
        """
        if page < 1:
            raise ValueError("Page number must be >= 1")

        params = {"page": page}
        if country_code:
            params["cc"] = country_code.lower()

        data = self._make_request("GET", "team", version="v2", params=params)

        # Parse pagination info
        pagination = None
        if "pager" in data:
            pagination = PaginationInfo.from_dict(data["pager"])

        # Parse player results
        players = []
        for player_data in data.get("results", []):
            players.append(Player.from_dict(player_data))

        return APIResponse(results=players, pagination=pagination)

    def list_all(self, country_code: Optional[str] = None) -> List[Player]:
        """
        Get ALL players by automatically handling pagination.

        Args:
            country_code: Filter by country code (e.g., 'cz', 'jp', 'cn')

        Returns:
            Complete list of all Player objects (handles pagination automatically)

        Warning:
            This method makes multiple API calls. Use with extreme caution due to rate limits.
            For table tennis, this could be ~211 API calls (21,082 total players).
            Consider using list() with pagination instead.
        """
        all_players = []
        page = 1

        while True:
            response = self.list(country_code=country_code, page=page)
            all_players.extend(response.results)

            # Check if there are more pages
            if not response.pagination or not response.pagination.has_next_page:
                break

            page += 1

        return all_players

    def search(
        self, query: str, limit: int = 20, country_code: Optional[str] = None
    ) -> List[Player]:
        """
        Search for players by name (client-side filtering).

        Args:
            query: Search query (player name or part of name)
            limit: Maximum number of results to return
            country_code: Optional country filter to narrow search

        Returns:
            List of Player objects matching the search query

        Note:
            This performs client-side filtering by fetching multiple pages
            and searching through names. For large datasets, this may use
            several API calls to find enough matches.
        """
        matches = []
        page = 1
        query_lower = query.lower()
        pages_searched = 0
        max_pages_to_search = 10  # Limit search to avoid excessive API calls

        while len(matches) < limit and pages_searched < max_pages_to_search:
            try:
                response = self.list(country_code=country_code, page=page)

                # Search through this page's results
                for player in response.results:
                    if query_lower in player.name.lower():
                        matches.append(player)
                        if len(matches) >= limit:
                            break

                # Check if there are more pages
                if not response.pagination or not response.pagination.has_next_page:
                    break

                page += 1
                pages_searched += 1

            except Exception:
                break  # Stop searching if we hit an error

        return matches[:limit]

    def get_singles_players(
        self, country_code: Optional[str] = None, page: int = 1
    ) -> APIResponse[Player]:
        """
        Get only individual players (filter out doubles pairs).

        Args:
            country_code: Filter by country code
            page: Page number for pagination

        Returns:
            APIResponse with only individual players (no doubles pairs)
        """
        response = self.list(country_code=country_code, page=page)

        # Filter out doubles pairs
        singles_players = [p for p in response.results if not p.is_doubles_pair]

        return APIResponse(results=singles_players, pagination=response.pagination)

    def get_doubles_pairs(
        self, country_code: Optional[str] = None, page: int = 1
    ) -> APIResponse[Player]:
        """
        Get only doubles pairs (filter out individual players).

        Args:
            country_code: Filter by country code
            page: Page number for pagination

        Returns:
            APIResponse with only doubles pairs (no individual players)
        """
        response = self.list(country_code=country_code, page=page)

        # Filter for doubles pairs only
        doubles_pairs = [p for p in response.results if p.is_doubles_pair]

        return APIResponse(results=doubles_pairs, pagination=response.pagination)

    def get_players_with_images(
        self, country_code: Optional[str] = None, page: int = 1
    ) -> APIResponse[Player]:
        """
        Get only players that have profile images.

        Args:
            country_code: Filter by country code
            page: Page number for pagination

        Returns:
            APIResponse with only players that have profile images
        """
        response = self.list(country_code=country_code, page=page)

        # Filter for players with images
        players_with_images = [p for p in response.results if p.has_image]

        return APIResponse(results=players_with_images, pagination=response.pagination)


class OddsManager(BaseManager):
    """Manager for odds-related endpoints"""

    def get_summary(self, event_id: str) -> Dict[str, Any]:
        """
        Get betting odds summary from multiple bookmakers.

        Args:
            event_id: Event ID

        Returns:
            Dictionary with odds summary from all bookmakers
        """
        params = {"event_id": event_id}
        data = self._make_request(
            "GET", "event/odds/summary", version="v2", params=params
        )
        return data.get("results", {})

    def get_detailed(self, event_id: str, bookmaker: str = "bet365") -> Dict[str, Any]:
        """
        Get detailed odds history from a specific bookmaker.

        Args:
            event_id: Event ID
            bookmaker: Bookmaker name (default: bet365)

        Returns:
            Dictionary with detailed odds data and history
        """
        params = {"event_id": event_id, "source": bookmaker}
        data = self._make_request("GET", "event/odds", version="v2", params=params)
        return data.get("results", {})
