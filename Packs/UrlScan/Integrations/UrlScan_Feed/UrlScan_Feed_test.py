import os

from CommonServerPython import FeedIndicatorType, string_to_table_header, tableToMarkdown, DemistoException

import pytest

import json

from Packs.UrlScan.Integrations.UrlScan_Feed import UrlScan_Feed


URL = "https://openphish.com/feed.txt"


def util_load_json(file_name):
    from os import path
    with open(os.path.join(os.path.dirname(__file__), "test_data", file_name), encoding="utf-8") as mock_file:
        return json.loads(mock_file.read())

class TestAPIClient:
    def test_search_api(self, mocker):
        from UrlScan_Feed import Client
        call_response = util_load_json("search_api_response.json")
        args = {"query": "test", "datasource": "test"}
        mocker.patch.object(Client, "_http_request", return_value=call_response)
        client = Client(base_url="https://urlscan.io", verify=False, proxy=False)
        assert client.call_search_api(args) == call_response

    def test_user_info_api(self, mocker):
        from UrlScan_Feed import Client
        httpreq = mocker.patch.object(Client, "_http_request", return_value={})
        client = Client(base_url="https://urlscan.io", verify=False, proxy=False)
        client.call_user_info()
        assert httpreq.called_once_with(method="GET", url_suffix="/api/v1/user/info/")

class TestHelpers:
    def test_parse_search_response_error(self):
        from UrlScan_Feed import parse_search_response
        search_response = {"results": [{"page":"http://test.com"}]}
        
        with pytest.raises(ValueError):
            parse_search_response(search_response)

class TestCommands:
    def test_fetch_urlscan_indicators(self, mocker):
        from UrlScan_Feed import Client, fetch_urlscan_indicators
        indicators_response = util_load_json("search_api_response.json")
        call_response = util_load_json("call_fetch_urlscan_indicators.json")
        mocker.patch.object(Client, "call_search_api", return_value=indicators_response)
        client = Client(base_url="https://urlscan.io", verify=False, proxy=False)
        assert fetch_urlscan_indicators(client, {"query": "test", "datasource": "test"}) == call_response
    
    def test_fetch_urlscan_indicators_with_missing_input(self, mocker):
        from UrlScan_Feed import Client, fetch_urlscan_indicators
        client = Client(base_url="https://urlscan.io", verify=False, proxy=False)
        with pytest.raises(ValueError):
            fetch_urlscan_indicators(client, {"query": "test"})
        with pytest.raises(ValueError):
            fetch_urlscan_indicators(client, {"datasource": "test"})
        with pytest.raises(ValueError):
            fetch_urlscan_indicators(client, {})
            
    def test_command_not_implemented(self, mocker):
        from UrlScan_Feed import main
        from CommonServerPython import demisto
        not_implemented_command = "bad-command"
        mocker.patch.object(demisto,"command", return_value=not_implemented_command)
        debug_call = mocker.patch.object(demisto, "debug")
        with pytest.raises(NotImplementedError) as returned_exception:
            main()
        assert returned_exception.value.args[0] == f"Command: {not_implemented_command} not implemented"
        assert debug_call.called_once()
        assert debug_call.called_with(f"Command being called is {not_implemented_command}")

    def test_test_module(self, mocker):
        from UrlScan_Feed import Client, test_module
        from CommonServerPython import return_results
        call_user_info = mocker.patch.object(Client, "call_user_info")
        demisto_results = mocker.patch.object(return_results,"__call__")
        assert test_module(Client(base_url="https://urlscan.io", verify=False, proxy=False)) == "ok"
        assert call_user_info.called_once()
        assert demisto_results.called_once_with("ok")
        
    def test_client_bad_input(self, mocker):
        from UrlScan_Feed import Client
        from CommonServerPython import demisto, return_error
        demisto_error = mocker.patch.object(demisto, "error")
        return_error_func = mocker.patch.object(return_error, "__call__")
        Client(base_url="https://urlscan.io", verify="bad_input", proxy=False)
        assert demisto_error.called_once()
        assert return_error_func.called_once()
        
