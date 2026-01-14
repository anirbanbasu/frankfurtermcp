import logging

from cachetools import LRUCache, TTLCache
from environs import Env
from marshmallow.validate import OneOf
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
    HTTPX_TIMEOUT = env.float("HTTPX_TIMEOUT", default=5.0)
    HTTPX_VERIFY_SSL = env.bool("HTTPX_VERIFY_SSL", default=True)

    LRU_CACHE_MAX_SIZE = env.int("LRU_CACHE_MAX_SIZE", default=1024)
    TTL_CACHE_MAX_SIZE = env.int("TTL_CACHE_MAX_SIZE", default=256)
    TTL_CACHE_TTL_SECONDS = env.int("TTL_CACHE_TTL_SECONDS", default=900)

    CORS_MIDDLEWARE_ALLOW_ORIGINS = env.list("CORS_MIDDLEWARE_ALLOW_ORIGINS", default=["localhost", "127.0.0.1"])

    # Uvicorn server limits
    UVICORN_LIMIT_CONCURRENCY = env.int("UVICORN_LIMIT_CONCURRENCY", default=100)
    UVICORN_LIMIT_MAX_REQUESTS = env.int("UVICORN_LIMIT_MAX_REQUESTS", default=10000)
    UVICORN_TIMEOUT_KEEP_ALIVE = env.int("UVICORN_TIMEOUT_KEEP_ALIVE", default=60)
    UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN = env.int("UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN", default=5)

    # Rate limiting
    RATE_LIMIT_MAX_REQUESTS_PER_SECOND = env.float("RATE_LIMIT_MAX_REQUESTS_PER_SECOND", default=10.0)
    RATE_LIMIT_BURST_CAPACITY = env.int("RATE_LIMIT_BURST_CAPACITY", default=20)

    # Request size limit
    REQUEST_SIZE_LIMIT_BYTES = env.int("REQUEST_SIZE_LIMIT_BYTES", default=102400)  # 100KB default


logging.basicConfig(
    level=EnvVar.LOG_LEVEL,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=False, markup=True, show_path=False, show_time=False)],
)

ttl_cache = TTLCache(EnvVar.TTL_CACHE_MAX_SIZE, EnvVar.TTL_CACHE_TTL_SECONDS)
lru_cache = LRUCache(EnvVar.LRU_CACHE_MAX_SIZE)
