"""
Integration tests for EventsManager bulk data collection methods.
Tests the new get_player_history and get_tournament_complete methods with real API calls.
"""

import os

import pytest
from dotenv import load_dotenv

from tabletennis_api import TableTennisAPI
from tabletennis_api.exceptions import TableTennisAPIError
from tabletennis_api.models import PlayerMatchHistory, TournamentData

# Load environment variables
load_dotenv()


@pytest.fixture
def real_api_client():
    """Create a real API client for integration testing"""
    api_token = os.getenv("B365_API_TOKEN")
    if not api_token or api_token == "your-api-token-here":
        pytest.skip("B365_API_TOKEN not configured for integration tests")

    return TableTennisAPI(api_key=api_token)


class TestBulkEventsManagerIntegration:
    """Integration tests for EventsManager bulk data collection using real API calls"""

    def test_real_get_player_history_basic(self, real_api_client):
        """Test get_player_history() method with real API calls - basic functionality."""
        print(f"\n🎯 Testing EventsManager.get_player_history() with real API...")

        # Use an active player found in recent ended events
        player_name = "Serhii Pitsyk"

        try:
            # Get player history - limit scope to avoid too many API calls
            print(f"   📊 Getting {player_name} match history (7 days, no H2H)...")
            history = real_api_client.events.get_player_history(
                player_name=player_name,
                days=7,  # Short period to limit API calls
                include_h2h=False,  # Skip H2H to reduce API usage
                max_pages=3,  # Limit pages
            )

            print(f"   ✅ Successfully retrieved player history")

            # Verify return type
            assert isinstance(
                history, PlayerMatchHistory
            ), "Should return PlayerMatchHistory object"

            # Verify basic structure
            assert (
                history.player_name == player_name
            ), f"Player name should be '{player_name}'"
            assert isinstance(history.matches, list), "Matches should be a list"
            assert isinstance(history.tournaments, list), "Tournaments should be a list"
            assert isinstance(history.opponents, list), "Opponents should be a list"
            assert isinstance(history.h2h_records, dict), "H2H records should be a dict"

            print(f"   📈 Statistics:")
            print(f"      Total matches: {history.total_matches}")
            print(f"      Win count: {history.win_count}")
            print(f"      Loss count: {history.loss_count}")
            print(f"      Win rate: {history.win_rate:.2%}")
            print(f"      Date range: {history.date_range_days} days")

            # Verify calculated properties
            assert history.total_matches == len(
                history.matches
            ), "Total matches should match list length"
            assert (
                history.win_count + history.loss_count == history.total_matches
            ), "Wins + losses should equal total"
            assert history.date_range_days == 7, "Date range should match input"

            if history.total_matches > 0:
                assert (
                    0.0 <= history.win_rate <= 1.0
                ), "Win rate should be between 0 and 1"

                print(f"   🏆 Tournaments played:")
                for tournament in history.tournaments[:3]:  # Show first 3
                    print(f"      - {tournament}")

                print(f"   🥊 Opponents faced:")
                for opponent in history.opponents[:3]:  # Show first 3
                    print(f"      - {opponent}")

                # Verify recent form
                recent_form = history.recent_form
                assert isinstance(recent_form, list), "Recent form should be a list"
                assert all(
                    isinstance(result, bool) for result in recent_form
                ), "Recent form should contain booleans"
                print(
                    f"      Recent form: {['W' if win else 'L' for win in recent_form[-5:]]}"
                )  # Last 5
            else:
                print(f"   ℹ️  No matches found in the last 7 days")
                assert history.win_rate == 0.0, "Win rate should be 0 when no matches"

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_get_player_history_with_h2h(self, real_api_client):
        """Test get_player_history() with H2H records enabled."""
        print(f"\n🎯 Testing EventsManager.get_player_history() with H2H records...")

        player_name = "Serhii Pitsyk"

        try:
            # Get player history with H2H - very limited to control API usage
            print(f"   📊 Getting {player_name} match history with H2H (3 days)...")
            history = real_api_client.events.get_player_history(
                player_name=player_name,
                days=3,  # Very short period
                include_h2h=True,  # Enable H2H
                max_pages=2,  # Limit pages significantly
            )

            print(f"   ✅ Successfully retrieved player history with H2H")

            # Verify H2H structure
            assert isinstance(history.h2h_records, dict), "H2H records should be a dict"

            print(f"   📈 H2H Statistics:")
            print(f"      Total matches: {history.total_matches}")
            print(f"      H2H opponents: {len(history.h2h_records)}")

            if history.h2h_records:
                print(f"   🤝 Head-to-head records:")
                for opponent, h2h_matches in list(history.h2h_records.items())[
                    :2
                ]:  # Show first 2
                    print(f"      vs {opponent}: {len(h2h_matches)} matches")

                    # Verify H2H match structure
                    if h2h_matches:
                        for match in h2h_matches[:1]:  # Check first match
                            assert hasattr(match, "id"), "H2H match should have ID"
                            assert hasattr(
                                match, "home_player"
                            ), "H2H match should have home player"
                            assert hasattr(
                                match, "away_player"
                            ), "H2H match should have away player"
            else:
                print(f"   ℹ️  No H2H records found (expected for short time period)")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_get_player_history_extended_period(self, real_api_client):
        """Test get_player_history() with longer time period."""
        print(
            f"\n🎯 Testing EventsManager.get_player_history() with extended period..."
        )

        player_name = "Serhii Pitsyk"

        try:
            # Get longer history - but without H2H to control API usage
            print(f"   📊 Getting {player_name} match history (30 days, no H2H)...")
            history = real_api_client.events.get_player_history(
                player_name=player_name, days=30, include_h2h=False, max_pages=5
            )

            print(f"   ✅ Successfully retrieved extended player history")

            print(f"   📈 Extended Statistics:")
            print(f"      Total matches: {history.total_matches}")
            print(f"      Win rate: {history.win_rate:.2%}")
            print(f"      Tournaments: {len(history.tournaments)}")
            print(f"      Opponents: {len(history.opponents)}")

            if history.total_matches > 0:
                # Test win/loss calculation accuracy
                actual_wins = sum(
                    1 for match in history.matches if match.is_winner(player_name)
                )
                actual_losses = history.total_matches - actual_wins

                assert (
                    history.win_count == actual_wins
                ), f"Win count mismatch: {history.win_count} != {actual_wins}"
                assert (
                    history.loss_count == actual_losses
                ), f"Loss count mismatch: {history.loss_count} != {actual_losses}"

                print(f"   ✅ Win/loss calculations verified correctly")

                # Test tournament and opponent extraction
                unique_tournaments = set()
                unique_opponents = set()

                for match in history.matches:
                    if match.league_name:
                        unique_tournaments.add(match.league_name)

                    opponent = (
                        match.away_player.name
                        if match.home_player.name == player_name
                        else match.home_player.name
                    )
                    unique_opponents.add(opponent)

                assert len(history.tournaments) == len(
                    unique_tournaments
                ), "Tournament extraction mismatch"
                assert len(history.opponents) == len(
                    unique_opponents
                ), "Opponent extraction mismatch"

                print(f"   ✅ Tournament and opponent extraction verified")
            else:
                print(f"   ℹ️  No matches found in 30-day period")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_get_player_history_error_handling(self, real_api_client):
        """Test get_player_history() error handling with invalid inputs."""
        print(f"\n🎯 Testing EventsManager.get_player_history() error handling...")

        try:
            # Test with non-existent player
            print(f"   🧪 Testing with unknown player...")
            history = real_api_client.events.get_player_history(
                player_name="Unknown Player XYZ123",
                days=7,
                include_h2h=False,
                max_pages=1,
            )

            # Should return empty results, not raise an error
            assert isinstance(
                history, PlayerMatchHistory
            ), "Should return PlayerMatchHistory even for unknown player"
            assert (
                history.total_matches == 0
            ), "Should have no matches for unknown player"
            assert history.win_rate == 0.0, "Win rate should be 0 for unknown player"

            print(f"   ✅ Unknown player handled gracefully (0 matches)")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_get_player_history_performance(self, real_api_client):
        """Test get_player_history() performance and API usage efficiency."""
        print(f"\n🎯 Testing EventsManager.get_player_history() performance...")

        import time

        player_name = "Serhii Pitsyk"

        try:
            # Track API usage before
            initial_remaining = real_api_client.rate_limit_remaining
            start_time = time.time()

            print(f"   📊 Initial rate limit: {initial_remaining}")
            print(f"   ⏱️  Starting performance test...")

            # Get player history with reasonable limits
            history = real_api_client.events.get_player_history(
                player_name=player_name,
                days=14,
                include_h2h=False,  # Skip H2H for performance
                max_pages=3,
            )

            end_time = time.time()
            final_remaining = real_api_client.rate_limit_remaining

            # Calculate performance metrics
            elapsed_time = end_time - start_time

            print(f"   ⏱️  Execution time: {elapsed_time:.2f} seconds")
            print(f"   📈 Matches found: {history.total_matches}")

            # Calculate API usage if rate limit info is available
            if initial_remaining is not None and final_remaining is not None:
                api_calls_used = initial_remaining - final_remaining
                print(f"   📊 API calls used: {api_calls_used}")

                if history.total_matches > 0:
                    print(
                        f"   🎯 Efficiency: {history.total_matches / max(api_calls_used, 1):.2f} matches per API call"
                    )

                # Performance assertions
                assert (
                    api_calls_used < 20
                ), "Should use less than 20 API calls for this test"
            else:
                print(f"   📊 Rate limit tracking not available")

            # Basic performance assertion
            assert elapsed_time < 30, "Should complete within 30 seconds"

            print(f"   ✅ Performance test passed")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_helper_methods(self, real_api_client):
        """Test the internal helper methods work correctly."""
        print(f"\n🎯 Testing EventsManager helper methods...")

        try:
            # Test _get_recent_player_matches directly
            print(f"   📊 Testing _get_recent_player_matches helper...")
            recent_matches = real_api_client.events._get_recent_player_matches(
                player_name="Serhii Pitsyk", days=7, max_pages=2
            )

            assert isinstance(recent_matches, list), "Should return list of matches"
            print(f"   ✅ Found {len(recent_matches)} recent matches")

            # Verify all matches contain the player
            for match in recent_matches:
                assert (
                    match.home_player.name == "Serhii Pitsyk"
                    or match.away_player.name == "Serhii Pitsyk"
                ), "Match should contain target player"

            if recent_matches:
                # Test _get_h2h_matches with real data
                print(f"   🤝 Testing _get_h2h_matches helper...")
                first_match = recent_matches[0]
                opponent = (
                    first_match.away_player.name
                    if first_match.home_player.name == "Serhii Pitsyk"
                    else first_match.home_player.name
                )

                h2h_matches = real_api_client.events._get_h2h_matches(
                    "Serhii Pitsyk", opponent, 30
                )
                assert isinstance(h2h_matches, list), "H2H should return list"
                print(f"   ✅ Found {len(h2h_matches)} H2H matches vs {opponent}")

                # Verify H2H matches are between correct players
                for match in h2h_matches:
                    players = {match.home_player.name, match.away_player.name}
                    assert (
                        "Serhii Pitsyk" in players
                    ), "H2H match should include Serhii Pitsyk"
                    assert opponent in players, f"H2H match should include {opponent}"

            print(f"   ✅ Helper methods working correctly")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise


class TestTournamentCompleteIntegration:
    """Integration tests for get_tournament_complete() using real API calls"""

    def test_real_get_tournament_complete_basic(self, real_api_client):
        """Test get_tournament_complete() method with real API calls - basic functionality."""
        print(f"\n🎯 Testing EventsManager.get_tournament_complete() with real API...")

        # First, get a recent tournament ID from ended events
        print(f"   📊 Finding active tournament from recent events...")
        try:
            recent_events = real_api_client.events.get_ended(page=1)

            if not recent_events.results:
                pytest.skip("No recent events found to test with")

            # Find most active tournament
            tournament_counts = {}
            for event in recent_events.results[:20]:
                league_id = event.league_id
                league_name = event.league_name
                if league_id not in tournament_counts:
                    tournament_counts[league_id] = {"name": league_name, "count": 0}
                tournament_counts[league_id]["count"] += 1

            # Get most active tournament
            most_active = max(tournament_counts.items(), key=lambda x: x[1]["count"])
            tournament_id = most_active[0]
            tournament_name = most_active[1]["name"]

            print(
                f"   🏆 Testing with tournament: {tournament_name} (ID: {tournament_id})"
            )
            print(f"      Found {most_active[1]['count']} recent matches")

            # Get complete tournament data
            print(f"   📊 Getting complete tournament data...")
            tournament = real_api_client.events.get_tournament_complete(
                tournament_id=tournament_id,
                include_odds=False,  # Skip odds for speed
                max_pages_per_type=2,  # Limit pages
            )

            print(f"   ✅ Successfully retrieved tournament data")

            # Verify return type
            assert isinstance(
                tournament, TournamentData
            ), "Should return TournamentData object"

            # Verify basic structure
            assert tournament.tournament_id == str(
                tournament_id
            ), f"Tournament ID should be '{tournament_id}'"
            assert (
                tournament.tournament_name == tournament_name
            ), f"Tournament name should be '{tournament_name}'"
            assert isinstance(tournament.matches, list), "Matches should be a list"
            assert isinstance(tournament.players, list), "Players should be a list"

            print(f"   📈 Tournament Statistics:")
            print(f"      Total matches: {tournament.total_matches}")
            print(f"      Completed: {tournament.completed_matches}")
            print(f"      Live: {tournament.live_matches}")
            print(f"      Upcoming: {tournament.upcoming_matches}")
            print(f"      Completion rate: {tournament.completion_rate:.1%}")
            print(f"      Unique players: {len(tournament.unique_players)}")

            # Verify counts match actual matches
            assert tournament.total_matches == len(
                tournament.matches
            ), "Total matches should match list length"
            assert (
                tournament.completed_matches
                + tournament.live_matches
                + tournament.upcoming_matches
                == tournament.total_matches
            )

            if tournament.total_matches > 0:
                assert (
                    0.0 <= tournament.completion_rate <= 1.0
                ), "Completion rate should be between 0 and 1"

                print(f"   🏓 Sample matches:")
                for match in tournament.matches[:3]:
                    status = (
                        "Completed"
                        if match.is_finished
                        else ("Live" if match.is_live else "Upcoming")
                    )
                    print(
                        f"      {match.home_player.name} vs {match.away_player.name} [{status}]"
                    )

                # Verify date range
                if tournament.date_range[0] and tournament.date_range[1]:
                    assert (
                        tournament.date_range[0] <= tournament.date_range[1]
                    ), "Date range should be properly ordered"
                    print(
                        f"      Date range: {tournament.date_range[0]} to {tournament.date_range[1]}"
                    )
            else:
                print(f"   ℹ️  No matches found for tournament")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_get_tournament_complete_with_odds(self, real_api_client):
        """Test get_tournament_complete() with odds checking enabled."""
        print(f"\n🎯 Testing EventsManager.get_tournament_complete() with odds...")

        try:
            # Get a small tournament to test odds
            recent_events = real_api_client.events.get_ended(page=1)

            if not recent_events.results:
                pytest.skip("No recent events found to test with")

            # Use first tournament found
            tournament_id = recent_events.results[0].league_id
            tournament_name = recent_events.results[0].league_name

            print(f"   🏆 Testing tournament: {tournament_name} (ID: {tournament_id})")

            # Get tournament with odds check enabled
            print(f"   💰 Getting tournament data with odds check...")
            tournament = real_api_client.events.get_tournament_complete(
                tournament_id=tournament_id,
                include_odds=True,  # Enable odds checking
                max_pages_per_type=1,  # Very limited for speed
            )

            print(f"   ✅ Successfully retrieved tournament data with odds check")

            # Verify odds flag
            print(f"      Has odds data: {tournament.has_odds_data}")

            # Note: has_odds_data may be False if no odds are available for recent matches
            assert isinstance(
                tournament.has_odds_data, bool
            ), "has_odds_data should be boolean"

            if tournament.has_odds_data:
                print(f"   💰 Tournament has odds data available")
            else:
                print(f"   ℹ️  No odds data available for this tournament")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_get_tournament_complete_all_match_types(self, real_api_client):
        """Test get_tournament_complete() captures all match types correctly."""
        print(
            f"\n🎯 Testing EventsManager.get_tournament_complete() match type collection..."
        )

        try:
            # Try to find a tournament with mixed match types
            recent_events = real_api_client.events.get_ended(page=1)

            if not recent_events.results:
                pytest.skip("No recent events found to test with")

            # Use TT Elite Series or similar active tournament
            tournament_id = recent_events.results[0].league_id
            tournament_name = recent_events.results[0].league_name

            print(f"   🏆 Testing tournament: {tournament_name} (ID: {tournament_id})")

            # Get complete tournament data
            tournament = real_api_client.events.get_tournament_complete(
                tournament_id=tournament_id,
                include_odds=False,
                max_pages_per_type=3,  # Get more pages to find different match types
            )

            print(f"   📊 Match type breakdown:")
            print(f"      Completed matches: {tournament.completed_matches}")
            print(f"      Live matches: {tournament.live_matches}")
            print(f"      Upcoming matches: {tournament.upcoming_matches}")
            print(f"      Total unique matches: {tournament.total_matches}")

            # Verify no duplicate matches
            match_ids = [match.id for match in tournament.matches]
            assert len(match_ids) == len(
                set(match_ids)
            ), "Should have no duplicate matches"

            # Verify match status counts
            actual_completed = sum(1 for m in tournament.matches if m.is_finished)
            actual_live = sum(1 for m in tournament.matches if m.is_live)
            actual_upcoming = sum(1 for m in tournament.matches if m.is_scheduled)

            assert (
                tournament.completed_matches == actual_completed
            ), "Completed count mismatch"
            assert tournament.live_matches == actual_live, "Live count mismatch"
            assert (
                tournament.upcoming_matches == actual_upcoming
            ), "Upcoming count mismatch"

            print(f"   ✅ Match type counts verified correctly")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_get_tournament_complete_performance(self, real_api_client):
        """Test get_tournament_complete() performance and efficiency."""
        print(f"\n🎯 Testing EventsManager.get_tournament_complete() performance...")

        import time

        try:
            # Get a tournament to test
            recent_events = real_api_client.events.get_ended(page=1)

            if not recent_events.results:
                pytest.skip("No recent events found to test with")

            tournament_id = recent_events.results[0].league_id
            tournament_name = recent_events.results[0].league_name

            print(f"   🏆 Testing tournament: {tournament_name} (ID: {tournament_id})")

            # Track performance
            initial_remaining = real_api_client.rate_limit_remaining
            start_time = time.time()

            # Get tournament data
            tournament = real_api_client.events.get_tournament_complete(
                tournament_id=tournament_id, include_odds=False, max_pages_per_type=2
            )

            end_time = time.time()
            final_remaining = real_api_client.rate_limit_remaining

            elapsed_time = end_time - start_time

            print(f"   ⏱️  Execution time: {elapsed_time:.2f} seconds")
            print(f"   📈 Total matches collected: {tournament.total_matches}")

            if initial_remaining is not None and final_remaining is not None:
                api_calls_used = initial_remaining - final_remaining
                print(f"   📊 API calls used: {api_calls_used}")

                # Should use roughly 3 API calls (ended, upcoming, live)
                assert api_calls_used <= 10, "Should use minimal API calls"

            # Performance assertion
            assert elapsed_time < 15, "Should complete within 15 seconds"

            print(f"   ✅ Performance test passed")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_get_tournament_complete_error_handling(self, real_api_client):
        """Test get_tournament_complete() error handling."""
        print(f"\n🎯 Testing EventsManager.get_tournament_complete() error handling...")

        try:
            # Test with non-existent tournament
            print(f"   🧪 Testing with non-existent tournament ID...")
            tournament = real_api_client.events.get_tournament_complete(
                tournament_id="99999999",  # Unlikely to exist
                include_odds=False,
                max_pages_per_type=1,
            )

            # Should return empty tournament data, not raise error
            assert isinstance(
                tournament, TournamentData
            ), "Should return TournamentData even for unknown tournament"
            assert (
                tournament.total_matches == 0
            ), "Should have no matches for unknown tournament"
            assert (
                tournament.tournament_id == "99999999"
            ), "Should preserve tournament ID"
            assert (
                tournament.tournament_name == "Tournament 99999999"
            ), "Should have fallback name"

            print(f"   ✅ Unknown tournament handled gracefully (0 matches)")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_helper_method_get_tournament_matches(self, real_api_client):
        """Test the _get_tournament_matches helper method."""
        print(f"\n🎯 Testing _get_tournament_matches helper method...")

        try:
            # Get a tournament ID
            recent_events = real_api_client.events.get_ended(page=1)

            if not recent_events.results:
                pytest.skip("No recent events found to test with")

            tournament_id = recent_events.results[0].league_id
            tournament_name = recent_events.results[0].league_name

            print(
                f"   🏆 Testing with tournament: {tournament_name} (ID: {tournament_id})"
            )

            # Test helper method directly
            print(f"   📊 Getting ended matches for tournament...")
            ended_matches = real_api_client.events._get_tournament_matches(
                tournament_id=tournament_id, match_type="ended", max_pages=2
            )

            assert isinstance(ended_matches, list), "Should return list of matches"
            print(f"   ✅ Found {len(ended_matches)} ended matches")

            # Verify all matches are from the correct tournament
            for match in ended_matches:
                assert match.league_id == str(
                    tournament_id
                ), f"Match should be from tournament {tournament_id}"
                assert match.is_finished, "Ended matches should be finished"

            # Test with upcoming matches
            print(f"   📊 Getting upcoming matches for tournament...")
            upcoming_matches = real_api_client.events._get_tournament_matches(
                tournament_id=tournament_id, match_type="upcoming", max_pages=1
            )

            print(f"   ✅ Found {len(upcoming_matches)} upcoming matches")

            for match in upcoming_matches:
                assert match.league_id == str(
                    tournament_id
                ), f"Match should be from tournament {tournament_id}"
                assert match.is_scheduled, "Upcoming matches should be scheduled"

            print(f"   ✅ Helper method working correctly")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise


