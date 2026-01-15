import logging

from cachetools import LRUCache, TTLCache
from environs import Env
from marshmallow.validate import OneOf, Range
from rich.logging import RichHandler

env = Env()
env.read_env()


class EnvVar:
    """Environment variables for configuring the Frankfurter MCP server."""

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
    MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE = env.bool("MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE", default=True)
    FRANKFURTER_API_URL = env.str("FRANKFURTER_API_URL", default="https://api.frankfurter.dev/v1")
    HTTPX_TIMEOUT = env.float(
        "HTTPX_TIMEOUT",
        default=5.0,
        validate=Range(min=5.0, max=60.0),
    )
    HTTPX_VERIFY_SSL = env.bool("HTTPX_VERIFY_SSL", default=True)

    LRU_CACHE_MAX_SIZE = env.int(
        "LRU_CACHE_MAX_SIZE",
        default=1024,
        validate=Range(min=128, max=65536),
    )
    TTL_CACHE_MAX_SIZE = env.int(
        "TTL_CACHE_MAX_SIZE",
        default=256,
        validate=Range(min=64, max=16384),
    )
    TTL_CACHE_TTL_SECONDS = env.int(
        "TTL_CACHE_TTL_SECONDS",
        default=900,
        validate=Range(min=60, max=3600),
    )

    CORS_MIDDLEWARE_ALLOW_ORIGINS = env.list("CORS_MIDDLEWARE_ALLOW_ORIGINS", default=["localhost", "127.0.0.1"])

    # Uvicorn server limits
    UVICORN_LIMIT_CONCURRENCY = env.int("UVICORN_LIMIT_CONCURRENCY", default=100, validate=Range(min=10, max=10000))
    # UVICORN_LIMIT_MAX_REQUESTS = env.int(
    #     "UVICORN_LIMIT_MAX_REQUESTS",
    #     default=10000,
    #     validate=Range(min=1000, max=1000000),
    # )
    UVICORN_TIMEOUT_KEEP_ALIVE = env.int(
        "UVICORN_TIMEOUT_KEEP_ALIVE",
        default=60,
        validate=Range(min=60, max=300),
    )
    UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN = env.int(
        "UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN",
        default=5,
        validate=Range(min=5, max=60),
    )

    # Rate limiting
    RATE_LIMIT_MAX_REQUESTS_PER_SECOND = env.float(
        "RATE_LIMIT_MAX_REQUESTS_PER_SECOND",
        default=10.0,
        validate=Range(min=1.0, max=10000.0),
    )
    RATE_LIMIT_BURST_CAPACITY = env.int(
        "RATE_LIMIT_BURST_CAPACITY",
        default=int(2 * RATE_LIMIT_MAX_REQUESTS_PER_SECOND),
        validate=Range(
            min=int(2 * RATE_LIMIT_MAX_REQUESTS_PER_SECOND), max=int(5 * RATE_LIMIT_MAX_REQUESTS_PER_SECOND)
        ),
    )

    # Request size limit
    REQUEST_SIZE_LIMIT_BYTES = env.int(
        "REQUEST_SIZE_LIMIT_BYTES",
        default=100 * 1024,
        validate=Range(min=10 * 1024, max=512 * 1024),
    )  # 100KB default


logging.basicConfig(
    level=EnvVar.LOG_LEVEL,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=False, markup=True, show_path=False, show_time=False)],
)

ttl_cache = TTLCache(EnvVar.TTL_CACHE_MAX_SIZE, EnvVar.TTL_CACHE_TTL_SECONDS)
lru_cache = LRUCache(EnvVar.LRU_CACHE_MAX_SIZE)
