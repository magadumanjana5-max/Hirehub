"""Custom exceptions for the HireHub application."""


class HireHubError(Exception):
    """Base application exception."""


class UserExistsError(HireHubError):
    """Raised when a user already exists."""


class ValidationError(HireHubError):
    """Raised for invalid request data."""
