import json
from pathlib import Path
from typing import Any

import pytest
import requests
from CommonServerPython import CommandResults, DemistoException
from demisto_sdk.commands.common.handlers import JSON_Handler



def util_load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.loads(f.read())

class TestAddAddressCommand:
    """Tests for add_address_command."""
    MISSING_INPUT_CASES = [
        ({"address_type": "IPv4"}),
        ({"ip": ""}),
        ({"address_type": ""}),
        ({"address_type": None}),
        ({"address": None}),
        ({"address_type": None, "address": None}),
        ({"address_type": "", "address": ""}),
    ]
    @pytest.mark.parametrize("missing_field", MISSING_INPUT_CASES)
    def test_add_address_missing_input(self, missing_field):
        """Tests add_address_command raises ValueError when ip is missing."""
        from ForcepointV2 import add_address_command

        client = ""
        args = missing_field

        with pytest.raises(ValueError, match="Option address and address_type are required"):
            add_address_command(client, args)
    
    def test_add_address_command_success(self, mocker):
        """Tests add_address_command with valid arguments."""
        from ForcepointV2 import Client,add_address_command

        client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
        mock_response = {"id": "addr_123", "address": "asdf"}
        mocker.patch.object(client, "add_address", return_value=mock_response)
        args = {"address": "asdf", "address_type": "IPv4"}
        result = add_address_command(client, args)
        assert result.outputs == mock_response
        assert result.outputs_prefix == "Forcepoint.Address"
        assert result.outputs_key_field == "id"
        client.add_address.assert_called_once()
        assert isinstance(result, CommandResults)
class TestListCategoriesCommand:
    """Tests for list_categories_command."""
    def test_list_categories_command_success(self, mocker):
        """Tests list_categories_command returns correct categories."""
        from ForcepointV2 import Client,list_categories_command

        client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
        mock_response = {"categories": [{"id": "cat_123", "name": "Test Category"}]}
        mocker.patch.object(client, "list_categories", return_value=mock_response)

        args = {"all": False}
        result = list_categories_command(client, args)

        assert result.outputs == mock_response
        assert result.outputs_prefix == "Forcepoint.Category"
        assert result.outputs_key_field == "id"
        client.list_categories.assert_called_once_with(all=False)

class TestAddCategoryCommand:
    """Tests for add_category_command."""
    def test_add_category_command_missing_name(self):
        """Tests add_category_command raises ValueError when category_name is missing."""
        from ForcepointV2 import add_category_command

        client = ""
        args = {"category_description": "Test Description"}

        with pytest.raises(ValueError, match="category_name is required"):
            add_category_command(client, args)

    def test_add_category_command_optional_fields(self, mocker):
        """Tests add_category_command with only required field."""
        from ForcepointV2 import Client,add_category_command

        client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
        mock_response = {"id": "cat_456", "name": "Category Only"}
        mocker.patch.object(client, "add_category", return_value=mock_response)

        args = {"category_name": "Category Only"}
        result = add_category_command(client, args)

        assert result.outputs == mock_response
        client.add_category.assert_called_once_with("Category Only", None, None)

    def test_add_category_command_success(self, mocker):
        """Tests add_category_command with valid arguments."""
        from ForcepointV2 import Client,add_category_command


        client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
        mock_response = {"id": "cat_123", "name": "Test Category", "description": "Test Description"}
        mocker.patch.object(client, "add_category", return_value=mock_response)

        args = {
            "category_name": "Test Category",
            "category_description": "Test Description",
            "parent_category_id": "parent_123",
        }
        result = add_category_command(client, args)

        assert result.outputs == mock_response
        assert result.outputs_prefix == "Forcepoint.Category"
        assert result.outputs_key_field == "id"


