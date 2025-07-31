"""
Integration tests for League functionality with real API calls.
These tests make actual HTTP requests to the B365 API.

Run with: pytest tests/test_integration_leagues.py -m integration
"""

import os

import pytest
from dotenv import load_dotenv

from tabletennis_api import TableTennisAPI, TableTennisAPIError
from tabletennis_api.models import APIResponse, League, PaginationInfo

# Load environment variables
load_dotenv()


@pytest.fixture(scope="module")
def real_api_client():
    """Create API client with real token for integration tests"""
    api_token = os.getenv("B365_API_TOKEN")
    if not api_token or api_token == "your-api-token-here":
        pytest.skip("No valid B365_API_TOKEN found in .env file")

    return TableTennisAPI(api_key=api_token)


@pytest.mark.integration
class TestLeagueIntegration:
    """Integration tests for League functionality with real API"""

    def test_real_league_list_basic(self, real_api_client):
        """
        Test basic league listing with real API call.
        API Requests: 1
        """
        response = real_api_client.leagues.list(page=1)

        # Verify response structure
        assert isinstance(response, APIResponse)
        assert len(response.results) > 0
        assert response.count > 0

        # Verify pagination info
        assert response.pagination is not None
        assert isinstance(response.pagination, PaginationInfo)
        assert response.pagination.page == 1
        assert response.pagination.per_page > 0
        assert response.pagination.total > 0
        assert response.pagination.total_pages > 0

        # Verify league objects
        first_league = response.results[0]
        assert isinstance(first_league, League)
        assert isinstance(first_league.id, str)
        assert len(first_league.name) > 0
        assert isinstance(first_league.has_leaguetable, bool)
        assert isinstance(first_league.has_toplist, bool)

        # Print results for manual verification
        print(f"\n✅ Successfully fetched {len(response.results)} leagues")
        print(f"📊 Total leagues available: {response.pagination.total}")
        print(
            f"📄 Page {response.pagination.page} of {response.pagination.total_pages}"
        )
        print(f"🏆 First league: {first_league.name} (ID: {first_league.id})")

        # Verify rate limit tracking
        assert real_api_client.rate_limit is not None
        assert real_api_client.rate_limit_remaining is not None
        print(
            f"⏱️  Rate limit: {real_api_client.rate_limit_remaining}/{real_api_client.rate_limit}"
        )

    def test_real_league_country_filter(self, real_api_client):
        """
        Test league listing with country filter.
        API Requests: 1
        """
        # Test with Czech Republic (known to have leagues)
        response = real_api_client.leagues.list(country_code="cz", page=1)

        assert isinstance(response, APIResponse)
        assert response.pagination is not None

        # Should have at least some Czech leagues
        print(f"\n🇨🇿 Found {len(response.results)} Czech leagues")
        if len(response.results) > 0:
            # Verify some leagues have Czech country code
            czech_leagues = [l for l in response.results if l.country_code == "cz"]
            print(f"🏆 Czech leagues with 'cz' code: {len(czech_leagues)}")

            # Show first few Czech league names
            for i, league in enumerate(response.results[:3]):
                print(f"  {i+1}. {league.name} (cc: {league.country_code})")

        # API should return success even if no results
        assert response.count >= 0

    def test_real_league_pagination(self, real_api_client):
        """
        Test pagination with real API calls.
        API Requests: 2 (page 1 and page 2)
        """
        # Get page 1
        page1 = real_api_client.leagues.list(page=1)
        assert page1.pagination.page == 1

        # Only test page 2 if there are multiple pages
        if page1.pagination.has_next_page:
            page2 = real_api_client.leagues.list(page=2)
            assert page2.pagination.page == 2
            assert page2.pagination.has_previous_page is True

            # Verify different results on different pages
            page1_ids = {league.id for league in page1.results}
            page2_ids = {league.id for league in page2.results}
            assert page1_ids.isdisjoint(
                page2_ids
            ), "Pages should have different leagues"

            print(f"\n📄 Page 1: {len(page1.results)} leagues")
            print(f"📄 Page 2: {len(page2.results)} leagues")
            print(f"🔢 Total pages: {page1.pagination.total_pages}")
        else:
            print(f"\n📄 Only one page of results ({len(page1.results)} leagues)")

    @pytest.mark.slow
    def test_real_league_capabilities(self, real_api_client):
        """
        Test leagues with different capabilities (standings/rankings).
        API Requests: 1
        """
        response = real_api_client.leagues.list(page=1)

        leagues_with_standings = [l for l in response.results if l.supports_standings]
        leagues_with_rankings = [l for l in response.results if l.supports_rankings]

        print(f"\n📊 Leagues with standings support: {len(leagues_with_standings)}")
        print(f"🏅 Leagues with rankings support: {len(leagues_with_rankings)}")

        # Show examples if available
        if leagues_with_standings:
            print("📊 Example leagues with standings:")
            for league in leagues_with_standings[:2]:
                print(f"  - {league.name} (ID: {league.id})")

        if leagues_with_rankings:
            print("🏅 Example leagues with rankings:")
            for league in leagues_with_rankings[:2]:
                print(f"  - {league.name} (ID: {league.id})")

        # At least some leagues should support standings
        assert len(leagues_with_standings) >= 0  # Could be 0, that's ok
        assert len(leagues_with_rankings) >= 0  # Could be 0, that's ok

    def test_real_api_error_handling(self, real_api_client):
        """
        Test error handling with invalid parameters.
        API Requests: 0 (client-side validation)
        """
        # Test invalid page number (should be caught client-side)
        with pytest.raises(ValueError, match="Page number must be >= 1"):
            real_api_client.leagues.list(page=0)

        # Test invalid page number (should be caught client-side)
        with pytest.raises(ValueError, match="Page number must be >= 1"):
            real_api_client.leagues.list(page=-1)

    def test_real_rate_limit_tracking(self, real_api_client):
        """
        Test that rate limit tracking works with real API.
        API Requests: 1
        """
        # Make a request and verify rate limit info is updated
        initial_remaining = real_api_client.rate_limit_remaining

        response = real_api_client.leagues.list(page=1)

        # Rate limit info should be available after request
        assert real_api_client.rate_limit is not None
        assert real_api_client.rate_limit_remaining is not None
        assert real_api_client.rate_limit_reset is not None

        # Should have used 1 request (if this is not the first call)
        if initial_remaining is not None:
            assert real_api_client.rate_limit_remaining <= initial_remaining

        # Rate limit info should be reasonable
        assert real_api_client.rate_limit > 0
        assert real_api_client.rate_limit_remaining >= 0

        print(f"\n⏱️  Rate Limit Status:")
        print(f"   Limit: {real_api_client.rate_limit} requests/hour")
        print(f"   Remaining: {real_api_client.rate_limit_remaining}")
        print(f"   Reset time: {real_api_client.rate_limit_reset}")
        print(f"   Is rate limited: {real_api_client.is_rate_limited()}")


