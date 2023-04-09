"""Exceptions used by Nexxtmove."""


class NexxtmoveException(Exception):
    """Base class for all exceptions raised by Nexxtmove."""

    pass


class NexxtmoveServiceException(Exception):
    """Raised when service is not available."""

    pass


class BadCredentialsException(Exception):
    """Raised when credentials are incorrect."""

    pass


class NotAuthenticatedException(Exception):
    """Raised when session is invalid."""

    pass


class GatewayTimeoutException(NexxtmoveServiceException):
    """Raised when server times out."""

    pass


class BadGatewayException(NexxtmoveServiceException):
    """Raised when server returns Bad Gateway."""

    pass
