"""Postprocess evaluator module."""

from .base import Evaluator
from ..rules import XRobotsTagHeader


class PostprocessEvaluator(Evaluator):
    """
    Postprocess Evaluator class. Loads XRobotsTagHeader rule by default.
    """
    name = "postprocess"

    def __init__(self, user_agent=None):
        super().__init__()
        self.add_rule(XRobotsTagHeader(user_agent))

    def is_allowed(self, **kwargs):
        """Check if the headers are allowed based on the rules in this evaluator.

        Args:
            **response (http.client.HTTPResponse|requests.Response): The response object.
            **headers (dict|http.client.HTTPMessage): The headers dictionary.

        Returns:
            bool: True if the content is allowed, False otherwise.
        """
        for rule in self.rules:
            if rule.is_ready() and not rule.is_allowed(**kwargs):
                return False
        return True
