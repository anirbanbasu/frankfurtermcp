from datetime import date
import logging
import sys
from typing import Annotated, List, Optional, Union
import httpx

from fastmcp import FastMCP, Context

from frankfurtermcp import env
from marshmallow.validate import OneOf

from pydantic import Field, PositiveFloat
from pydantic_extra_types.currency_code import ISO4217
from frankfurtermcp.common import EnvVar

from frankfurtermcp.common import AppMetadata
from frankfurtermcp.mixin import HTTPHelperMixin, MCPMixin
from frankfurtermcp.model import CurrencyConversionResponse

logger = logging.getLogger(__name__)


class FrankfurterMCP(MCPMixin, HTTPHelperMixin):
    """
    A FastMCP application that provides currency exchange rate functionalities
    using the Frankfurter API.
    """

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
    ]

    async def get_supported_currencies(self, ctx: Context):
        """
        Returns a list of three-letter currency codes for the supported currencies.
        """
        try:
            with self.get_httpx_client() as client:
                await ctx.info(
                    f"Fetching supported currencies from Frankfurter API at {self.frankfurter_api_url}"
                )
                http_response = client.get(f"{self.frankfurter_api_url}/currencies")
                http_response.raise_for_status()
                result = http_response.json()
                return self.get_response_text_content(
                    response=result, http_response=http_response
                )
        except httpx.RequestError as e:
            raise ValueError(
                f"Failed to fetch supported currencies from {self.frankfurter_api_url}. {e}"
            )

    def _get_latest_exchange_rates(
        self,
        base_currency: Union[str, None] = None,
        symbols: Union[List[str], None] = None,
    ):
        """
        Internal function to get the latest exchange rates.
        This is a helper function for the main tool.
        """
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
            raise ValueError(
                f"Failed to fetch latest exchange rates from {self.frankfurter_api_url}. {e}"
            )

    def _get_historical_exchange_rates(
        self,
        specific_date: Union[str, None] = None,
        start_date: Union[str, None] = None,
        end_date: Union[str, None] = None,
        base_currency: Union[str, None] = None,
        symbols: Union[List[str], None] = None,
    ):
        """
        Internal function to get historical exchange rates.
        This is a helper function for the main tool.
        """
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
                raise ValueError(
                    "You must provide either a specific date, a start date, or a date range."
                )

            with self.get_httpx_client() as client:
                http_response = client.get(
                    frankfurter_url,
                    params=params,
                )
                http_response.raise_for_status()
                result = http_response.json()
                return result, http_response
        except httpx.RequestError as e:
            raise ValueError(
                f"Failed to fetch historical exchange rates from {self.frankfurter_api_url}. {e}"
            )

    async def get_latest_exchange_rates(
        self,
        ctx: Context,
        base_currency: Annotated[
            ISO4217,
            Field(
                description="A base currency ISO4217 code for which rates are to be requested."
            ),
        ],
        symbols: Annotated[
            Optional[List[ISO4217] | ISO4217],
            Field(
                description="A list of target currency ISO4217 codes for which rates against the base currency will be provided. If not provided, all supported currencies will be shown."
            ),
        ] = None,
    ):
        """
        Returns the latest exchange rates for specific currencies. The
        symbols can be used to filter the results to specific currencies.
        If symbols is not provided, all supported currencies will be returned.
        """
        # Some LLMs make this mistake of passing just one currency but not as a list!
        if type(symbols) is str:
            symbols = [symbols]
        await ctx.info(
            f"Fetching latest exchange rates from Frankfurter API at {self.frankfurter_api_url}"
        )
        result, http_response = self._get_latest_exchange_rates(
            base_currency=base_currency,
            symbols=symbols,
        )
        return self.get_response_text_content(
            response=result, http_response=http_response
        )

    async def convert_currency_latest(
        self,
        ctx: Context,
        amount: Annotated[
            PositiveFloat,
            Field(description="The amount in the source currency to convert."),
        ],
        from_currency: Annotated[
            ISO4217, Field(description="The source currency ISO4217 code.")
        ],
        to_currency: Annotated[
            ISO4217, Field(description="The target currency ISO4217 code.")
        ],
    ):
        """
        Converts an amount from one currency to another using the latest exchange rates.
        """
        if from_currency.lower() == to_currency.lower():
            # If the source and target currencies are the same, no conversion is needed
            raise ValueError(
                f"Source currency '{from_currency}' and target currency '{to_currency}' are the same. No conversion needed."
            )
        await ctx.info(
            f"Obtaining latest exchange rates for {from_currency} to {to_currency} from Frankfurter API at {self.frankfurter_api_url}"
        )
        latest_rates, http_response = self._get_latest_exchange_rates(
            base_currency=from_currency,
            symbols=[to_currency],
        )
        await ctx.info(f"Converting {amount} of {from_currency} to {to_currency}")
        if not latest_rates or "rates" not in latest_rates:
            raise ValueError(
                f"Could not retrieve exchange rates for {from_currency} to {to_currency}."
            )
        rate = latest_rates["rates"].get(to_currency)
        if rate is None:
            raise ValueError(
                f"Exchange rate for {from_currency} to {to_currency} not found."
            )
        converted_amount = amount * float(rate)
        result = CurrencyConversionResponse(
            from_currency=from_currency,
            to_currency=to_currency,
            amount=amount,
            converted_amount=converted_amount,
            exchange_rate=rate,
            rate_date=latest_rates["date"],
        )
        return self.get_response_text_content(
            response=result, http_response=http_response
        )

    async def get_historical_exchange_rates(
        self,
        ctx: Context,
        base_currency: Annotated[
            ISO4217,
            Field(
                description="A base currency ISO4217 code for which rates are to be requested."
            ),
        ],
        symbols: Annotated[
            Optional[List[ISO4217] | ISO4217],
            Field(
                description="A list of target currency ISO4217 codes for which rates against the base currency will be provided. If not provided, all supported currencies will be shown."
            ),
        ] = None,
        specific_date: Annotated[
            Optional[date],
            Field(
                default=None,
                description="The specific date for which the historical rates are requested in the YYYY-MM-DD format.",
            ),
        ] = None,
        start_date: Annotated[
            Optional[date],
            Field(
                default=None,
                description="The start date, of a date range, for which the historical rates are requested in the YYYY-MM-DD format.",
            ),
        ] = None,
        end_date: Annotated[
            Optional[date],
            Field(
                default=None,
                description="The end date, of a date range, for which the historical rates are requested in the YYYY-MM-DD format.",
            ),
        ] = None,
    ):
        """
        Returns historical exchange rates for a specific date or date range.
        If the exchange rates for a specified date is not available, the rates available for
        the closest date before the specified date will be provided.
        Either a specific date, a start date, or a date range must be provided.
        The symbols can be used to filter the results to specific currencies.
        If symbols are not provided, all supported currencies will be returned.
        """
        await ctx.info(
            f"Fetching historical exchange rates from Frankfurter API at {self.frankfurter_api_url}"
        )
        # Some LLMs make this mistake of passing just one currency but not as a list!
        if type(symbols) is str:
            symbols = [symbols]
        result, http_response = self._get_historical_exchange_rates(
            specific_date=specific_date.isoformat() if specific_date else None,
            start_date=start_date.isoformat() if start_date else None,
            end_date=end_date.isoformat() if end_date else None,
            base_currency=base_currency,
            symbols=symbols,
        )
        await ctx.info(
            f"Historical exchange rates fetched for {len(result.get('rates', []))} dates."
        )
        return self.get_response_text_content(
            response=result, http_response=http_response
        )

    async def convert_currency_specific_date(
        self,
        ctx: Context,
        amount: Annotated[
            PositiveFloat,
            Field(description="The amount in the source currency to convert."),
        ],
        from_currency: Annotated[
            ISO4217, Field(description="The source currency ISO4217 code.")
        ],
        to_currency: Annotated[
            ISO4217, Field(description="The target currency ISO4217 code.")
        ],
        specific_date: Annotated[
            date,
            Field(
                description="The specific date for which the conversion is requested in the YYYY-MM-DD format."
            ),
        ],
    ):
        """
        Convert an amount from one currency to another using the exchange rates for a specific date.
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
        date_specific_rates, http_response = self._get_historical_exchange_rates(
            specific_date=specific_date.isoformat(),
            base_currency=from_currency,
            symbols=[to_currency],
        )
        await ctx.info(
            f"Converting {amount} of {from_currency} to {to_currency} on {specific_date}"
        )
        if not date_specific_rates or "rates" not in date_specific_rates:
            raise ValueError(
                f"Could not retrieve exchange rates for {from_currency} to {to_currency} for {specific_date}."
            )
        rate = date_specific_rates["rates"].get(to_currency)
        if rate is None:
            raise ValueError(
                f"Exchange rate for {from_currency} to {to_currency} not found."
            )
        converted_amount = amount * float(rate)
        result = CurrencyConversionResponse(
            from_currency=from_currency,
            to_currency=to_currency,
            amount=amount,
            converted_amount=converted_amount,
            exchange_rate=rate,
            rate_date=date_specific_rates["date"],
        )
        return self.get_response_text_content(
            response=result, http_response=http_response
        )


def app() -> FastMCP:
    app = FastMCP(
        name=AppMetadata.package_metadata["Name"],
        instructions=AppMetadata.package_metadata["Description"],
        on_duplicate_prompts="error",
        on_duplicate_resources="error",
        on_duplicate_tools="error",
    )
    mcp_obj = FrankfurterMCP()
    app_with_features = mcp_obj.register_features(app)
    return app_with_features


def main():  # pragma: no cover
    try:
        mcp_app = app()
        transport_type = env.str(
            name=EnvVar.MCP_SERVER_TRANSPORT,
            default=EnvVar.DEFAULT__MCP_SERVER_TRANSPORT,
            validate=OneOf(EnvVar.ALLOWED__MCP_SERVER_TRANSPORT),
        )
        (
            mcp_app.run(
                transport=transport_type,
                host=env.str(
                    name=EnvVar.FASTMCP_HOST,
                    default=EnvVar.DEFAULT__FASTMCP_HOST,
                ),
                port=env.int(
                    name=EnvVar.FASTMCP_PORT,
                    default=EnvVar.DEFAULT__FASTMCP_PORT,
                ),
                uvicorn_config={
                    "timeout_graceful_shutdown": 5,  # seconds
                },
            )
            if transport_type != "stdio"
            else mcp_app.run(transport=transport_type)
        )
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    finally:
        # Cleanup if necessary
        pass


if __name__ == "__main__":
    main()
