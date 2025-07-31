"""Utility functions for Table Tennis API"""

from datetime import date, datetime
from typing import Optional, Union


def format_date(date_input: Union[str, date, datetime]) -> str:
    """
    Format date to ISO format string.

    Args:
        date_input: Date as string, date, or datetime object

    Returns:
        ISO formatted date string (YYYY-MM-DD)
    """
    if isinstance(date_input, str):
        return date_input
    elif isinstance(date_input, datetime):
        return date_input.date().isoformat()
    elif isinstance(date_input, date):
        return date_input.isoformat()
    else:
        raise ValueError(f"Invalid date type: {type(date_input)}")


def parse_american_odds(odds: Union[int, str]) -> float:
    """
    Convert American odds to decimal odds.

    Args:
        odds: American odds as int or string (e.g., -150, +200)

    Returns:
        Decimal odds
    """
    odds_int = int(odds)
    if odds_int > 0:
        return 1 + (odds_int / 100)
    else:
        return 1 + (100 / abs(odds_int))


def calculate_implied_probability(decimal_odds: float) -> float:
    """
    Calculate implied probability from decimal odds.

    Args:
        decimal_odds: Decimal odds

    Returns:
        Implied probability as percentage
    """
    return (1 / decimal_odds) * 100


def normalize_player_name(name: str) -> str:
    """
    Normalize player name for matching.

    Args:
        name: Player name

    Returns:
        Normalized name (lowercase, stripped)
    """
    return name.lower().strip().replace(".", "").replace(",", "")


def parse_score(score_string: str) -> Optional[dict]:
    """
    Parse match score string into structured format.

    Args:
        score_string: Score string (e.g., "3-1 (11-9, 8-11, 11-7, 11-8)")

    Returns:
        Dictionary with match and game scores
    """
    if not score_string:
        return None

    try:
        parts = score_string.split(" (")
        match_score = parts[0].strip()

        result = {"match_score": match_score, "games": []}

        if len(parts) > 1:
            games_str = parts[1].rstrip(")")
            games = games_str.split(", ")
            for game in games:
                scores = game.split("-")
                if len(scores) == 2:
                    result["games"].append(
                        {"player1": int(scores[0]), "player2": int(scores[1])}
                    )

        return result
    except (ValueError, IndexError):
        return None