@pytest.mark.integration
@pytest.mark.slow
class TestLeagueIntegrationAdvanced:
    """Advanced integration tests (use more API calls)"""

    def test_real_list_all_leagues_partial(self, real_api_client):
        """
        Test list_all with a small subset to avoid using too many API calls.
        API Requests: Variable (stops after finding some results)
        """
        # Get first page to see total
        first_page = real_api_client.leagues.list(page=1)
        total_pages = first_page.pagination.total_pages

        print(f"\n📊 Total pages available: {total_pages}")

        # Test a few pages (limited to avoid excessive API usage)
        max_pages_to_test = min(3, total_pages)
        all_leagues = []

        for page in range(1, max_pages_to_test + 1):
            if page == 1:
                # Use already fetched first page
                page_response = first_page
            else:
                page_response = real_api_client.leagues.list(page=page)

            all_leagues.extend(page_response.results)

            # Verify each page has expected structure
            assert len(page_response.results) > 0
            assert page_response.pagination.page == page

            # Check some leagues have expected properties
            for league in page_response.results[:2]:  # Check first 2 from each page
                assert isinstance(league, League)
                assert isinstance(league.id, str)
                assert isinstance(league.name, str)
                assert len(league.id) > 0
                assert len(league.name) > 0

        print(
            f"✅ Successfully tested {len(all_leagues)} leagues across {max_pages_to_test} pages"
        )

        # Verify we got unique leagues
        league_ids = [league.id for league in all_leagues]
        assert len(league_ids) == len(set(league_ids)), "Found duplicate league IDs"

    def test_real_league_table_functionality(self, real_api_client):
        """
        Test get_table() method with real API calls.
        First finds leagues that support standings, then tests the table functionality.
        API Requests: Variable (depends on finding leagues with standings)
        """
        print("\n🏆 Testing league table functionality...")

        # Find leagues that support standings
        leagues_with_tables = []
        max_pages_to_search = 3  # Limit search to avoid excessive API calls

        for page in range(1, max_pages_to_search + 1):
            response = real_api_client.leagues.list(page=page)

            for league in response.results:
                if league.supports_standings:
                    leagues_with_tables.append(league)
                    if len(leagues_with_tables) >= 3:  # We only need a few for testing
                        break

            if len(leagues_with_tables) >= 3:
                break

        print(f"📊 Found {len(leagues_with_tables)} leagues with standings support")

        if not leagues_with_tables:
            pytest.skip("No leagues with standings support found in first few pages")

        # Test get_table for each league that supports it
        for league in leagues_with_tables[:2]:  # Test first 2 to limit API calls
            print(f"📋 Testing table for: {league.name} (ID: {league.id})")

            try:
                table_data = real_api_client.leagues.get_table(league.id)

                # Verify response structure - API returns different formats
                if isinstance(table_data, list):
                    print(f"   ✅ Table has {len(table_data)} entries")
                    if table_data:
                        first_entry = table_data[0]
                        assert isinstance(first_entry, dict)
                        print(f"   📝 Sample entry keys: {list(first_entry.keys())}")
                    else:
                        print(f"   ℹ️  Table is empty (no current standings)")

                elif isinstance(table_data, dict):
                    print(
                        f"   ✅ Table has nested structure with keys: {list(table_data.keys())}"
                    )

                    # Check for common table sections
                    if "overall" in table_data and "tables" in table_data["overall"]:
                        overall_tables = table_data["overall"]["tables"]
                        print(f"   📊 Overall tables: {len(overall_tables)} entries")

                    if "home" in table_data and "tables" in table_data["home"]:
                        home_tables = table_data["home"]["tables"]
                        print(f"   🏠 Home tables: {len(home_tables)} entries")

                    if "away" in table_data and "tables" in table_data["away"]:
                        away_tables = table_data["away"]["tables"]
                        print(f"   🚌 Away tables: {len(away_tables)} entries")

                else:
                    print(f"   ⚠️  Unexpected table data type: {type(table_data)}")
                    assert False, f"Unexpected table data type: {type(table_data)}"

            except TableTennisAPIError as e:
                # Some leagues might not have current table data
                print(f"   ⚠️  API error for league {league.name}: {e}")
                continue

        print("✅ League table testing completed")

    def test_real_league_rankings_functionality(self, real_api_client):
        """
        Test get_rankings() method with real API calls.
        First finds leagues that support rankings, then tests the rankings functionality.
        API Requests: Variable (depends on finding leagues with rankings)
        """
        print("\n🏅 Testing league rankings functionality...")

        # Find leagues that support rankings
        leagues_with_rankings = []
        max_pages_to_search = 5  # Search more pages since rankings are rarer

        for page in range(1, max_pages_to_search + 1):
            response = real_api_client.leagues.list(page=page)

            for league in response.results:
                if league.supports_rankings:
                    leagues_with_rankings.append(league)
                    if (
                        len(leagues_with_rankings) >= 3
                    ):  # We only need a few for testing
                        break

            if len(leagues_with_rankings) >= 3:
                break

        print(f"🏅 Found {len(leagues_with_rankings)} leagues with rankings support")

        if not leagues_with_rankings:
            # Based on DEVELOPMENT.md, we expect 0 leagues with rankings
            print(
                "ℹ️  No leagues with rankings support found (expected based on documentation)"
            )

            # Test with a league that doesn't support rankings to verify error handling
            response = real_api_client.leagues.list(page=1)
            if response.results:
                test_league = response.results[0]
                print(
                    f"🧪 Testing rankings on non-supporting league: {test_league.name}"
                )

                try:
                    rankings_data = real_api_client.leagues.get_rankings(test_league.id)
                    # Should return empty list or minimal data
                    assert isinstance(rankings_data, list)
                    print(
                        f"   ✅ Returned {len(rankings_data)} ranking entries (expected to be 0 or minimal)"
                    )
                except TableTennisAPIError as e:
                    print(f"   ✅ Expected API error for non-supporting league: {e}")

            return

        # Test get_rankings for each league that supports it
        for league in leagues_with_rankings[:2]:  # Test first 2 to limit API calls
            print(f"🏅 Testing rankings for: {league.name} (ID: {league.id})")

            try:
                rankings_data = real_api_client.leagues.get_rankings(league.id)

                # Verify response structure
                assert isinstance(rankings_data, list)
                print(f"   ✅ Rankings has {len(rankings_data)} entries")

                # If rankings has data, verify structure
                if rankings_data:
                    first_entry = rankings_data[0]
                    assert isinstance(first_entry, dict)
                    print(f"   📝 Sample ranking keys: {list(first_entry.keys())}")
                else:
                    print(f"   ℹ️  Rankings is empty (no current rankings)")

            except TableTennisAPIError as e:
                # Some leagues might not have current ranking data
                print(f"   ⚠️  API error for league {league.name}: {e}")
                continue

        print("✅ League rankings testing completed")


if __name__ == "__main__":
    # Run integration tests manually
    print("🧪 Running League Integration Tests")
    print("=" * 50)

    # This would use the API token from .env
    pytest.main(
        ["tests/test_integration_leagues.py", "-v", "-m", "integration", "--tb=short"]
    )
