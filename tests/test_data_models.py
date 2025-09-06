from frankfurtermcp.common import EnvVar, AppMetadata
from frankfurtermcp.model import CurrencyConversionResponse, ResponseMetadata


class TestDataModels:
    def test_currency_conversion_response(self):
        """
        Test the CurrencyConversionResponse data model to ensure that it correctly validates and stores data.
        """
        # Made up data for testing
        data = {
            "from_currency": "GBP",
            "to_currency": "EUR",
            "amount": 100.0,
            "converted_amount": 115.0,
            "exchange_rate": 1.15,
            "rate_date": "2025-08-31",
        }
        response = CurrencyConversionResponse(**data)
        assert response.from_currency == "GBP"
        assert response.to_currency == "EUR"
        assert response.amount == 100.0
        assert response.converted_amount == 115.0
        assert response.exchange_rate == 1.15
        assert response.rate_date.isoformat() == "2025-08-31"

    def test_currency_conversion_response_negative_floats(self):
        """
        Test the CurrencyConversionResponse data model to ensure that it raises a validation error for invalid amount.
        """
        data = {
            "from_currency": "GBP",
            "to_currency": "EUR",
            "amount": -100.0,  # Invalid negative amount
            "converted_amount": -115.0,  # Invalid negative amount
            "exchange_rate": -1.15,  # Invalid negative exchange rate
            "rate_date": "2025-08-31",
        }
        obj: CurrencyConversionResponse = None
        try:
            obj = CurrencyConversionResponse(**data)
        except Exception as e:
            assert (
                f"3 validation errors for {CurrencyConversionResponse.__name__}"
                in str(e)
            )
        finally:
            assert obj is None

    def test_currency_conversion_response_invalid_currency_codes(self):
        """
        Test the CurrencyConversionResponse data model to ensure that it raises a validation error for invalid currency codes.
        """
        data = {
            "from_currency": "ABC",  # Invalid currency code
            "to_currency": "XYZ",
            "amount": 100.0,
            "converted_amount": 115.0,
            "exchange_rate": 1.15,
            "rate_date": "2025-08-31",
        }
        obj: CurrencyConversionResponse = None
        try:
            obj = CurrencyConversionResponse(**data)
        except Exception as e:
            assert (
                f"2 validation errors for {CurrencyConversionResponse.__name__}"
                in str(e)
            )
        finally:
            assert obj is None

    def test_currency_conversion_response_invalid_date(self):
        """
        Test the CurrencyConversionResponse data model to ensure that it raises a validation error for invalid date format.
        """
        data = {
            "from_currency": "GBP",
            "to_currency": "EUR",
            "amount": 100.0,
            "converted_amount": 115.0,
            "exchange_rate": 1.15,
            "rate_date": "25-32-31",  # Invalid date format
        }
        obj: CurrencyConversionResponse = None
        try:
            obj = CurrencyConversionResponse(**data)
        except Exception as e:
            assert (
                f"1 validation error for {CurrencyConversionResponse.__name__}"
                in str(e)
            )
        finally:
            assert obj is None

    def test_response_metadata(self):
        """
        Test the ResponseMetadata data model to ensure that it correctly initializes with valid data.
        """

        data = {
            "version": AppMetadata.package_metadata["Version"],
            "api_url": EnvVar.DEFAULT__FRANKFURTER_API_URL,
            "api_status_code": 200,
            "api_bytes_downloaded": 512,
            "api_elapsed_time": 150000,  # in microseconds
        }
        response = ResponseMetadata(**data)
        assert response.version == AppMetadata.package_metadata["Version"]
        assert str(response.api_url) == EnvVar.DEFAULT__FRANKFURTER_API_URL
        assert response.api_status_code == 200
        assert response.api_bytes_downloaded == 512
        assert response.api_elapsed_time == 150000

    def test_response_metadata_negative_values(self):
        """
        Test the ResponseMetadata data model to ensure that it raises a validation error for negative values.
        """

        data = {
            "version": AppMetadata.package_metadata["Version"],
            "api_url": EnvVar.DEFAULT__FRANKFURTER_API_URL,
            "api_status_code": 200,
            "api_bytes_downloaded": -512,  # Invalid negative bytes downloaded
            "api_elapsed_time": -150000,  # Invalid negative elapsed time
        }
        obj: ResponseMetadata = None
        try:
            obj = ResponseMetadata(**data)
        except Exception as e:
            assert f"2 validation errors for {ResponseMetadata.__name__}" in str(e)
        finally:
            assert obj is None

    def test_response_metadata_invalid_url(self):
        """
        Test the ResponseMetadata data model to ensure that it raises a validation error for invalid URL.
        """

        data = {
            "version": AppMetadata.package_metadata["Version"],
            "api_url": "htp:/invalid-url",  # Invalid URL format
            "api_status_code": 200,
            "api_bytes_downloaded": 512,
            "api_elapsed_time": 150000,  # in microseconds
        }
        obj: ResponseMetadata = None
        try:
            obj = ResponseMetadata(**data)
        except Exception as e:
            assert f"1 validation error for {ResponseMetadata.__name__}" in str(e)
        finally:
            assert obj is None
