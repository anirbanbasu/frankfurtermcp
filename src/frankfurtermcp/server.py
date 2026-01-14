import logging
import sys
import threading
from datetime import date
from typing import Annotated

import httpx
import uvicorn
from cachetools import cached
from cachetools.keys import hashkey
from fastmcp import Context, FastMCP
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from pydantic import Field, PositiveFloat
from pydantic_extra_types.currency_code import ISO4217
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from frankfurtermcp import EnvVar, lru_cache, ttl_cache
from frankfurtermcp.common import AppMetadata
from frankfurtermcp.middleware import RequestSizeLimitMiddleware, StripUnknownArgumentsMiddleware
from frankfurtermcp.mixin import HTTPHelperMixin, MCPMixin
from frankfurtermcp.model import CurrencyConversionResponse

logger = logging.getLogger(__name__)


class FrankfurterMCP(MCPMixin, HTTPHelperMixin):
    """A FastMCP application that provides currency exchange rate functionalities using the Frankfurter API."""

    tools = [
        {
            "fn": "get_supported_currencies",
            "tags": ["currency-rates", "supported-currencies"],
            "annotations": {
                "readOnlyHint": True,
                "openWorldHint": True,
            },
        },
        {
            "fn": "get_latest_exchange_rates",
            "tags": ["currency-rates", "exchange-rates"],
            "annotations": {
                "readOnlyHint": True,
                "openWorldHint": True,
            },
        },
        {
            "fn": "convert_currency_latest",
            "tags": ["currency-rates", "currency-conversion"],
            "annotations": {
                "readOnlyHint": True,
                "openWorldHint": True,
            },
        },
        {
            "fn": "get_historical_exchange_rates",
            "tags": ["currency-rates", "historical-exchange-rates"],
            "annotations": {
                "readOnlyHint": True,
                "openWorldHint": True,
            },
        },
        {
            "fn": "convert_currency_specific_date",
            "tags": [
                "currency-rates",
                "currency-conversion",
                "historical-exchange-rates",
            ],
            "annotations": {
                "readOnlyHint": True,
                "openWorldHint": True,
            },
        },
        {
            "fn": "greet",
            "tags": ["greet", "hello-world"],
            "annotations": {
                "readOnlyHint": True,
                "openWorldHint": True,
            },
        },
    ]

    async def get_supported_currencies(self, ctx: Context):
        """Returns a list of three-letter currency codes for the supported currencies."""
        try:
            with self.get_httpx_client() as client:
                await ctx.info(f"Fetching supported currencies from Frankfurter API at {self.frankfurter_api_url}")
                http_response = client.get(f"{self.frankfurter_api_url}/currencies")
                http_response.raise_for_status()
                # Note: The following line could easily be result = http_response.json() but we use content.decode() to
                # demonstrate the TextContent wrapping capability of the get_response_content utility method.
                # Questionable choice? Should we just use # pragma: no cover in the respective branch of get_response_content?
                result = http_response.content.decode()
                return self.get_response_content(response=result, http_response=http_response)
        except httpx.RequestError as e:
            raise ValueError(f"Failed to fetch supported currencies from {self.frankfurter_api_url}. {e}")

    @cached(
        cache=ttl_cache,
        lock=threading.Lock(),
        key=hashkey,
    )
    def _get_latest_exchange_rates(
        self,
        base_currency: str | None = None,
        symbols: tuple[str, ...] | None = None,
    ):
        """Internal function to get the latest exchange rates. This is a helper function for the main tool."""
        try:
            params = {}
            if base_currency:
                params["base"] = base_currency
            if symbols:
                params["symbols"] = ",".join(symbols)
            with self.get_httpx_client() as client:
                http_response = client.get(
                    f"{self.frankfurter_api_url}/latest",
                    params=params,
                )
                http_response.raise_for_status()
                result = http_response.json()
                return result, http_response
        except httpx.RequestError as e:
            raise ValueError(f"Failed to fetch latest exchange rates from {self.frankfurter_api_url}. {e}")

    @cached(cache=lru_cache, lock=threading.Lock(), key=hashkey)
    def _get_historical_exchange_rates(
        self,
        specific_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        base_currency: str | None = None,
        symbols: tuple[str, ...] | None = None,
    ):
        """Internal function to get historical exchange rates. This is a helper function for the main tool."""
        try:
            params = {}
            if base_currency:
                params["base"] = base_currency
            if symbols:
                params["symbols"] = ",".join(symbols)

            frankfurter_url = self.frankfurter_api_url
            if start_date and end_date:
                frankfurter_url += f"/{start_date}..{end_date}"
            elif start_date:
                # If only start_date is provided, we assume the end date is the latest available date
                frankfurter_url += f"/{start_date}.."
            elif specific_date:
                # If only specific_date is provided, we assume it is the date for which we want the rates
                frankfurter_url += f"/{specific_date}"
            else:
                raise ValueError("You must provide either a specific date, a start date, or a date range.")

            with self.get_httpx_client() as client:
                http_response = client.get(
                    frankfurter_url,
                    params=params,
                )
                http_response.raise_for_status()
                result = http_response.json()
                return result, http_response
        except httpx.RequestError as e:
            raise ValueError(f"Failed to fetch historical exchange rates from {self.frankfurter_api_url}. {e}")

    async def get_latest_exchange_rates(
        self,
        ctx: Context,
        base_currency: Annotated[
            ISO4217,
            Field(description="A base currency ISO4217 code for which rates are to be requested."),
        ],
        symbols: Annotated[
            list[ISO4217] | ISO4217 | None,
            Field(
                description="A list of target currency ISO4217 codes for which rates against the base currency will be provided. If not provided, all supported currencies will be shown."
            ),
        ] = None,
    ):
        """Returns the latest exchange rates for specific currencies.

        The symbols can be used to filter the results to specific currencies.
        If symbols is not provided, all supported currencies will be returned.
        """
        # Some LLMs make this mistake of passing just one currency but not as a list!
        if type(symbols) is str:
            symbols = [symbols]
        await ctx.info(f"Fetching latest exchange rates from Frankfurter API at {self.frankfurter_api_url}")
        cache_key = hashkey(
            self,
            base_currency=base_currency,
            symbols=tuple(symbols) if symbols else None,
        )
        cache_hit = cache_key in ttl_cache
        result, http_response = self._get_latest_exchange_rates(
            base_currency=base_currency,
            symbols=tuple(symbols) if symbols else None,
        )
        if cache_hit:
            await ctx.info("Latest exchange rates fetched from TTL cache.")
        return self.get_response_content(response=result, http_response=http_response, cached_response=cache_hit)

    async def convert_currency_latest(
        self,
        ctx: Context,
        amount: Annotated[
            PositiveFloat,
            Field(description="The amount in the source currency to convert."),
        ],
        from_currency: Annotated[ISO4217, Field(description="The source currency ISO4217 code.")],
        to_currency: Annotated[ISO4217, Field(description="The target currency ISO4217 code.")],
    ):
        """Converts an amount from one currency to another using the latest exchange rates."""
        if from_currency.lower() == to_currency.lower():
            # If the source and target currencies are the same, no conversion is needed
            raise ValueError(
                f"Source currency '{from_currency}' and target currency '{to_currency}' are the same. No conversion needed."
            )
        await ctx.info(
            f"Obtaining latest exchange rates for {from_currency} to {to_currency} from Frankfurter API at {self.frankfurter_api_url}"
        )
        cache_key = hashkey(
            self,
            base_currency=from_currency,
            symbols=tuple([to_currency]),
        )
        cache_hit = cache_key in ttl_cache
        latest_rates, http_response = self._get_latest_exchange_rates(
            base_currency=from_currency,
            symbols=tuple([to_currency]),
        )
        if cache_hit:
            await ctx.info("Latest exchange rates fetched from TTL cache.")
        await ctx.info(f"Converting {amount} of {from_currency} to {to_currency}")
        if not latest_rates or "rates" not in latest_rates:  # pragma: no cover
            raise ValueError(f"Could not retrieve exchange rates for {from_currency} to {to_currency}.")
        rate = latest_rates["rates"].get(to_currency)
        if rate is None:  # pragma: no cover
            raise ValueError(f"Exchange rate for {from_currency} to {to_currency} not found.")
        converted_amount = amount * float(rate)
        result = CurrencyConversionResponse(
            from_currency=from_currency,
            to_currency=to_currency,
            amount=amount,
            converted_amount=converted_amount,
            exchange_rate=rate,
            rate_date=latest_rates["date"],
        )
        return self.get_response_content(response=result, http_response=http_response, cached_response=cache_hit)

    async def get_historical_exchange_rates(
        self,
        ctx: Context,
        base_currency: Annotated[
            ISO4217,
            Field(description="A base currency ISO4217 code for which rates are to be requested."),
        ],
        symbols: Annotated[
            list[ISO4217] | ISO4217 | None,
            Field(
                description="A list of target currency ISO4217 codes for which rates against the base currency will be provided. If not provided, all supported currencies will be shown."
            ),
        ] = None,
        specific_date: Annotated[
            date | None,
            Field(
                default=None,
                description="The specific date for which the historical rates are requested in the YYYY-MM-DD format.",
            ),
        ] = None,
        start_date: Annotated[
            date | None,
            Field(
                default=None,
                description="The start date, of a date range, for which the historical rates are requested in the YYYY-MM-DD format.",
            ),
        ] = None,
        end_date: Annotated[
            date | None,
            Field(
                default=None,
                description="The end date, of a date range, for which the historical rates are requested in the YYYY-MM-DD format.",
            ),
        ] = None,
    ):
        """Returns historical exchange rates for a specific date or date range.

        If the exchange rates for a specified date is not available, the rates available for
        the closest date before the specified date will be provided.
        Either a specific date, a start date, or a date range must be provided.
        The symbols can be used to filter the results to specific currencies.
        If symbols are not provided, all supported currencies will be returned.
        """
        await ctx.info(f"Fetching historical exchange rates from Frankfurter API at {self.frankfurter_api_url}")
        # Some LLMs make this mistake of passing just one currency but not as a list!
        if type(symbols) is str:
            symbols = [symbols]
        cache_key = hashkey(
            self,
            specific_date=specific_date.isoformat() if specific_date else None,
            start_date=start_date.isoformat() if start_date else None,
            end_date=end_date.isoformat() if end_date else None,
            base_currency=base_currency,
            symbols=tuple(symbols) if symbols else None,
        )
        cache_hit = cache_key in lru_cache
        result, http_response = self._get_historical_exchange_rates(
            specific_date=specific_date.isoformat() if specific_date else None,
            start_date=start_date.isoformat() if start_date else None,
            end_date=end_date.isoformat() if end_date else None,
            base_currency=base_currency,
            symbols=tuple(symbols) if symbols else None,
        )
        if cache_hit:
            await ctx.info(
                f"Historical exchange rates fetched for {len(result.get('rates', []))} dates from least-recently used (LRU) cache."
            )
        else:
            await ctx.info(f"Historical exchange rates fetched for {len(result.get('rates', []))} dates.")
        return self.get_response_content(response=result, http_response=http_response, cached_response=cache_hit)

    async def convert_currency_specific_date(
        self,
        ctx: Context,
        amount: Annotated[
            PositiveFloat,
            Field(description="The amount in the source currency to convert."),
        ],
        from_currency: Annotated[ISO4217, Field(description="The source currency ISO4217 code.")],
        to_currency: Annotated[ISO4217, Field(description="The target currency ISO4217 code.")],
        specific_date: Annotated[
            date,
            Field(description="The specific date for which the conversion is requested in the YYYY-MM-DD format."),
        ],
    ):
        """Convert an amount from one currency to another using the exchange rates for a specific date.

        If there is no exchange rate available for the specific date, the rate for the closest available date before
        the specified date will be used.
        """
        if from_currency.lower() == to_currency.lower():
            # If the source and target currencies are the same, no conversion is needed
            raise ValueError(
                f"Source currency '{from_currency}' and target currency '{to_currency}' are the same. No conversion needed."
            )
        await ctx.info(
            f"Obtaining historical exchange rates for {from_currency} to {to_currency} on {specific_date} from Frankfurter API at {self.frankfurter_api_url}"
        )
        cache_key = hashkey(
            self,
            specific_date=specific_date.isoformat(),
            base_currency=from_currency,
            symbols=tuple([to_currency]),
        )
        cache_hit = cache_key in lru_cache
        date_specific_rates, http_response = self._get_historical_exchange_rates(
            specific_date=specific_date.isoformat(),
            base_currency=from_currency,
            symbols=tuple([to_currency]),
        )
        if cache_hit:
            await ctx.info(
                f"Retrieved historical exchange rates for {specific_date} from least-recently used (LRU) cache."
            )
        await ctx.info(f"Converting {amount} of {from_currency} to {to_currency} on {specific_date}")
        if not date_specific_rates or "rates" not in date_specific_rates:
            raise ValueError(  # pragma: no cover
                f"Could not retrieve exchange rates for {from_currency} to {to_currency} for {specific_date}."
            )
        rate = date_specific_rates["rates"].get(to_currency)
        if rate is None:  # pragma: no cover
            raise ValueError(f"Exchange rate for {from_currency} to {to_currency} not found.")
        converted_amount = amount * float(rate)
        result = CurrencyConversionResponse(
            from_currency=from_currency,
            to_currency=to_currency,
            amount=amount,
            converted_amount=converted_amount,
            exchange_rate=rate,
            rate_date=date_specific_rates["date"],
        )
        return self.get_response_content(response=result, http_response=http_response, cached_response=cache_hit)

    async def greet(
        self,
        ctx: Context,
        name: str | None = None,
    ):
        """A simple greeting tool to demonstrate middleware functionality."""
        greeting_name = name if name else "World"
        greeting_message = f"Hello, {greeting_name} from Frankfurter MCP!"
        await ctx.info(f"Greeting generated: {greeting_message}")
        return self.get_response_content(response=greeting_message)


