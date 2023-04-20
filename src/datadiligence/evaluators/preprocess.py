"""
This module contains the PreprocessEvaluator class.
"""

from .base import Evaluator
from ..rules import SpawningAPI, BulkRule


class PreprocessEvaluator(Evaluator):
    """
    Preprocess Evaluator class. Loads SpawningAPI rule by default.
    """
    name = "preprocess"

    def __init__(self, user_agent=None):
        """ Load the default rules.

        Args:
            user_agent (str): The user agent to pass on to the rules.

        """
        super().__init__()
        self.add_rule(SpawningAPI(user_agent))

    def add_rule(self, rule):
        """Add a rule to the evaluator."""
        if issubclass(rule.__class__, BulkRule):
            self.rules.append(rule)

    def get_allowed(self, urls=None):
        """Filter a list of urls based on the rules in this evaluator.

        Args:
            urls (list): A list of urls to filter.

        Returns:
            list: A list of urls that are allowed.
        """

        if urls is None:
            return []

        allowed = urls
        for rule in self.rules:
            # if everything is already filtered out, stop
            if len(allowed) == 0:
                break
            if rule.is_ready():
                allowed = rule.get_allowed(urls=allowed)

        return allowed

    def is_allowed(self, **kwargs):
        return self.get_allowed(**kwargs)