class TestDeleteCategoryCommand:
    """Tests for delete_category_command."""
    def test_delete_category_command_missing_id(self):
        """Tests delete_category_command raises ValueError when category_id is missing."""
        from ForcepointV2 import delete_category_command

        client = ""
        args = {}

        with pytest.raises(ValueError, match="category_id is required"):
            delete_category_command(client, args)
    
    def test_delete_category_command_success(self, mocker):
        """Tests delete_category_command with valid category_id."""
        from ForcepointV2 import Client,delete_category_command
        from CommonServerPython import DemistoException

        client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
        mock_response = {"id": "cat_123", "name": "Test Category", "description": "Test Description"}
        mocker.patch.object(client, "delete_category", return_value=mock_response)

        args = {"category_id": "cat_123"}
        result = delete_category_command(client, args)

        assert result.outputs == mock_response
        assert result.outputs_prefix == "Forcepoint.Category"
        assert result.outputs_key_field == "id"
        assert client.delete_category.call_count == 1
        assert isinstance(result, CommandResults)
    
    def test_delete_category_command_api_error(self, mocker):
        """Tests delete_category_command when API returns an error."""
        from ForcepointV2 import Client,delete_category_command

        client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
        mocker.patch.object(client, "delete_category", side_effect=DemistoException("API error occurred"))

        args = {"category_id": "cat_123"}
        with pytest.raises(DemistoException, match="API error occurred"):
            delete_category_command(client, args)
    
    def test_delete_category_command_not_found(self, mocker):
        """Tests delete_category_command when category is not found."""
        from ForcepointV2 import Client,delete_category_command

        client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
        mocker.patch.object(client, "delete_category", side_effect=DemistoException("Category not found"))

        args = {"category_id": "nonexistent_cat"}
        with pytest.raises(DemistoException, match="Category not found"):
            delete_category_command(client, args)
            

class TestGetCategoryCommand:
    """Tests for get_category_command."""


    def test_get_category_command_success(self, mocker):
        """Tests get_category_command with valid category_id."""
        from ForcepointV2 import Client,get_category_command

        client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
        mock_response = {"id": "cat_123", "name": "Test Category", "description": "Test Description"}
        mocker.patch.object(client, "get_category", return_value=mock_response)

        args = {"category_id": "cat_123"}
        result = get_category_command(client, args)

        assert result.outputs == mock_response
        assert result.outputs_prefix == "Forcepoint.Category"
        assert result.outputs_key_field == "id"

    def test_get_category_command_missing_id(self):
        """Tests get_category_command raises ValueError when category_id is missing."""
        from ForcepointV2 import Client,get_category_command

        client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
        args = {}

        with pytest.raises(ValueError, match="category_id is required"):
            get_category_command(client, args)

    def test_get_category_command_api_error(self,mocker):
        """Tests get_category_command when API returns an error."""
        from ForcepointV2 import Client,get_category_command

        client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
        mocker.patch.object(client, "get_category", side_effect=DemistoException("API error occurred"))

        args = {"category_id": "cat_123"}
        with pytest.raises(DemistoException, match="API error occurred"):
            get_category_command(client, args)

    def test_get_category_command_invalid_id(self,mocker):
        """Tests get_category_command with invalid category_id format."""
        from ForcepointV2 import Client,get_category_command

        client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
        mocker.patch.object(client, "get_category", side_effect=DemistoException("Invalid category ID format"))

        args = {"category_id": "invalid_id"}
        with pytest.raises(DemistoException, match="Invalid category ID format"):
            get_category_command(client, args)
    

    def test_get_category_command_not_found(self, mocker):
        """Tests get_category_command when category is not found."""
        from ForcepointV2 import Client,get_category_command

        client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
        mocker.patch.object(client, "get_category", side_effect=DemistoException("Category not found"))

        args = {"category_id": "nonexistent_cat"}
        with pytest.raises(DemistoException, match="Category not found"):
            get_category_command(client, args)

    def test_get_category_command_success(self, mocker):
        """Tests get_category_command with valid category_id."""
        from ForcepointV2 import Client,get_category_command

        client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
        mock_response = {"id": "cat_123", "name": "Test Category", "description": "Test Description"}
        mocker.patch.object(client, "get_category", return_value=mock_response)

        args = {"category_id": "cat_123"}
        result = get_category_command(client, args)

        assert result.outputs == mock_response
        assert result.outputs_prefix == "Forcepoint.Category"
        assert result.outputs_key_field == "id"
        
        
class TestGetStatusCommand:
    """Tests for get_status_command."""
    def test_get_status_command_success(self, mocker):
        """Tests get_status_command returns correct status."""
        from ForcepointV2 import Client,get_status_command

        client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
        mock_response = util_load_json(Path(__file__).parent / "test_data" / "get_status_api_resp.json")
        mocker.patch.object(client, "_http_request", return_value=mock_response)

        args = {}
        result = get_status_command(client, args)

        assert result.outputs == mock_response
        assert result.outputs_prefix == "Forcepoint.Status"
        assert isinstance(result, CommandResults)

