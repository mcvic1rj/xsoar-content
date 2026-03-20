import demistomock as demisto  # noqa: F401
import urllib3
from CommonServerPython import *  # noqa: F401

# disable insecure warnings
urllib3.disable_warnings()


class Client(BaseClient):
    def call_user_info(self) -> dict[str, any]:
        return self._http_request(
            method="GET",
            url_suffix="/api/v1/user/info/",
        )
    def call_search_api(self, args: dict[str, any]) -> dict[str, any]:
        params = {
            "query": args.get("query"),
            "datasource": args.get("datasource"),
        }
        return self._http_request(
            method="GET",
            url_suffix="/api/v1/search/",
            params=params,
        )

def parse_search_response(response: dict[str, any]) -> list[dict[str, any]]:
    result = []
    try:
        for item in response.get("results", []):
            raw_data = {}
            result.append(
            {
                    "value": item.get("page").get("url"),
                    "type": FeedIndicatorType.URL,
                    "service": "UrlScanFeed",
                }
            )
    except Exception as err:
        demisto.debug(str(err))
        raise ValueError(
            f"Could not parse returned data as indicator. \n\nError massage: {err}"
        )
    return result
def test_module(client: Client) -> str:
    """Builds the iterator to check that the feed is accessible.
    Args:
        client: Client object.
    Returns:
        Outputs.
    """
    client.call_user_info()
    return "ok"

def fetch_urlscan_indicators(client: Client, args: dict[str, any]) -> List[Dict]:
    """Fetches indicators from the feed and creates indicator objects.
    Args:
        client: Client object with request
    Returns:
        Indicators.
    """
    if not args.get("query") or not args.get("datasource"):
        raise ValueError("Both 'query' and 'datasource' arguments are required.")
    indicators = client.call_search_api(args)
    return parse_search_response(indicators)


def main():
    params = demisto.params()
    base_url = params.get("url")
    insecure = not params.get("insecure", False)
    proxy = params.get("proxy", False)
    command = demisto.command()
    args = demisto.args()
    demisto.debug(f"Command being called is {command}")
    
    commands = {
        "test-module": test_module,
        "urlscanfeed-get-indicators":fetch_urlscan_indicators,
        "fetch-indicators": fetch_urlscan_indicators,
    }
    if command not in commands:
        raise NotImplementedError(f"Command: {command} not implemented")
        
    try:
        client = Client(
            base_url=base_url,
            verify=insecure,
            proxy=proxy,
        )
        result = commands[command](client, **args)  # type: ignore
        return_results(result)
    except Exception as e:
        demisto.error(traceback.format_exc())  # Print the traceback
        return_error(f"Failed to execute {command} command.\nError:\n{str(e)}")


if __name__ in ("__main__", "__builtin__", "builtins"):  # pragma: no cover
    main()
