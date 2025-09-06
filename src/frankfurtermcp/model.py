from typing import Annotated
from pydantic import BaseModel, Field, HttpUrl, PositiveFloat, PositiveInt
from pydantic_extra_types.currency_code import ISO4217
from datetime import date


class CurrencyConversionResponse(BaseModel):
    """
    Response model for currency conversion.
    """

    from_currency: ISO4217 = Field(
        description="The ISO 4217 code of the currency to convert from."
    )
    to_currency: ISO4217 = Field(
        description="The ISO 4217 code of the currency to convert to."
    )
    amount: PositiveFloat = Field(
        description="The amount (of the source currency) to convert."
    )
    converted_amount: PositiveFloat = Field(
        description="The converted amount (of the target currency)."
    )
    exchange_rate: PositiveFloat = Field(
        description="The exchange rate used for the conversion."
    )
    rate_date: date = Field(
        description="The date, in ISO format, of the exchange rate used for the conversion."
    )


class ResponseMetadata(BaseModel):
    """
    Metadata for MCP response.
    """

    version: Annotated[str, Field(description="The version of the package.")]
    api_url: HttpUrl = (
        Field(description="The URL of the Frankfurter API used for the call."),
    )
    api_status_code: int = Field(
        description="The HTTP status code of the API response."
    )
    api_bytes_downloaded: PositiveInt = Field(
        description="The number of bytes downloaded in the API response."
    )
    api_elapsed_time: PositiveInt = Field(
        description="The elapsed time for the API call in microseconds."
    )