class TestTestModuleCommand:
    """Tests for test_module_command."""
    def test_test_module_command_success(self, mocker):
        """Tests test_module_command returns success when API is reachable."""
        from ForcepointV2 import Client,test_module_command

        client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
        mock_response = "ok"
        mocker.patch.object(client, "get_status", return_value=mock_response)

        args = {}
        result = test_module_command(client, args)

        assert result == mock_response
        assert isinstance(result, str)
        
class TestClient:
    """Tests for Client class."""
    
    class TestAddressCalls:
        """Tests for address-related Client methods."""
        def test_add_address_call(self, mocker):
            """Tests add_address method calls API with correct parameters."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mock_response = {"id": "addr_123", "address": "asdf"}
            mocker.patch.object(client, "transaction_request", return_value=mock_response)

            result = client.add_address("asdf", "IPv4")
            assert result == mock_response
            client.transaction_request.assert_called_once_with("asdf", "IPv4") #TODO fix params
            client.transaction_request.assert_called_once()
        
        def test_delete_address_call(self, mocker):
            """Tests delete_address method calls API with correct parameters."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mock_response = {"id": "addr_123", "address": "asdf"}
            mocker.patch.object(client, "transaction_request", return_value=mock_response)

            result = client.delete_address("addr_123")
            assert result == mock_response
            client.transaction_request.assert_called_once_with(url_suffix="/addresses/delete", method="POST", body={"Address IDs": ["addr_123"]}) #TODO fix params
            client.transaction_request.assert_called_once()
    class TestCategoryCalls:
        """Tests for category-related Client methods."""
        def test_add_category_call(self, mocker):
            """Tests add_category method calls API with correct parameters."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mocker.patch.object(client, "transaction_request", return_value={"id": "cat_123"})
            

            result = client.add_category("Test Category", "Test Description", "parent_123")
            assert result == {"id": "cat_123"}
            client.transaction_request.assert_called_once_with(url_suffix="/categories", method="POST", body={"name": "Test Category", "description": "Test Description", "parent": "parent_123"})
            client.transaction_request.assert_called_once()
            
        def test_add_category_api_error(self, mocker):
            """Tests add_category method when API returns an error."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mocker.patch.object(client, "transaction_request", side_effect=requests.exceptions.HTTPError("Internal Server Error"))

            with pytest.raises(Exception) as err:
                client.add_category("Test Category", "Test Description", "parent_123")
            assert str(err.value) == "Internal Server Error"
            assert client.transaction_request.call_count == 1
            assert client.transaction_request.called_with(method="POST", url_suffix="/categories", json_data={"name": "Test Category", "description": "Test Description", "parent_id": "parent_123"})
    
        def test_delete_category_single_id_call(self, mocker):
            """Tests delete_category method calls API with correct parameters."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mocker.patch.object(client, "transaction_request", return_value={"id": "cat_123"})

            result = client.delete_category(category_id="cat_123")
            assert result == {"id": "cat_123"}
            client.transaction_request.assert_called_once_with(url_suffix="/categories/delete", method="POST", body={"Category IDs": ["cat_123"]})
            client.transaction_request.assert_called_once()

        
        def test_delete_category_multiple_ids_call(self, mocker):
            """Tests delete_category method with multiple category IDs."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mocker.patch.object(client, "transaction_request", return_value={"ids": ["cat_123", "cat_456"]})

            result = client.delete_category(["cat_123", "cat_456"])
            assert result == {"ids": ["cat_123", "cat_456"]}
            client.transaction_request.assert_called_once_with(url_suffix="/categories/delete", method="POST", body={"Category IDs": ["cat_123", "cat_456"]})
            client.transaction_request.assert_called_once()
        
        def test_delete_category_single_name_call(self, mocker):
            """Tests delete_category method with single category name."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mocker.patch.object(client, "transaction_request", return_value={"id": "cat_123"})

            result = client.delete_category(category_name="Test Category")
            assert result == {"id": "cat_123"}
            client.transaction_request.assert_called_once_with(url_suffix="/categories/delete", method="POST", body={"Category Names": ["Test Category"]})
            client.transaction_request.assert_called_once()
        
        def test_delete_category_multiple_names_call(self, mocker):
            """Tests delete_category method with multiple category names."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mocker.patch.object(client, "transaction_request", return_value={"names": ["Test Category 1", "Test Category 2"]})

            result = client.delete_category(category_name=["Test Category 1", "Test Category 2"])
            assert result == {"names": ["Test Category 1", "Test Category 2"]}
            client.transaction_request.assert_called_once_with(url_suffix="/categories/delete", method="POST", body={"Category Names": ["Test Category 1", "Test Category 2"]})
            client.transaction_request.assert_called_once()
        
        def test_delete_category_both_id_and_name_call(self, mocker):
            """Tests delete_category method when both category_id and category_name are provided."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mocker.patch.object(client, "transaction_request", return_value={"id": "cat_123"})

            result = client.delete_category(category_id="cat_123", category_name="Test Category")
            assert result == {"id": "cat_123"}
            client.transaction_request.assert_called_once_with(url_suffix="/categories/delete", method="POST", body={"Category IDs": ["cat_123"], "Category Names": ["Test Category"]})
            client.transaction_request.assert_called_once()
        
        def test_delete_category_api_error(self, mocker):
            """Tests delete_category method when API returns an error."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mocker.patch.object(client, "transaction_request", side_effect=requests.exceptions.HTTPError("Internal Server Error"))

            with pytest.raises(Exception) as err:
                client.delete_category("cat_123")
            assert str(err.value) == "Internal Server Error"
            assert client.transaction_request.call_count == 1
            assert client.transaction_request.called_with(method="DELETE", url_suffix="/categories", json_data={"id": "cat_123"})
        
    
        def test_list_categories_call(self, mocker):
            """Tests list_categories method calls API and returns correct categories."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mock_response = {"categories": [{"id": "cat_123", "name": "Test Category"}]}
            mocker.patch.object(client, "_http_request", return_value=mock_response)

            result = client.list_categories(all=False)
            assert result == mock_response
            client._http_request.assert_called_once()
            client._http_request.assert_called_with(method="GET", url_suffix="/categories")
            
        def test_list_categories_api_error(self, mocker):
            """Tests list_categories method when API returns an error."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mocker.patch.object(client, "_http_request", side_effect=requests.exceptions.HTTPError("Internal Server Error"))

            with pytest.raises(Exception) as err:
                client.list_categories(all=False)
            assert str(err.value) == "Internal Server Error"
            assert client._http_request.call_count == 1
            assert client._http_request.called_with(method="GET", url_suffix="/categories")
        
        def test_list_categories_all_call(self, mocker):
            """Tests list_categories method with all parameters."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mock_response = {"categories": [{"id": "cat_123", "name": "Test Category"}]}
            mocker.patch.object(client, "_http_request", return_value=mock_response)

            result = client.list_categories(all=True)
            assert result == mock_response
            client._http_request.assert_called_once()
            client._http_request.assert_called_with(method="GET", url_suffix="/categories/all")
            
        def test_get_category_call_single_id(self, mocker):
            """Tests get_category method calls API with correct parameters."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mock_response = {"id": "cat_123", "name": "Test Category", "description": "Test Description"}
            mocker.patch.object(client, "_http_request", return_value=mock_response)

            result = client.get_category(category_id="cat_123", category_name=None)
            assert result == mock_response
            client._http_request.assert_called_once()
            client._http_request.assert_called_with(method="GET", url_suffix="/categories", params={"catid": "cat_123"})
        
        def test_get_category_call_single_name(self, mocker):
            """Tests get_category method with single category name."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mock_response = {"id": "cat_123", "name": "Test Category", "description": "Test Description"}
            mocker.patch.object(client, "_http_request", return_value=mock_response)

            result = client.get_category(category_id=None, category_name="Test Category")
            assert result == mock_response
            client._http_request.assert_called_once()
            client._http_request.assert_called_with(method="GET", url_suffix="/categories", params={"catname": "Test Category"})
        
        def test_get_category_call_both_id_and_name(self, mocker):
            """Tests get_category method when both category_id and category_name are provided."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mock_response = {"id": "cat_123", "name": "Test Category", "description": "Test Description"}
            mocker.patch.object(client, "_http_request", return_value=mock_response)

            result = client.get_category(category_id="cat_123", category_name="Test Category")
            assert result == mock_response
            client._http_request.assert_called_once()
            client._http_request.assert_called_with(method="GET", url_suffix="/categories", params={"catid": "cat_123", "catname": "Test Category"})
    
        
    class TestGetStatusCall:
        """Tests for get_status method."""
        def test_get_status_call(self, mocker):
            """Tests get_status method calls API and returns correct status."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mock_response = util_load_json(Path(__file__).parent / "test_data" / "api_resp.json")
            mocker.patch.object(client, "_http_request", return_value=mock_response)

            result = client.get_status()
            assert result == mock_response
            client._http_request.assert_called_once()
            client._http_request.assert_called_with(method="GET", url_suffix="/categories/status")
            
    
    class TestTransactionCalls:
        """Tests for transaction method."""
        def test_start_transaction_call(self, mocker):
            """Tests start_transaction method calls API with correct parameters."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mocker.patch.object(client, "_http_request", return_value={"transaction_id": "txn_123"})

            result = client.start_transaction()
            assert result == "txn_123"
            client._http_request.assert_called_once()
            client._http_request.assert_called_with(method="GET", url_suffix="/categories/start")
        
        def test_start_transaction_api_error(self, mocker):
            """Tests start_transaction method when API returns an error."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mocker.patch.object(client, "_http_request", side_effect=requests.exceptions.HTTPError("Internal Server Error"))

            with pytest.raises(Exception) as err:
                client.start_transaction()

            assert str(err.value) == "API error occurred"
            assert client._http_request.call_count == 5
        
        def test_commit_transaction_call(self, mocker):
            """Tests commit_transaction method calls API with correct parameters."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mock_response = {"status": "committed"}
            mocker.patch.object(client, "_http_request", return_value=mock_response)

            result = client.commit_transaction("txn_123")
            assert result == mock_response
            client._http_request.assert_called_once()
            client._http_request.assert_called_with(method="POST", url_suffix="/categories/commit?transaction_id=txn_123")
            
        def test_rollback_transaction_call(self, mocker):
            """Tests rollback_transaction method calls API with correct parameters."""
            from ForcepointV2 import Client

            client = Client(base_url="", verify=False, proxy=False, auth=("", ""))
            mock_response = {"status": "rolled back"}
            mocker.patch.object(client, "_http_request", return_value=mock_response)

            result = client.rollback_transaction("txn_123")
            assert result == mock_response
            client._http_request.assert_called_once()
            client._http_request.assert_called_with(method="POST", url_suffix="/categories/rollback?transactionid=txn_123")
        