class TestEventsBulkIntegration:
    """Integration tests for get_events_bulk() using real API calls"""

    def test_real_get_events_bulk_basic(self, real_api_client):
        """Test get_events_bulk() method with real API calls - basic functionality."""
        print(f"\n🎯 Testing EventsManager.get_events_bulk() with real API...")

        # First, get some real event IDs from recent ended events
        print(f"   📊 Finding event IDs from recent matches...")
        try:
            recent_events = real_api_client.events.get_ended(page=1)

            if not recent_events.results or len(recent_events.results) < 3:
                pytest.skip("Not enough recent events found to test with")

            # Get first 3 event IDs
            event_ids = [event.id for event in recent_events.results[:3]]
            print(f"   📋 Testing with event IDs: {', '.join(event_ids)}")

            # Test bulk retrieval
            print(f"   🏓 Getting events in bulk...")
            events = real_api_client.events.get_events_bulk(
                event_ids=event_ids, include_odds=False, include_view=False
            )

            print(f"   ✅ Successfully retrieved events in bulk")

            # Verify return type
            assert isinstance(events, dict), "Should return dict mapping IDs to events"

            # Verify we got all requested events
            assert len(events) == len(
                event_ids
            ), f"Should retrieve all {len(event_ids)} events"

            for event_id in event_ids:
                assert event_id in events, f"Event {event_id} should be in results"

                event = events[event_id]
                assert hasattr(event, "home_player"), "Event should have home_player"
                assert hasattr(event, "away_player"), "Event should have away_player"
                assert event.id == event_id, "Event ID should match requested ID"

                print(f"      ✓ {event.home_player.name} vs {event.away_player.name}")

            print(f"   ✅ All event data verified correctly")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_get_events_bulk_with_view_data(self, real_api_client):
        """Test get_events_bulk() with view data enabled."""
        print(f"\n🎯 Testing EventsManager.get_events_bulk() with view data...")

        try:
            # Get one recent event
            recent_events = real_api_client.events.get_ended(page=1)

            if not recent_events.results:
                pytest.skip("No recent events found to test with")

            event_id = recent_events.results[0].id
            print(f"   📋 Testing with event ID: {event_id}")

            # Test with view data
            print(f"   👁️  Getting event with detailed view data...")
            events = real_api_client.events.get_events_bulk(
                event_ids=[event_id], include_view=True
            )

            assert len(events) == 1, "Should retrieve one event"
            assert event_id in events, "Event should be in results"

            event = events[event_id]
            if hasattr(event, "_view_data"):
                print(f"   ✅ View data was attached to event")
                assert event._view_data is not None, "View data should not be None"
            else:
                print(f"   ℹ️  No view data available for this event")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_get_events_bulk_with_odds_data(self, real_api_client):
        """Test get_events_bulk() with odds data enabled."""
        print(f"\n🎯 Testing EventsManager.get_events_bulk() with odds data...")

        try:
            # Check if odds manager is available
            if not hasattr(real_api_client, "odds"):
                pytest.skip("Odds manager not available in API client")

            # Get one recent event
            recent_events = real_api_client.events.get_ended(page=1)

            if not recent_events.results:
                pytest.skip("No recent events found to test with")

            event_id = recent_events.results[0].id
            print(f"   📋 Testing with event ID: {event_id}")

            # Test with odds data
            print(f"   💰 Getting event with odds data...")
            events = real_api_client.events.get_events_bulk(
                event_ids=[event_id], include_odds=True
            )

            assert len(events) == 1, "Should retrieve one event"
            assert event_id in events, "Event should be in results"

            event = events[event_id]
            if hasattr(event, "_odds_data"):
                print(f"   ✅ Odds data was attached to event")
                assert event._odds_data is not None, "Odds data should not be None"
            else:
                print(f"   ℹ️  No odds data available for this event")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_get_events_bulk_mixed_types(self, real_api_client):
        """Test get_events_bulk() with events from different types (ended, upcoming, live)."""
        print(f"\n🎯 Testing EventsManager.get_events_bulk() with mixed event types...")

        try:
            collected_ids = []

            # Try to get events from different types
            print(f"   📊 Collecting events from different types...")

            # Get ended event
            ended_events = real_api_client.events.get_ended(page=1)
            if ended_events.results:
                collected_ids.append(ended_events.results[0].id)
                print(f"      ✓ Found ended event: {ended_events.results[0].id}")

            # Get upcoming event
            try:
                upcoming_events = real_api_client.events.get_upcoming(page=1)
                if upcoming_events.results:
                    collected_ids.append(upcoming_events.results[0].id)
                    print(
                        f"      ✓ Found upcoming event: {upcoming_events.results[0].id}"
                    )
            except Exception:
                print(f"      ⚠️  No upcoming events available")

            # Get live event
            try:
                live_events = real_api_client.events.get_inplay(page=1)
                if live_events.results:
                    collected_ids.append(live_events.results[0].id)
                    print(f"      ✓ Found live event: {live_events.results[0].id}")
            except Exception:
                print(f"      ⚠️  No live events available")

            if not collected_ids:
                pytest.skip("Could not find events from different types")

            # Test bulk retrieval across types
            print(f"   🏓 Getting {len(collected_ids)} events from different types...")
            events = real_api_client.events.get_events_bulk(event_ids=collected_ids)

            assert len(events) == len(
                collected_ids
            ), f"Should retrieve all {len(collected_ids)} events"

            for event_id in collected_ids:
                assert event_id in events, f"Event {event_id} should be in results"
                event = events[event_id]

                status = (
                    "Ended"
                    if event.is_finished
                    else ("Live" if event.is_live else "Upcoming")
                )
                print(
                    f"      ✓ {event.home_player.name} vs {event.away_player.name} [{status}]"
                )

            print(f"   ✅ Successfully retrieved events from different types")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_get_events_bulk_performance(self, real_api_client):
        """Test get_events_bulk() performance compared to individual calls."""
        print(f"\n🎯 Testing EventsManager.get_events_bulk() performance...")

        import time

        try:
            # Get 5 event IDs
            recent_events = real_api_client.events.get_ended(page=1)

            if not recent_events.results or len(recent_events.results) < 5:
                pytest.skip("Not enough events for performance test")

            event_ids = [event.id for event in recent_events.results[:5]]
            print(f"   📋 Testing with {len(event_ids)} events")

            # Track performance
            initial_remaining = real_api_client.rate_limit_remaining
            start_time = time.time()

            # Use bulk method
            events = real_api_client.events.get_events_bulk(event_ids=event_ids)

            bulk_time = time.time() - start_time
            final_remaining = real_api_client.rate_limit_remaining

            print(f"   ⏱️  Bulk retrieval time: {bulk_time:.2f} seconds")
            print(f"   📈 Retrieved {len(events)} events")

            if initial_remaining is not None and final_remaining is not None:
                api_calls_used = initial_remaining - final_remaining
                print(f"   📊 API calls used: {api_calls_used}")

                # Should use fewer calls than individual requests
                assert api_calls_used < len(
                    event_ids
                ), "Bulk method should be more efficient"

            # Performance assertion
            assert bulk_time < 10, "Should complete within 10 seconds"

            print(f"   ✅ Performance test passed")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_get_events_bulk_partial_results(self, real_api_client):
        """Test get_events_bulk() when some events don't exist."""
        print(
            f"\n🎯 Testing EventsManager.get_events_bulk() with non-existent events..."
        )

        try:
            # Get one real event ID
            recent_events = real_api_client.events.get_ended(page=1)

            if not recent_events.results:
                pytest.skip("No recent events found to test with")

            real_event_id = recent_events.results[0].id
            fake_event_ids = ["99999999", "88888888"]  # Unlikely to exist

            all_ids = [real_event_id] + fake_event_ids
            print(f"   📋 Testing with {len(all_ids)} events (1 real, 2 fake)")

            # Test bulk retrieval
            events = real_api_client.events.get_events_bulk(event_ids=all_ids)

            # Should only find the real event
            assert len(events) >= 1, "Should find at least the real event"
            assert real_event_id in events, "Real event should be found"

            print(f"   ✅ Found {len(events)} out of {len(all_ids)} requested events")

            if len(events) < len(all_ids):
                not_found = set(all_ids) - set(events.keys())
                print(f"   ℹ️  Events not found: {', '.join(not_found)}")

        except TableTennisAPIError as e:
            print(f"   ❌ API Error: {e}")
            raise

    def test_real_get_events_bulk_validation(self, real_api_client):
        """Test get_events_bulk() validation."""
        print(f"\n🎯 Testing EventsManager.get_events_bulk() validation...")

        # Test empty list
        with pytest.raises(ValueError, match="event_ids cannot be empty"):
            real_api_client.events.get_events_bulk([])
        print(f"   ✅ Empty list validation passed")

        # Test too many IDs
        too_many_ids = [str(i) for i in range(101)]
        with pytest.raises(ValueError, match="Cannot request more than 100 events"):
            real_api_client.events.get_events_bulk(too_many_ids)
        print(f"   ✅ Max IDs validation passed")
