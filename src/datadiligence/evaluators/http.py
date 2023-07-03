"""
This module contains the HttpEvaluator class.
"""

from .base import Evaluator
from ..rules import XRobotsTagHeader, TDMRepHeader


class HttpEvaluator(Evaluator):
    """
    HTTP Evaluator class. Loads XRobotsTagHeader rule by default.
    """
    name = "http"

    def __init__(self, user_agent=None, respect_robots=True, respect_tdmrep=True):
        """Load the default rules.

        Args:
            user_agent (str): The user agent to pass on to the rules.
            respect_robots (bool): Whether to respect the X-Robots-Tag header.
            respect_tdmrep (bool): Whether to respect the TDMRep header.
        """
        super().__init__()
        if respect_robots:
            self.rules.append(XRobotsTagHeader(user_agent))
        if respect_tdmrep:
            self.rules.append(TDMRepHeader())