class TestMainFunction:
    """Tests for main function."""
    ALL_FUNC_CASES = [
        ("forcepoint-list-categories", {"all": False}, "list_categories_command"),
        ("forcepoint-add-category", {"category_name": "Test Category"}, "add_category_command"),
        ("forcepoint-delete-category", {"category_id": "cat_123"}, "delete_category_command"),
        ("forcepoint-get-category", {"category_id": "cat_123"}, "get_category_command"),
        ("forcepoint-get-status", {}, "get_status_command"),
        ("test-module", {}, "test_module_command"),
    ]
    @pytest.mark.parametrize("command, demisto_args, expected_call", ALL_FUNC_CASES)
    def test_main_function(self, mocker, command,demisto_args, expected_call):
        """Tests main function calls correct command function based on demisto.args."""
        from ForcepointV2 import main
        from CommonServerPython import demisto

        mocker.patch("ForcepointV2.demisto.args", return_value=demisto_args)
        mocker.patch("ForcepointV2.demisto.params", return_value={"url": "https://example.com", "credentials": {"identifier": "user", "password": "pass"}, "insecure": False, "proxy": False, "port": 15783})
        mock_command = mocker.patch(f"ForcepointV2.{expected_call}", return_value="mocked_result")
        mocker.patch("ForcepointV2.demisto.command", return_value=command)
        main()
        mock_command.assert_called_once()
    
    def test_main_function_invalid_command(self, mocker):
        """Tests main function raises ValueError for invalid command."""
        from ForcepointV2 import main
        from CommonServerPython import demisto

        mocker.patch("ForcepointV2.demisto.args", return_value={})
        mocker.patch("ForcepointV2.demisto.params", return_value={"url": "https://example.com", "credentials": {"identifier": "user", "password": "pass"}, "insecure": False, "proxy": False, "port": 15783})
        mocker.patch("ForcepointV2.demisto.command", return_value="invalid-command")

        errorWrapper = mocker.patch("ForcepointV2.return_error")
        result = main()
        assert errorWrapper.call_count == 1
        assert errorWrapper.called_with("Command 'invalid-command' not found")
