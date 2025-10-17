from importlib.metadata import metadata


class AppMetadata:
    """
    Metadata for the application.
    """

    PACKAGE_NAME = "frankfurtermcp"
    TEXT_CONTENT_META_PREFIX = f"{PACKAGE_NAME}."
    package_metadata = metadata(PACKAGE_NAME)
