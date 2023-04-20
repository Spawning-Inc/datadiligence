"""
This module contains the HttpEvaluator class.
"""

from .base import Evaluator
from ..rules import XRobotsTagHeader, SpawningAPI


class HttpEvaluator(Evaluator):
    """
    HTTP Evaluator class. Loads XRobotsTagHeader and SpawningAPI rules by default.
    """
    name = "http"

    def __init__(self, user_agent=None, respect_robots=True, respect_spawning=True):
        """Load the default rules.

        Args:
            user_agent (str): The user agent to pass on to the rules.
            respect_robots (bool): Whether to respect the X-Robots-Tag header.
            respect_spawning (bool): Whether to respect the spawning API.
        """
        super().__init__()
        if respect_robots:
            self.rules.append(XRobotsTagHeader(user_agent))
        if respect_spawning:
            self.rules.append(SpawningAPI(user_agent))
