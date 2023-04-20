"""
Rules to manage validation using HTTP properties
"""

import http.client
import requests
from ..exceptions import XRobotsTagNoParam, XRobotsTagUnknownHeaderObject, XRobotsTagUnknownResponseObject
from ..utils import get_url
from .base import HttpRule


class XRobotsTagHeader(HttpRule):
    """
    This class wraps logic to read the X-Robots-Tag header.
    """
    AI_DISALLOWED_VALUES = ["noai", "noimageai"]
    INDEX_DISALLOWED_VALUES = ["noindex", "none", "noimageindex", "noai", "noimageai"]
    HEADER_NAME = "X-Robots-Tag"

    def __init__(self, user_agent=None, respect_noindex=False):
        """Create a new XRobotsTagHeader instance.

        Args:
            user_agent (str): The user agent to use when making requests to the Spawning AI API.
            respect_noindex (bool): If True, index rules will be respected alongside AI rules.
        """
        super().__init__(user_agent=user_agent)

        # index rules aren't for AI, so we ignore them by default.
        # They could have been delivered/found by any number of other means, even for internal use
        if respect_noindex:
            self.disallowed_headers = self.INDEX_DISALLOWED_VALUES
        else:
            self.disallowed_headers = self.AI_DISALLOWED_VALUES

    def is_allowed(self, url=None, response=None, headers=None, **kwargs):
        """Check if the X-Robots-Tag header allows the user agent to access the resource.

        Args:
            url: (str): The URL of the resource.
            response (http.client.HTTPResponse|requests.Response, optional): The response object. Defaults to None
            headers (dict|http.client.HTTPMessage, optional): The headers dictionary. Defaults to None.

        Returns:
            bool: True if the user agent is allowed to access the resource, False otherwise.
        """

        if headers:
            header_value = self._handle_headers(headers)
        elif response:
            header_value = self._handle_response(response)
        elif url:
            response = self._handle_url(url)
            header_value = self._handle_headers(response.headers)
        else:
            raise XRobotsTagNoParam()

        return self._eval_header_value(header_value)

    def is_ready(self):
        """
        This rule is always ready.
        """
        return True

    def _eval_header_value(self, header_value):
        """
        Evaluate the header value to determine if the user agent is allowed to access the resource.

        Args:
            header_value (str): The header value.

        Returns:
            bool: True if the user agent is allowed to access the resource, False otherwise.
        """
        if not header_value:
            return True

        # check if blocking all user-agents
        if header_value in self.disallowed_headers:
            return False

        # if we have a specific user agent
        if self.user_agent:
            for value in header_value.split(","):
                if value.strip() in self.disallowed_headers:
                    return False

                # check user-agent directives
                ua_values = value.split(":")
                if len(ua_values) == 2 and ua_values[0].strip() == self.user_agent \
                        and ua_values[1].strip() in self.disallowed_headers:
                    return False

        return True

    def _handle_response(self, response):
        """
        Handle the response object to get the header value.

        Args:
            response (http.client.HTTPResponse|requests.Response): The response object.

        Returns:
            str: The header value.
        """
        if type(response) == http.client.HTTPResponse:
            header_value = response.getheader(XRobotsTagHeader.HEADER_NAME, "")
        elif type(response) == requests.Response:
            header_value = response.headers.get(XRobotsTagHeader.HEADER_NAME, "")
        else:
            raise XRobotsTagUnknownResponseObject()
        return header_value

    def _handle_headers(self, headers):
        """
        Handle the headers object to get the header value.

        Args:
            headers (dict|http.client.HTTPMessage|CaseInsensitiveDict): The headers object.

        Returns:
            str: The header value.
        """
        if type(headers) == dict or type(headers) == requests.structures.CaseInsensitiveDict:
            header_value = headers.get(XRobotsTagHeader.HEADER_NAME, "")
        elif type(headers) == list and len(headers) > 0 and type(headers[0]) == tuple:
            header_value = dict(headers).get(XRobotsTagHeader.HEADER_NAME, "")
        elif type(headers) == http.client.HTTPMessage:
            header_value = headers.get(XRobotsTagHeader.HEADER_NAME, "")
        else:
            raise XRobotsTagUnknownHeaderObject()

        return header_value

    def _handle_url(self, url):
        """
        If given a raw URL, submit a request to get the image.

        Args:
            url (str): The URL of the resource.

        Returns:
            requests.Response: Response object.
        """
        return get_url(url, user_agent=self.user_agent)
