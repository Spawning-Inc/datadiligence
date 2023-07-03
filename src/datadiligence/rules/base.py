import http.client
import requests.structures
from ..exceptions import HttpUnknownHeaderObject, HttpUnknownResponseObject
from ..utils import get_url

"""
This module contains the base rule classes.
"""


class Rule:
    """
    Base class for rules. is_allowed and is_ready must be implemented.
    """

    def is_allowed(self, **kwargs):
        """Check if the request is allowed. Must be implemented.

        Args:
            **kwargs: Arbitrary keyword arguments to read args from.
        """
        raise NotImplementedError

    def is_ready(self):
        """Check if the rule is ready to be used."""
        raise NotImplementedError


class BulkRule(Rule):
    """
    Base class for bulk rules. filter_allowed and is_ready must be implemented.
    """

    def filter_allowed(self, **kwargs):
        """Filter a list of entries based on the rules in this evaluator."""
        raise NotImplementedError


class HttpRule(Rule):
    def __init__(self, user_agent=None):
        """Initialize the rule with a user agent.

        Args:
            user_agent (str): The user agent to pass on to the rules.
        """
        super().__init__()
        self.user_agent = user_agent

    def get_header_value(self, headers, header_name):
        """
        Handle the headers object to get the header value.

        Args:
            headers (dict|http.client.HTTPMessage|CaseInsensitiveDict): The headers object.
            header_name (str): The header name.

        Returns:
            str: The header value.
        """
        if type(headers) == dict or type(headers) == requests.structures.CaseInsensitiveDict:
            header_value = headers.get(header_name, "")
        elif type(headers) == list and len(headers) > 0 and type(headers[0]) == tuple:
            header_value = dict(headers).get(header_name, "")
        elif type(headers) == http.client.HTTPMessage:
            header_value = headers.get(header_name, "")
        else:
            raise HttpUnknownHeaderObject()

        return header_value

    def is_ready(self):
        """
        These rules should always be ready.
        """
        return True

    def _handle_url(self, url):
        """
        If given a raw URL, submit a request to get the image.

        Args:
            url (str): The URL of the resource.

        Returns:
            requests.Response: Response object.
        """
        return get_url(url, user_agent=self.user_agent)

    def get_header_value_from_response(self, response, header_name):
        """
        Handle the response object to get the header value.

        Args:
            response (http.client.HTTPResponse|requests.Response): The response object.
            header_name (str): The header name.

        Returns:
            str: The header value.
        """
        if type(response) == http.client.HTTPResponse:
            header_value = response.getheader(header_name, "")
        elif type(response) == requests.Response:
            header_value = response.headers.get(header_name, "")
        else:
            raise HttpUnknownResponseObject()
        return header_value
