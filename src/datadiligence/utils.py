"""
Utility functions for package.
"""
import requests


def get_url(url, user_agent=None):
    """
    Get the URL and return the response object.

    Args:
        url (str): The URL to get.
        user_agent (str): The user agent to use.

    Returns:
        requests.Response: The response object.
    """

    # TODO: add a cache so requests aren't made twice for the same URL

    if not user_agent:
        user_agent = requests.utils.default_user_agent()

    session = requests.Session()
    return session.get(url, headers={"User-Agent": user_agent}, timeout=10)
