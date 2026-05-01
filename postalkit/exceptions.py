class PostalKitError(Exception):
    """Base exception for all PostalKit errors."""

    pass


class InitializationError(PostalKitError):
    """Raised when libpostal fails to initialize (e.g., memory issues, bad data dir)."""

    pass


class DependencyMissingError(PostalKitError):
    """Raised when required binaries or data models cannot be downloaded or found."""

    pass


class ParsingError(PostalKitError):
    """Raised when the C library encounters an error parsing an address."""

    pass
