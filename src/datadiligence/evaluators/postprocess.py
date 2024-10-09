"""Postprocess evaluator module."""

from .base import Evaluator
from ..rules import XRobotsTagHeader, TDMRepHeader, C2PAMetadataRule


class PostprocessEvaluator(Evaluator):
    """
    Postprocess Evaluator class. Loads XRobotsTagHeader, TDMRepHeader, and C2PAMetadata rules by default.
    """
    name = "postprocess"

    def __init__(self, user_agent=None):
        super().__init__()
        self.add_rule(XRobotsTagHeader(user_agent))
        self.add_rule(TDMRepHeader())
        self.add_rule(C2PAMetadataRule())

    def is_allowed(self, **kwargs):
        """Check if the headers are allowed based on the rules in this evaluator.

        Args:
            **url (str): The URL of the request.
            **response (http.client.HTTPResponse|requests.Response): The response object.
            **headers (dict|http.client.HTTPMessage): The headers dictionary.

        Returns:
            bool: True if the content is allowed, False otherwise.
        """
        for rule in self.rules:
            if rule.is_ready() and not rule.is_allowed(**kwargs):
                return False
        return True
