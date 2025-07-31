"""Custom exceptions for Table Tennis API"""


class TableTennisAPIError(Exception):
    """Base exception for Table Tennis API errors"""
    pass


class AuthenticationError(TableTennisAPIError):
    """Raised when authentication fails"""
    pass


class RateLimitError(TableTennisAPIError):
    """Raised when API rate limit is exceeded"""
    pass


class InvalidRequestError(TableTennisAPIError):
    """Raised when request parameters are invalid"""
    pass


class NotFoundError(TableTennisAPIError):
    """Raised when requested resource is not found"""
    pass


class ServerError(TableTennisAPIError):
    """Raised when API server returns a 5xx error"""
    pass