import asyncio
import json
import logging

import pytest
from fastmcp import Client, FastMCP

from frankfurtermcp.common import AppMetadata
from frankfurtermcp.model import ResponseMetadata
from frankfurtermcp.server import FrankfurterMCP, app as frankfurtermcp_app

logger = logging.getLogger(__name__)


class TestMCPServer:
    """Test suite for the Frankfurter MCP server."""

    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def mcp_server(cls):
        """Fixture to register features in an MCP server."""
        server = FastMCP()
        mcp_obj = FrankfurterMCP()
        server_with_features = mcp_obj.register_features(server)
        # We don't really need to test the middleware here since it has its own dedicated tests
        return server_with_features

    @pytest.fixture(scope="class")
    @classmethod
    def mcp_server_bogus_config(cls):
        """Fixture to register features in an MCP server with a bogus configuration."""
        server = FastMCP()
        mcp_obj = FrankfurterMCP()
        mcp_obj.frankfurter_api_url = "http://127.0.0.1:12345/nonexistent_endpoint"
        server_with_features = mcp_obj.register_features(server)
        # We don't care about the middleware for this bogus config test
        return server_with_features

    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def mcp_client(cls, mcp_server):
        """Fixture to create a client for the MCP server."""
        mcp_client = Client(
            transport=mcp_server,
            timeout=60,
        )
        return mcp_client

    @pytest.fixture(scope="class")
    @classmethod
    def mcp_client_bogus_config(cls, mcp_server_bogus_config):
        """Fixture to create a client for the MCP server with a bogus config."""
        mcp_client = Client(
            transport=mcp_server_bogus_config,
            timeout=60,
        )
        return mcp_client

    async def call_tool(self, tool_name: str, mcp_client: Client, **kwargs):
        """Helper method to call a tool on the MCP server."""
        logger.debug(f"Calling tool '{tool_name}' with arguments: {kwargs}")
        async with mcp_client:
            result = await mcp_client.call_tool(tool_name, arguments=kwargs)
            await mcp_client.close()
        logger.debug(f"Tool '{tool_name}' returned result: {result}")
        return result

    def test_app_creation(self):
        """Test the creation of the FastMCP application."""
        mcp_server = frankfurtermcp_app()
        assert isinstance(mcp_server, FastMCP), "Expected mcp_server to be an instance of FastMCP"
        tools_list = asyncio.run(mcp_server.get_tools())
        assert len(tools_list) == 6, (
            f"Expected exactly 6 tools to be registered in the MCP server, got {len(tools_list)}"
        )

    def test_get_supported_currencies(self, mcp_client, mcp_client_bogus_config):
        """Test the get_supported_currencies function to ensure it returns a list of supported currencies."""
        test_method = "get_supported_currencies"
        response = asyncio.run(
            self.call_tool(
                tool_name=test_method,
                mcp_client=mcp_client,
            )
        )
        assert isinstance(response.meta, dict), (
            f"Expected result from MCP tool call, {test_method}, to contain a metadata dictionary"
        )
        try:
            ResponseMetadata.model_validate(response.meta[AppMetadata.PACKAGE_NAME])
        except Exception as e:  # pragma: no cover
            assert False, f"Metadata validation failed with error: {e}"
        json_result: dict = json.loads(response.content[0].text)
        assert len(json_result.keys()) > 0, "Expected non-empty list of currencies"
        assert all((isinstance(code, str) and len(code) == 3) for code in json_result.keys()), (
            "All currency codes should be 3-character strings"
        )

        with pytest.raises(Exception) as exc_info:
            asyncio.run(
                self.call_tool(
                    tool_name=test_method,
                    mcp_client=mcp_client_bogus_config,
                )
            )
        assert "Connection refused" in str(exc_info.value), (
            "Expected exception message to indicate failure to connect to bogus API endpoint"
        )

    def test_convert_currency_latest(self, mcp_client):
        """Test the convert_currency_latest function to ensure it returns a list of supported currencies."""
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
        assert isinstance(response.meta, dict), (
            f"Expected result from MCP tool call, {test_method}, to contain a metadata dictionary"
        )
        try:
            ResponseMetadata.model_validate(response.meta[AppMetadata.PACKAGE_NAME])
        except Exception as e:  # pragma: no cover
            assert False, f"Metadata validation failed with error: {e}"
        json_result: dict = json.loads(response.content[0].text)
        logger.info(f"{test_method} response: {json_result}")
        assert isinstance(json_result["converted_amount"], float), "Expected float value for converted amount"
        assert json_result["converted_amount"] > 100.0, "The exchange rate for GBP to JPY should be greater than 1.0"
        # Run again to test cache hit
        response = asyncio.run(
            self.call_tool(
                tool_name=test_method,
                mcp_client=mcp_client,
                from_currency="GBP",
                to_currency="JPY",
                amount=100.0,
            )
        )
        parsed_metadata = ResponseMetadata.model_validate(response.meta[AppMetadata.PACKAGE_NAME])
        assert parsed_metadata.cached_response is True, "Expected cached_response to be True on second call"

        # Test with the same currency for from and to to raise an expected exception
        with pytest.raises(Exception) as exc_info:
            asyncio.run(
                self.call_tool(
                    tool_name=test_method,
                    mcp_client=mcp_client,
                    from_currency="GBP",
                    to_currency="GBP",
                    amount=100.0,
                )
            )
        assert "Source currency 'GBP' and target currency 'GBP' are the same." in str(exc_info.value), (
            "Expected exception message to indicate failure to retrieve exchange rates"
        )

    def test_get_latest_exchange_rates(self, mcp_client, mcp_client_bogus_config, benchmark):
        """Test the get_latest_exchange_rates function to ensure that it returns the list of latest rates with other currencies."""
        test_method = "get_latest_exchange_rates"

        def bench_func():
            return asyncio.run(
                self.call_tool(
                    tool_name=test_method,
                    mcp_client=mcp_client,
                    base_currency="JPY",
                    symbols=["EUR", "GBP", "CHF", "NZD"],
                )
            )

        response = benchmark.pedantic(bench_func, iterations=1, rounds=5, warmup_rounds=1)
        assert isinstance(response.meta, dict), (
            f"Expected result from MCP tool call, {test_method}, to contain a metadata dictionary"
        )
        try:
            ResponseMetadata.model_validate(response.meta[AppMetadata.PACKAGE_NAME])
        except Exception as e:
            assert False, f"Metadata validation failed with error: {e}"
        json_result: dict = json.loads(response.content[0].text)
        assert len(json_result["rates"].keys()) > 0, "Expected non-empty list of currency rates"
        assert all((isinstance(code, str) and len(code) == 3) for code in json_result["rates"].keys()), (
            "All currency codes for exchange rates should be 3-character strings"
        )

        # Run again to test cache hit
        response = asyncio.run(
            self.call_tool(
                tool_name=test_method,
                mcp_client=mcp_client,
                base_currency="JPY",
                symbols=["EUR", "GBP", "CHF", "NZD"],
            )
        )
        parsed_metadata = ResponseMetadata.model_validate(response.meta[AppMetadata.PACKAGE_NAME])
        assert parsed_metadata.cached_response is True, "Expected cached_response to be True on second call"

        with pytest.raises(Exception) as exc_info:
            asyncio.run(
                self.call_tool(
                    tool_name=test_method,
                    mcp_client=mcp_client_bogus_config,
                    base_currency="JPY",
                    symbols=["EUR", "GBP", "CHF", "NZD"],
                )
            )

        assert "Connection refused" in str(exc_info.value), (
            "Expected exception message to indicate failure to connect to bogus API endpoint"
        )

    def test_get_historical_exchange_rates(self, mcp_client, mcp_client_bogus_config, benchmark):
        """Test the get_historical_exchange_rates function to ensure that it returns the list of historical rates with other currencies."""
        test_method = "get_historical_exchange_rates"

        def bench_func():
            return asyncio.run(
                self.call_tool(
                    tool_name=test_method,
                    mcp_client=mcp_client,
                    base_currency="JPY",
                    start_date="2025-06-01",
                    end_date="2025-06-19",
                    symbols=["EUR", "GBP", "CHF", "NZD"],
                )
            )

        response = benchmark.pedantic(bench_func, iterations=1, rounds=5, warmup_rounds=1)
        assert isinstance(response.meta, dict), (
            f"Expected result from MCP tool call, {test_method}, to contain a metadata dictionary"
        )
        try:
            ResponseMetadata.model_validate(response.meta[AppMetadata.PACKAGE_NAME])
        except Exception as e:
            assert False, f"Metadata validation failed with error: {e}"
        json_result: dict = json.loads(response.content[0].text)
        assert all(len(rates_for_date) > 0 for _, rates_for_date in json_result["rates"].items()), (
            "Expected non-empty list of currency rates"
        )
        assert all(
            ((isinstance(code, str) and len(code) == 3) for code in rates_for_date.keys())
            for _, rates_for_date in json_result["rates"].items()
        ), "All currency codes for exchange rates should be 3-character strings"

        try:
            asyncio.run(
                self.call_tool(
                    tool_name=test_method,
                    mcp_client=mcp_client,
                    base_currency="JPY",
                    start_date="2025-06-01",
                    end_date="2025-06-19",
                    symbols="EUR",
                )
            )
        except Exception as e:
            assert False, f"MCP tool call with single currency symbol should not have raised exception: {e}"

        try:
            asyncio.run(
                self.call_tool(
                    tool_name=test_method,
                    mcp_client=mcp_client,
                    base_currency="JPY",
                    start_date="2025-08-31",
                    symbols=["NOK"],
                )
            )
        except Exception as e:
            assert False, f"MCP tool call with only start_date and no end_date should not have raised exception: {e}"

        with pytest.raises(Exception) as exc_info:
            asyncio.run(
                self.call_tool(
                    tool_name=test_method,
                    mcp_client=mcp_client,
                    base_currency="JPY",
                    symbols=["EUR", "GBP", "CHF", "NZD"],
                )
            )
        assert "You must provide either a specific date, a start date, or a date range." in str(exc_info.value), (
            "Expected exception message to indicate failure to retrieve exchange rates"
        )

        with pytest.raises(Exception) as exc_info:
            asyncio.run(
                self.call_tool(
                    tool_name=test_method,
                    mcp_client=mcp_client_bogus_config,
                    base_currency="JPY",
                    start_date="2025-06-01",
                    end_date="2025-06-19",
                    symbols=["EUR", "GBP", "CHF", "NZD"],
                )
            )
        assert "Connection refused" in str(exc_info.value), (
            "Expected exception message to indicate failure to connect to bogus API endpoint"
        )

    def test_get_latest_exchange_rates_for_single_currency(self, mcp_client):
        """Test the get_latest_exchange_rates function to ensure that it returns the latest rates for a single currency."""
        test_method = "get_latest_exchange_rates"
        response = asyncio.run(
            self.call_tool(
                tool_name=test_method,
                mcp_client=mcp_client,
                base_currency="JPY",
                symbols="GBP",
            )
        )
        assert isinstance(response.meta, dict), (
            f"Expected result from MCP tool call, {test_method}, to contain a metadata dictionary"
        )
        try:
            ResponseMetadata.model_validate(response.meta[AppMetadata.PACKAGE_NAME])
        except Exception as e:
            assert False, f"Metadata validation failed with error: {e}"
        json_result: dict = json.loads(response.content[0].text)
        assert len(json_result["rates"].keys()) > 0, "Expected non-empty list of currency rates"
        assert all((isinstance(code, str) and len(code) == 3) for code in json_result["rates"].keys()), (
            "All currency codes for exchange rates should be 3-character strings"
        )

    def test_get_historical_exchange_rates_for_a_single_currency(self, mcp_client):
        """Test the get_historical_exchange_rates function to ensure that it returns the historical rates for a single currency."""
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
        assert isinstance(response.meta, dict), (
            f"Expected result from MCP tool call, {test_method}, to contain a metadata dictionary"
        )
        try:
            ResponseMetadata.model_validate(response.meta[AppMetadata.PACKAGE_NAME])
        except Exception as e:
            assert False, f"Metadata validation failed with error: {e}"
        json_result: dict = json.loads(response.content[0].text)
        assert all(len(rates_for_date) > 0 for _, rates_for_date in json_result["rates"].items()), (
            "Expected non-empty list of currency rates"
        )
        assert all(
            ((isinstance(code, str) and len(code) == 3) for code in rates_for_date.keys())
            for _, rates_for_date in json_result["rates"].items()
        ), "All currency codes for exchange rates should be 3-character strings"

    def test_convert_currency_specific_date(self, mcp_client):
        """Test the convert_currency_specific_date function to ensure it returns a list of supported currencies."""
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
        assert isinstance(response.meta, dict), (
            f"Expected result from MCP tool call, {test_method}, to contain a metadata dictionary"
        )
        try:
            ResponseMetadata.model_validate(response.meta[AppMetadata.PACKAGE_NAME])
        except Exception as e:
            assert False, f"Metadata validation failed with error: {e}"
        json_result: dict = json.loads(response.content[0].text)
        print(f"{test_method} response: {json_result}")
        assert isinstance(json_result["converted_amount"], float), "Expected float value for converted amount"
        assert json_result["converted_amount"] > 100.0, "The exchange rate for GBP to JPY should be greater than 1.0"

        # Run again to test cache hit
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
        parsed_metadata = ResponseMetadata.model_validate(response.meta[AppMetadata.PACKAGE_NAME])
        assert parsed_metadata.cached_response is True, "Expected cached_response to be True on second call"

        # Test with the same currency for from and to to raise an expected exception
        with pytest.raises(Exception) as exc_info:
            asyncio.run(
                self.call_tool(
                    tool_name=test_method,
                    mcp_client=mcp_client,
                    from_currency="GBP",
                    to_currency="GBP",
                    amount=100.0,
                    specific_date="2025-06-01",
                )
            )
        assert "Source currency 'GBP' and target currency 'GBP' are the same." in str(exc_info.value), (
            "Expected exception message to indicate failure to retrieve exchange rates"
        )
