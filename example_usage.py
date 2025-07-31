#!/usr/bin/env python3
"""
Example usage of the Table Tennis API library.
Shows basic usage patterns for the league functionality.
"""

import os
from dotenv import load_dotenv
from tabletennis_api import TableTennisAPI

# Load environment variables
load_dotenv()

def main():
    """Example usage of the Table Tennis API"""
    
    # Initialize the API client
    api_token = os.getenv("B365_API_TOKEN")
    if not api_token or api_token == "your-api-token-here":
        print("Please set your B365_API_TOKEN in the .env file")
        return
    
    api = TableTennisAPI(api_key=api_token)
    
    # Example 1: Get leagues with pagination
    print("Example 1: Getting first page of leagues")
    response = api.leagues.list()
    print(f"Total leagues: {response.pagination.total}")
    print(f"Leagues on this page: {len(response.results)}")
    
    # Example 2: Find WTT tournaments
    print("\nExample 2: Finding WTT tournaments")
    wtt_leagues = [league for league in response.results 
                   if "WTT" in league.name]
    print(f"Found {len(wtt_leagues)} WTT tournaments:")
    for league in wtt_leagues[:5]:
        print(f"  - {league.name}")
    
    # Example 3: Get leagues by country
    print("\nExample 3: Getting Czech Republic leagues")
    cz_leagues = api.leagues.list(country_code="cz")
    print(f"Czech leagues: {len(cz_leagues.results)}")
    for league in cz_leagues.results:
        print(f"  - {league.name}")
    
    # Example 4: Check which leagues support standings
    print("\nExample 4: Leagues with standings support")
    leagues_with_standings = [l for l in response.results 
                            if l.supports_standings]
    print(f"Leagues with standings: {len(leagues_with_standings)}")
    
    # Example 5: Rate limit monitoring
    print(f"\nRate limit: {api.rate_limit_remaining} requests remaining")

if __name__ == "__main__":
    main()