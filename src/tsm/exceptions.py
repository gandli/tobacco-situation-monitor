"""Custom exceptions for TSM.

Provides domain-specific exception classes for better error handling.
"""


class TSMError(Exception):
    """Base exception for all TSM errors."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize TSM error.

        Args:
            message: Human-readable error message.
            details: Optional dictionary with additional error details.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DatabaseError(TSMError):
    """Database operation failed."""

    pass


class ConfigurationError(TSMError):
    """Invalid or missing configuration."""

    pass


class ValidationError(TSMError):
    """Data validation failed."""

    pass


class ExtractionError(TSMError):
    """Entity or region extraction failed."""

    pass


class CrawlerError(TSMError):
    """Web crawling operation failed."""

    pass


class APIError(TSMError):
    """API operation failed."""

    pass


class DuplicateError(TSMError):
    """Duplicate data detected."""

    pass


class NotFoundError(TSMError):
    """Requested resource not found."""

    pass


class AuthenticationError(TSMError):
    """Authentication failed."""

    pass


class AuthorizationError(TSMError):
    """Authorization failed - insufficient permissions."""

    pass
