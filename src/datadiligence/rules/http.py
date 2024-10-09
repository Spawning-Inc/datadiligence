"""
Rules to manage validation using HTTP properties
"""

from ..exceptions import XRobotsTagNoParam, TDMRepNoParam
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
            header_value = self.get_header_value(headers, self.HEADER_NAME)
        elif response:
            header_value = self.get_header_value_from_response(response, self.HEADER_NAME)
        elif url:
            response = self._handle_url(url)
            header_value = self.get_header_value(response.headers, self.HEADER_NAME)
        else:
            raise XRobotsTagNoParam()

        return self._eval_header_value(header_value, **kwargs)

    def _eval_header_value(self, header_value, user_agent=None, **kwargs):
        """
        Evaluate the header value to determine if the user agent is allowed to access the resource.

        Args:
            header_value (str): The header value.
            user_agent (str): Override user agent to use when making requests to the Spawning AI API.

        Returns:
            bool: True if the user agent is allowed to access the resource, False otherwise.
        """
        if not header_value:
            return True

        # if we have a specific user agent
        if not user_agent:
            user_agent = self.user_agent

        # check if blocking all user agents
        for value in header_value.split(","):
            if value.strip() in self.disallowed_headers:
                return False

            # check if blocking specific user agent
            if user_agent:
                ua_values = value.split(":")
                if len(ua_values) == 2 and ua_values[0].strip() == user_agent \
                        and ua_values[1].strip() in self.disallowed_headers:
                    return False

        return True


class TDMRepHeader(HttpRule):
    """
    This class wraps logic to evaluate the TDM Reservation Protocol headers: https://www.w3.org/2022/tdmrep/.
    """
    HEADER_NAME = "tdm-reservation"

    def __init__(self):
        """Create a new TDMRepHeaders instance."""
        super().__init__()

    def is_allowed(self, url=None, response=None, headers=None, **kwargs):
        """Check if the tdm-rep header allows access to the resource without a policy.

        Args:
            url: (str): The URL of the resource.
            response (http.client.HTTPResponse|requests.Response, optional): The response object. Defaults to None
            headers (dict|http.client.HTTPMessage, optional): The headers dictionary. Defaults to None.

        Returns:
            bool: True if access is allowed for the resource, False otherwise.
        """

        if headers:
            header_value = self.get_header_value(headers, self.HEADER_NAME)
        elif response:
            header_value = self.get_header_value_from_response(response, self.HEADER_NAME)
        elif url:
            response = self._handle_url(url)
            header_value = self.get_header_value(response.headers, self.HEADER_NAME)
        else:
            raise TDMRepNoParam()

        return self._eval_header_value(header_value, **kwargs)

    def _eval_header_value(self, header_value, **kwargs):
        """
        Evaluate the header value to determine if the resource permits anonymous access.

        Args:
            header_value (str): The header value.

        Returns:
            bool: True if resource allows access without a policy, False otherwise.
        """

        if not header_value:
            return True

        return header_value.strip() != "1"
