import json
import asyncio
import logging
from fastmcp import Client, FastMCP

from frankfurtermcp.server import FrankfurterMCP
import pytest

logger = logging.getLogger(__name__)


class TestMCPServer:
    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    def mcp_server(cls):
        """
        Fixture to register features in an MCP server.
        """
        server = FastMCP()
        mcp_obj = FrankfurterMCP()
        server_with_features = mcp_obj.register_features(server)
        return server_with_features

    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    def mcp_client(cls, mcp_server):
        """
        Fixture to create a client for the MCP server.
        """
        mcp_client = Client(
            transport=mcp_server,
            timeout=60,
        )
        return mcp_client

    async def call_tool(self, tool_name: str, mcp_client: Client, **kwargs):
        """
        Helper method to call a tool on the MCP server.
        """
        logger.debug(f"Calling tool '{tool_name}' with arguments: {kwargs}")
        async with mcp_client:
            result = await mcp_client.call_tool(tool_name, arguments=kwargs)
            await mcp_client.close()
        logger.debug(f"Tool '{tool_name}' returned result: {result}")
        return result

    def test_get_supported_currencies(self, mcp_client):
        """
        Test the get_supported_currencies function to ensure it returns a list of supported currencies.
        """
        test_method = "get_supported_currencies"
        response = asyncio.run(
            self.call_tool(
                tool_name=test_method,
                mcp_client=mcp_client,
            )
        )
        json_result: dict = json.loads(response.content[0].text)
        assert len(json_result.keys()) > 0, "Expected non-empty list of currencies"
        assert all(
            (isinstance(code, str) and len(code) == 3) for code in json_result.keys()
        ), "All currency codes should be 3-character strings"

    def test_convert_currency_latest(self, mcp_client):
        """
        Test the convert_currency_latest function to ensure it returns a list of supported currencies.
        """
        test_method = "convert_currency_latest"
        response = asyncio.run(
            self.call_tool(
                tool_name=test_method,
                mcp_client=mcp_client,
                from_currency="GBP",
                to_currency="JPY",
                amount=100.0,
            )
        )
        json_result: dict = json.loads(response.content[0].text)
        logger.info(f"{test_method} response: {json_result}")
        assert isinstance(json_result["converted_amount"], float), (
            "Expected float value for converted amount"
        )
        assert json_result["converted_amount"] > 100.0, (
            "The exchange rate for GBP to JPY should be greater than 1.0"
        )

    def test_get_latest_exchange_rates(self, mcp_client):
        """
        Test the get_latest_exchange_rates function to ensure that it returns the list of latest rates with other currencies.
        """
        test_method = "get_latest_exchange_rates"
        response = asyncio.run(
            self.call_tool(
                tool_name=test_method,
                mcp_client=mcp_client,
                base_currency="JPY",
                symbols=["EUR", "GBP", "CHF", "NZD"],
            )
        )
        json_result: dict = json.loads(response.content[0].text)
        assert len(json_result["rates"].keys()) > 0, (
            "Expected non-empty list of currency rates"
        )
        assert all(
            (isinstance(code, str) and len(code) == 3)
            for code in json_result["rates"].keys()
        ), "All currency codes for exchange rates should be 3-character strings"

    def test_get_historical_exchange_rates(self, mcp_client):
        """
        Test the get_historical_exchange_rates function to ensure that it returns the list of historical rates with other currencies.
        """
        test_method = "get_historical_exchange_rates"
        response = asyncio.run(
            self.call_tool(
                tool_name=test_method,
                mcp_client=mcp_client,
                base_currency="JPY",
                start_date="2025-06-01",
                end_date="2025-06-19",
                symbols=["EUR", "GBP", "CHF", "NZD"],
            )
        )
        json_result: dict = json.loads(response.content[0].text)
        assert all(
            len(rates_for_date) > 0
            for _, rates_for_date in json_result["rates"].items()
        ), "Expected non-empty list of currency rates"
        assert all(
            (
                (isinstance(code, str) and len(code) == 3)
                for code in rates_for_date.keys()
            )
            for _, rates_for_date in json_result["rates"].items()
        ), "All currency codes for exchange rates should be 3-character strings"

    def test_get_latest_exchange_rates_for_single_currency(self, mcp_client):
        """
        Test the get_latest_exchange_rates function to ensure that it returns the latest rates for a single currency.
        """
        test_method = "get_latest_exchange_rates"
        response = asyncio.run(
            self.call_tool(
                tool_name=test_method,
                mcp_client=mcp_client,
                base_currency="JPY",
                symbols="GBP",
            )
        )
        json_result: dict = json.loads(response.content[0].text)
        assert len(json_result["rates"].keys()) > 0, (
            "Expected non-empty list of currency rates"
        )
        assert all(
            (isinstance(code, str) and len(code) == 3)
            for code in json_result["rates"].keys()
        ), "All currency codes for exchange rates should be 3-character strings"

    def test_get_historical_exchange_rates_for_a_single_currency(self, mcp_client):
        """
        Test the get_historical_exchange_rates function to ensure that it returns the historical rates for a single currency.
        """
        test_method = "get_historical_exchange_rates"
        response = asyncio.run(
            self.call_tool(
                tool_name=test_method,
                mcp_client=mcp_client,
                base_currency="JPY",
                start_date="2025-06-01",
                end_date="2025-06-19",
                symbols=["EUR", "GBP", "CHF", "NZD"],
            )
        )
        json_result: dict = json.loads(response.content[0].text)
        assert all(
            len(rates_for_date) > 0
            for _, rates_for_date in json_result["rates"].items()
        ), "Expected non-empty list of currency rates"
        assert all(
            (
                (isinstance(code, str) and len(code) == 3)
                for code in rates_for_date.keys()
            )
            for _, rates_for_date in json_result["rates"].items()
        ), "All currency codes for exchange rates should be 3-character strings"

    def test_convert_currency_specific_date(self, mcp_client):
        """
        Test the convert_currency_specific_date function to ensure it returns a list of supported currencies.
        """
        test_method = "convert_currency_specific_date"
        response = asyncio.run(
            self.call_tool(
                tool_name=test_method,
                mcp_client=mcp_client,
                from_currency="GBP",
                to_currency="JPY",
                amount=100.0,
                specific_date="2025-06-01",
            )
        )
        json_result: dict = json.loads(response.content[0].text)
        print(f"{test_method} response: {json_result}")
        assert isinstance(json_result["converted_amount"], float), (
            "Expected float value for converted amount"
        )
        assert json_result["converted_amount"] > 100.0, (
            "The exchange rate for GBP to JPY should be greater than 1.0"
        )