def app() -> FastMCP:
    """Create and configure the FastMCP application for the Frankfurter MCP server."""
    app = FastMCP(
        name=AppMetadata.package_metadata["Name"],
        instructions=AppMetadata.package_metadata["Summary"],
        version=AppMetadata.package_metadata["Version"],
        website_url=AppMetadata.PROJECT_URL,
        on_duplicate_prompts="error",
        on_duplicate_resources="error",
        on_duplicate_tools="error",
    )
    mcp_obj = FrankfurterMCP()
    app_with_features = mcp_obj.register_features(app)
    app_with_features.add_middleware(StripUnknownArgumentsMiddleware())
    # Token bucket rate limiting (allows controlled bursts)
    app_with_features.add_middleware(
        RateLimitingMiddleware(
            max_requests_per_second=EnvVar.RATE_LIMIT_MAX_REQUESTS_PER_SECOND,
            burst_capacity=EnvVar.RATE_LIMIT_BURST_CAPACITY,
        )
    )
    return app_with_features


def main():  # pragma: no cover
    """Main entry point for running the Frankfurter MCP server."""
    try:
        mcp_app = app()
        transport_type = EnvVar.MCP_SERVER_TRANSPORT
        if transport_type != "stdio":
            middleware = [
                Middleware(
                    RequestSizeLimitMiddleware,
                    max_body_size=EnvVar.REQUEST_SIZE_LIMIT_BYTES,
                ),
                # Configure CORS for browser-based clients, see: https://gofastmcp.com/deployment/http#cors-for-browser-based-clients
                Middleware(
                    CORSMiddleware,
                    allow_origins=EnvVar.CORS_MIDDLEWARE_ALLOW_ORIGINS,
                    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
                    allow_headers=[
                        "mcp-protocol-version",
                        "mcp-session-id",
                        "Authorization",
                        "Content-Type",
                    ],
                    expose_headers=["mcp-session-id"],
                ),
            ]

            asgi_app = mcp_app.http_app(middleware=middleware, transport=transport_type)
            if EnvVar.FASTMCP_HOST == "0.0.0.0":
                logger.warning(
                    "The server is configured to listen on all IPs ('0.0.0.0'), which may expose it to external network traffic. "
                    "This is not recommended for production deployments due to security risks. "
                    "Should you need to expose the server to external traffic, consider using a reverse proxy with proper security measures in place."
                )
            if "*" in EnvVar.CORS_MIDDLEWARE_ALLOW_ORIGINS:
                logger.warning(
                    "Cross-Origin Resource Sharing (CORS) allowed origins contains '*', which allows requests from any origin. "
                    "This is not recommended for production deployments due to security risks. "
                    "To learn more about CORS, see: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS."
                )
            logger.info(
                f"Starting server with Cross-Origin Resource Sharing (CORS) allowed origins: {', '.join(EnvVar.CORS_MIDDLEWARE_ALLOW_ORIGINS)}"
            )
            logger.info(
                f"Server limits: max_concurrency={EnvVar.UVICORN_LIMIT_CONCURRENCY}, "
                f"max_requests={EnvVar.UVICORN_LIMIT_MAX_REQUESTS}, "
                f"keep_alive_timeout={EnvVar.UVICORN_TIMEOUT_KEEP_ALIVE}s"
            )
            uvicorn.run(
                asgi_app,
                host=EnvVar.FASTMCP_HOST,
                port=EnvVar.FASTMCP_PORT,
                timeout_graceful_shutdown=EnvVar.UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN,
                limit_concurrency=EnvVar.UVICORN_LIMIT_CONCURRENCY,
                limit_max_requests=EnvVar.UVICORN_LIMIT_MAX_REQUESTS,
                timeout_keep_alive=EnvVar.UVICORN_TIMEOUT_KEEP_ALIVE,
            )
        else:
            mcp_app.run(transport=transport_type)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    finally:
        # Cleanup if necessary
        pass


if __name__ == "__main__":
    main()  # pragma: no cover
