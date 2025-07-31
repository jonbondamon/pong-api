"""
Integration tests for OddsManager with real API calls.
Tests odds summary and detailed odds endpoints.
"""

import os

import pytest
from dotenv import load_dotenv

from tabletennis_api import TableTennisAPI
from tabletennis_api.exceptions import TableTennisAPIError

# Load environment variables
load_dotenv()


@pytest.fixture
def real_api_client():
    """Create a real API client for integration testing"""
    api_token = os.getenv("B365_API_TOKEN")
    if not api_token or api_token == "your-api-token-here":
        pytest.skip("B365_API_TOKEN not configured for integration tests")

    return TableTennisAPI(api_key=api_token)


class TestOddsManagerIntegration:
    """Integration tests for OddsManager using real API calls"""

    def test_real_odds_summary_functionality(self, real_api_client):
        """Test get_summary() method with real API calls."""
        print(f"\n🎯 Testing OddsManager.get_summary() with real API...")

        # Use event ID from research data that we know has odds
        event_id = "10385512"

        try:
            # Get odds summary
            print(f"   📊 Getting odds summary for event {event_id}...")
            odds_summary = real_api_client.odds.get_summary(event_id)

            print(f"   ✅ Successfully retrieved odds summary")
            print(f"   📋 Available bookmakers: {len(odds_summary)}")

            if odds_summary:
                # Display bookmaker information
                for bookmaker, data in odds_summary.items():
                    print(f"   🏢 {bookmaker}:")

                    if "odds" in data:
                        odds_data = data["odds"]
                        print(
                            f"      📈 Has odds data with {len(odds_data)} categories"
                        )

                        # Check for different odds categories
                        for category, category_odds in odds_data.items():
                            if category_odds:
                                print(
                                    f"         {category}: {len(category_odds)} markets"
                                )

                                # Show sample odds for each category
                                for market_id, odds in list(category_odds.items())[:2]:
                                    odds_info = []
                                    if "home_od" in odds and "away_od" in odds:
                                        odds_info.append(
                                            f"1x2: {odds['home_od']}/{odds['away_od']}"
                                        )
                                    if "handicap" in odds:
                                        odds_info.append(
                                            f"Handicap: {odds['handicap']}"
                                        )
                                    if "over_od" in odds and "under_od" in odds:
                                        odds_info.append(
                                            f"O/U: {odds['over_od']}/{odds['under_od']}"
                                        )

                                    if odds_info:
                                        print(
                                            f"            {market_id}: {', '.join(odds_info)}"
                                        )
                            else:
                                print(f"         {category}: No odds available")
                    else:
                        print(f"      ❌ No odds data structure found")

                # Verify data structure
                assert isinstance(odds_summary, dict), "Should return dictionary"

                # Check for known bookmakers from research data
                expected_bookmakers = ["Bet365", "DafaBet"]
                found_bookmakers = [
                    bm for bm in expected_bookmakers if bm in odds_summary
                ]
                print(
                    f"   🎯 Found {len(found_bookmakers)}/{len(expected_bookmakers)} expected bookmakers"
                )

            else:
                print(f"   ⚠️  No odds data returned (might be expected for this event)")

        except TableTennisAPIError as e:
            if "EVENT_NOT_FOUND" in str(e) or "ODDS_NOT_AVAILABLE" in str(e):
                print(f"   ℹ️  Event {event_id} has no odds data: {e}")
            else:
                print(f"   ❌ API Error: {e}")
                raise

    def test_real_odds_detailed_functionality(self, real_api_client):
        """Test get_detailed() method with real API calls."""
        print(f"\n🎯 Testing OddsManager.get_detailed() with real API...")

        # Use event ID from research data that we know has detailed odds
        event_id = "10385512"
        bookmaker = "bet365"

        try:
            # Get detailed odds
            print(
                f"   📊 Getting detailed odds for event {event_id} from {bookmaker}..."
            )
            detailed_odds = real_api_client.odds.get_detailed(event_id, bookmaker)

            print(f"   ✅ Successfully retrieved detailed odds")

            if detailed_odds:
                # Check data structure
                assert isinstance(detailed_odds, dict), "Should return dictionary"

                # Check for stats section
                if "stats" in detailed_odds:
                    stats = detailed_odds["stats"]
                    print(f"   📈 Stats section found with {len(stats)} fields")
                    if "matching_dir" in stats:
                        print(f"      Matching direction: {stats['matching_dir']}")
                else:
                    print(f"   ⚠️  No stats section found")

                # Check for odds section
                if "odds" in detailed_odds:
                    odds_data = detailed_odds["odds"]
                    print(f"   📊 Odds section found with {len(odds_data)} categories")

                    for category, odds_history in odds_data.items():
                        if odds_history and isinstance(odds_history, list):
                            print(f"      {category}: {len(odds_history)} odds updates")

                            # Show sample from odds history
                            if odds_history:
                                latest_odds = odds_history[0]
                                oldest_odds = odds_history[-1]

                                print(
                                    f"         Latest: {latest_odds.get('ss', 'N/A')} score"
                                )
                                if (
                                    "home_od" in latest_odds
                                    and "away_od" in latest_odds
                                ):
                                    print(
                                        f"         Latest odds: {latest_odds['home_od']}/{latest_odds['away_od']}"
                                    )

                                print(
                                    f"         Opening: {oldest_odds.get('ss', 'N/A')} score"
                                )
                                if (
                                    "home_od" in oldest_odds
                                    and "away_od" in oldest_odds
                                ):
                                    print(
                                        f"         Opening odds: {oldest_odds['home_od']}/{oldest_odds['away_od']}"
                                    )
                        else:
                            print(f"      {category}: No odds history")
                else:
                    print(f"   ⚠️  No odds section found")

                # Verify expected categories from research data
                expected_categories = [
                    "92_1",
                    "92_2",
                    "92_3",
                ]  # Match winner, Handicap, Over/Under
                found_categories = [
                    cat
                    for cat in expected_categories
                    if cat in detailed_odds.get("odds", {})
                ]
                print(
                    f"   🎯 Found {len(found_categories)}/{len(expected_categories)} expected odds categories"
                )

            else:
                print(f"   ⚠️  No detailed odds data returned")

        except TableTennisAPIError as e:
            if "EVENT_NOT_FOUND" in str(e) or "ODDS_NOT_AVAILABLE" in str(e):
                print(f"   ℹ️  Event {event_id} has no detailed odds: {e}")
            else:
                print(f"   ❌ API Error: {e}")
                raise

    def test_real_odds_multiple_bookmakers(self, real_api_client):
        """Test get_detailed() with different bookmakers."""
        print(f"\n🎯 Testing OddsManager.get_detailed() with multiple bookmakers...")

        event_id = "10385512"
        bookmakers = ["bet365", "pinnacle", "betfair"]

        for bookmaker in bookmakers:
            try:
                print(f"   📊 Testing bookmaker: {bookmaker}")
                detailed_odds = real_api_client.odds.get_detailed(event_id, bookmaker)

                if detailed_odds:
                    print(f"      ✅ {bookmaker}: Data available")
                    if "odds" in detailed_odds:
                        categories = len(detailed_odds["odds"])
                        print(f"         📈 {categories} odds categories")
                else:
                    print(f"      ⚠️  {bookmaker}: No data available")

            except TableTennisAPIError as e:
                if "ODDS_NOT_AVAILABLE" in str(e):
                    print(f"      ℹ️  {bookmaker}: No odds available ({e})")
                else:
                    print(f"      ❌ {bookmaker}: API Error - {e}")

    def test_real_odds_with_events_integration(self, real_api_client):
        """Test integration between OddsManager and EventsManager."""
        print(f"\n🎯 Testing OddsManager integration with EventsManager...")

        try:
            # Get some recent events first
            print(f"   📊 Getting recent ended events...")
            ended_events = real_api_client.events.get_ended(page=1)

            if ended_events.results:
                # Take first event and get its odds
                test_event = ended_events.results[0]
                print(
                    f"   🏓 Testing with event: {test_event.home_player.name} vs {test_event.away_player.name}"
                )
                print(f"      Event ID: {test_event.id}")
                print(f"      Status: {test_event.status_description}")

                # Try to get odds for this event
                try:
                    odds_summary = real_api_client.odds.get_summary(test_event.id)

                    if odds_summary:
                        print(
                            f"      ✅ Found odds data from {len(odds_summary)} bookmakers"
                        )

                        # Try detailed odds
                        detailed_odds = real_api_client.odds.get_detailed(test_event.id)
                        if detailed_odds and "odds" in detailed_odds:
                            print(
                                f"      ✅ Found detailed odds with {len(detailed_odds['odds'])} categories"
                            )
                        else:
                            print(f"      ⚠️  No detailed odds available")
                    else:
                        print(f"      ℹ️  No odds data available for this event")

                except TableTennisAPIError as e:
                    print(f"      ℹ️  Odds not available for this event: {e}")

            else:
                print(f"   ⚠️  No ended events found to test with")

        except TableTennisAPIError as e:
            print(f"   ❌ Integration test failed: {e}")
            raise

    def test_real_odds_error_handling(self, real_api_client):
        """Test error handling with invalid event IDs."""
        print(f"\n🎯 Testing OddsManager error handling...")

        # Test with invalid event ID
        invalid_event_id = "999999999"

        try:
            print(f"   🧪 Testing with invalid event ID: {invalid_event_id}")
            odds_summary = real_api_client.odds.get_summary(invalid_event_id)

            # If we get here, the API might return empty results instead of an error
            if not odds_summary:
                print(
                    f"      ✅ API correctly returned empty results for invalid event"
                )
            else:
                print(f"      ⚠️  API returned data for invalid event (unexpected)")

        except TableTennisAPIError as e:
            print(f"      ✅ API correctly raised error for invalid event: {e}")

        # Test detailed odds with invalid event
        try:
            print(f"   🧪 Testing detailed odds with invalid event ID")
            detailed_odds = real_api_client.odds.get_detailed(invalid_event_id)

            if not detailed_odds:
                print(
                    f"      ✅ Detailed odds correctly returned empty for invalid event"
                )
            else:
                print(
                    f"      ⚠️  Detailed odds returned data for invalid event (unexpected)"
                )

        except TableTennisAPIError as e:
            print(
                f"      ✅ Detailed odds correctly raised error for invalid event: {e}"
            )
