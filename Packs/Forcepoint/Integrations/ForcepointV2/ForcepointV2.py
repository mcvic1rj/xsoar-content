from typing import Any, Dict, Optional
from base64 import b64encode
from urllib.parse import urljoin
import urllib3
from CommonServerPython import *  # noqa # pylint: disable=unused-wildcard-import

# Disable insecure warnings
urllib3.disable_warnings()

""" CONSTANTS """

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"  # ISO8601 format with UTC, default in XSOAR

""" CLIENT CLASS """


class Client(BaseClient):
    def start_transaction(self) -> str:
        """Starts a transaction.

        Returns:
            str: The transaction id.
        """
        url = "/categories/start"
        transaction_id = None
        loop_count = 0
        while transaction_id is None and loop_count < 5:
            loop_count += 1
            try:
                result = self._http_request(url_suffix=url, method="GET")
                transaction_id = result.get("transaction_id")
            except Exception:
                safe_sleep(1)  # Sleep for a second before retrying
                continue
        
        if transaction_id is None:
            raise DemistoException("API error occurred")
                
        return transaction_id

    def commit_transaction(self, transaction_id: str) -> dict[str, Any]:
        """Commits all commands included in the specified transaction.

        Args:
            transaction_id (str): The transaction id to commit.

        Returns:
            dict[str, Any]: _description_
        """
        url = f"/categories/commit?transaction_id={transaction_id}"
        result = self._http_request(url_suffix=url, method="POST")
        return result

    def rollback_transaction(self, transaction_id: str) -> dict[str, Any]:
        """Rolls back all commands included in the specified transaction.

        Args:
            transaction_id (str): The ID of the transaction to roll back.

        Returns:
            dict[str, Any]: _description_
        """
        url = f"/categories/rollback?transactionid={transaction_id}"
        result = self._http_request(url_suffix=url, method="POST")
        return result
    
    def transaction_request(self, url_suffix: str, method: str, body: Optional[Dict[str, Any]] = None) -> dict[str, Any]:
        """Helper method to make API calls within a transaction.

        Args:
            url_suffix (str): The API endpoint suffix.
            method (str): The HTTP method to use.
            body (Optional[Dict[str, Any]]): The request body, if applicable.

        Returns:
            dict[str, Any]: _description_
        """
        try:
            transaction_id = self.start_transaction()
            if body is None:
                body = {}
            body['Transaction ID'] = transaction_id
            result = self._http_request(url_suffix=url_suffix, method=method, json_data=body)
            self.commit_transaction(transaction_id)
            return result
        except Exception as e:
            self.rollback_transaction(transaction_id)
            raise e

    def get_status(self) -> dict[str, Any]:
        """Gets status information that describes the health of the system,
        as well as the total number of URLs, IP addresses, and ranges in the system.

        Returns:
            dict[str, Any]: _description_
        """
        url = "/categories/status"
        result = self._http_request(url_suffix=url, method="GET")
        return result

    def add_category(
        self,
        category_name: str,
        category_description: Optional[str],
        parent_category_id: Optional[str],
    ) -> dict[str, Any]:
        """Calls Forcepoint API to add a new category

        Args:
            category_name (str): The name of the new category.
            category_description (Optional[str]): The description of the new category.
            parent_category_id (Optional[str]): The ID of the parent category.

        Returns:
            dict[str, Any]: _description_
        """
        url = "/categories"
        body = {
            "name": category_name,
            "description": category_description,
            "parent": parent_category_id,
        }
        result = self.transaction_request(url_suffix=url, method="POST", body=body)

        return result

    def delete_category(
        self,
        category_id: Optional[list[str]] = None,
        category_name: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Deletes a category from the Forcepoint.

        Args:
            category_id (Optional[list[str]], optional): The category id to delete. Defaults to None.
            category_name (Optional[list[str]], optional): The category name to delete. Defaults to None.

        Returns:
            dict[str, Any]: _description_
        """
        url = "/categories/delete"
        method = "POST"
        body = {}
        if category_id is not None:
            if isinstance(category_id, str):
                body['Category IDs'] = [category_id]
            elif isinstance(category_id, list):
                body['Category IDs'] = category_id
        if category_name is not None:
            if isinstance(category_name, str):
                body['Category Names'] = [category_name]
            elif isinstance(category_name, list):
                body['Category Names'] = category_name
        result = self.transaction_request(url_suffix=url, method=method, body=body)

        return result

    def list_categories(self, all: bool) -> dict[str, Any]:
        """List categories know to Forcepoint.

        Args:
            all (bool): Include all categories including those created in Forcepoint Security Manager.

        Returns:
            dict[str, Any]: _description_
        """
        if all:
            url = "/categories/all"
        else:
            url = "/categories"
        result = self._http_request(url_suffix=url, method="GET")

        return result

    def get_category(self, category_id: Optional[str], category_name: Optional[str]) -> dict[str, Any]:
        """Get category details.

        Args:
            category_id (Optional[str]): The category id.
            category_name (Optional[str]): The category name.

        Returns:
            dict[str, Any]: _description_
        """
        url = "/categories"
        params = {}
        if category_id is not None:
            params['catid'] = category_id
        if category_name is not None:
            params['catname'] = category_name
        result = self._http_request(url_suffix=url, method="GET",params=params)

        return result

    def add_address(self, address: str, address_type: str) -> dict[str, Any]: #TODO
        """Adds an address to Forcepoint.

        Args:
            address (str): The IP address or range to add.
            address_type (str): The type of the address, either "IP" or "Range".

        Returns:
            dict[str, Any]: _description_
        """
        url = "/addresses"
        body = {
            "address": address,
            "type": address_type,
        }
        result = self.transaction_request(url_suffix=url, method="POST", body=body)

        return result
    
    def delete_address(self, address_id: str) -> dict[str, Any]: #TODO
        """Deletes an address from Forcepoint.

        Args:
            address_id (str): The ID of the address to delete.

        Returns:
            dict[str, Any]: _description_
        """
        url = "/addresses/delete"
        method = "POST"
        body = {
            "Address IDs": [address_id],
        }
        result = self.transaction_request(url_suffix=url, method=method, body=body)

        return result

# """ HELPER FUNCTIONS """


# """ COMMAND FUNCTIONS """


# TODO: ADD additional command functions that translate XSOAR inputs/outputs to Client
def add_category_command(client: Client, args: dict[str, Any]) -> CommandResults:
    """Adds a new category using Demisto command arguments.

    Args:
        client (Client): The Forcepoint API client.
        args (dict[str, Any]): Demisto command arguments.

    Raises:
        ValueError: If the category name is not provided.

    Returns:
        CommandResults: _description_
    """
    category_name = args.get("category_name", None)
    category_description = args.get("category_description", None)
    parent_category_id = args.get("parent_category_id", None)
    if not category_name:
        raise ValueError("category_name is required")
    result = client.add_category(category_name, category_description, parent_category_id)
    return CommandResults(
        outputs_prefix="Forcepoint.Category",
        outputs_key_field="id",
        outputs=result,
    )


def list_categories_command(client: Client, args: dict[str, Any]) -> CommandResults:
    all_call = argToBoolean(args.get("all", False))
    result = client.list_categories(all=all_call)
    return CommandResults(
        outputs_prefix="Forcepoint.Category",
        outputs_key_field="id",
        outputs=result,
    )


def delete_category_command(client: Client, args: dict[str, Any]) -> CommandResults:
    category_id = args.get("category_id")
    if category_id is None:
        raise ValueError("category_id is required")
    result = client.delete_category(category_id)
    return CommandResults(
        outputs_prefix="Forcepoint.Category",
        outputs_key_field="id",
        outputs=result,
    )


def get_category_command(client: Client, args: dict[str, Any]) -> CommandResults:
    category_id = args.get("category_id", None)
    if category_id is None:
        raise ValueError("category_id is required")
    result = client.get_category(category_id)
    return CommandResults(
        outputs_prefix="Forcepoint.Category",
        outputs_key_field="id",
        outputs=result,
    )


def add_address_command(client: Client, args: dict[str, Any]) -> CommandResults:
    address = args.get("address", None)
    address_type = args.get("address_type", None)
    if address is None or address_type is None or address == "" or address_type == "":
        raise ValueError("Option address and address_type are required")
    result = client.add_address(address, address_type)
    return CommandResults(
        outputs_prefix="Forcepoint.Address",
        outputs_key_field="id",
        outputs=result,
    )


def delete_address_command(client: Client, args: dict[str, Any]) -> CommandResults:
    address_id = args.get("address_id", None)
    if address_id is None:
        raise ValueError("address_id is required")
    result = client.delete_address(address_id)
    return CommandResults(
        outputs_prefix="Forcepoint.Address",
        outputs_key_field="id",
        outputs=result,
    )

def get_status_command(client: Client, args: dict[str, Any]) -> CommandResults:
    """Returns the current status of the Forcepoint blade.

    Args:
        client (Client): The Forcepoint API Client.
        args (dict[str, Any]): Demisto command arguments.

    Returns:
        CommandResults: _description_
    """
    result = client.get_status()
    return CommandResults(
        outputs_prefix="Forcepoint.Status",
        outputs_key_field="id",
        outputs=result,
    )

def test_module_command(client: Client, args: dict[str, Any]) -> str:
    return "ok"


def main():
    """main function, parses params and runs command functions"""

    # TODO: make sure you properly handle authentication
    # api_key = params.get('apikey')

    params = demisto.params()
    username = params.get("credentials", {}).get("identifier")
    password = params.get("credentials", {}).get("password")
    base_url = urljoin(params.get("url"), f":{params.get('port')}/api/web/v1")
    verify_certificate = not argToBoolean(params.get("insecure", False))
    proxy = argToBoolean(params.get("proxy", False))
    commands = {
        "forcepoint-add-category": add_category_command,
        "forcepoint-list-categories": list_categories_command,
        "forcepoint-delete-category": delete_category_command,
        "forcepoint-get-category": get_category_command,
        "forcepoint-add-address": add_address_command,
        "forcepoint-delete-address": delete_address_command,
        "forcepoint-get-status": get_status_command,
    }
    command = demisto.command()
    demisto.debug(f"Command being called is {command}")
    try:
        headers: dict[str, str] = {"authorization": f"Basic {b64encode(f'{username}:{password}'.encode()).decode()}"}

        client = Client(base_url=base_url, verify=verify_certificate, headers=headers, proxy=proxy)
        args = demisto.args()
        if command == "test-module":
            result = test_module_command(client, args)
        elif command in commands:
            result = commands[command](client, args)
        else:
            raise NotImplementedError(f"Command {command} is not implemented")

        return_results(result)
    # Log exceptions and return errors
    except Exception as e:
        return_error(f"Failed to execute {command} command.\nError:\n{str(e)}")


if __name__ in ("__main__", "__builtin__", "builtins"):  # pragma: no cover
    main()
