from importlib.metadata import metadata


class AppMetadata:
    """Metadata for the application."""

    PACKAGE_NAME = "frankfurtermcp"
    TEXT_CONTENT_META_PREFIX = f"{PACKAGE_NAME}."
    PROJECT_URL = "https://github.com/anirbanbasu/frankfurtermcp"
    package_metadata = metadata(PACKAGE_NAME)
