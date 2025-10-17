import logging
from environs import Env
from rich.logging import RichHandler

from marshmallow.validate import OneOf


try:
    from icecream import ic

    ic.configureOutput(includeContext=True)
except ImportError:  # pragma: no cover
    # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


env = Env()
env.read_env()


class EnvVar:
    LOG_LEVEL = env.str(
        "LOG_LEVEL",
        default="INFO",
        validate=OneOf(["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    ).upper()
    FASTMCP_HOST = env.str("FASTMCP_HOST", default="localhost")
    FASTMCP_PORT = env.int("FASTMCP_PORT", default=8000)
    MCP_SERVER_TRANSPORT = env.str(
        "MCP_SERVER_TRANSPORT",
        default="stdio",
        validate=OneOf(["stdio", "sse", "streamable-http", "http"]),
    )
    MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE = env.bool(
        "MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE", default=True
    )
    FRANKFURTER_API_URL = env.str(
        "FRANKFURTER_API_URL", default="https://api.frankfurter.dev/v1"
    )
    HTTPX_TIMEOUT = env.float("HTTPX_TIMEOUT", default=5.0)
    HTTPX_VERIFY_SSL = env.bool("HTTPX_VERIFY_SSL", default=True)

    LRU_CACHE_MAX_SIZE = env.int("LRU_CACHE_MAX_SIZE", default=1024)
    TTL_CACHE_MAX_SIZE = env.int("TTL_CACHE_MAX_SIZE", default=256)
    TTL_CACHE_TTL_SECONDS = env.int("TTL_CACHE_TTL_SECONDS", default=900)


logging.basicConfig(
    level=EnvVar.LOG_LEVEL,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(
            rich_tracebacks=False, markup=True, show_path=False, show_time=False
        )
    ],
)
