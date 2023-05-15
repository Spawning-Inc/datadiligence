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

    def filter_allowed(self, urls=None, **kwargs):
        """Filter a list of urls based on the rules in this evaluator.

        Args:
            urls (list): A list of urls to filter.
            **kwargs: Arbitrary keyword arguments to read args from.

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
                allowed = rule.filter_allowed(urls=allowed, **kwargs)

        return allowed

    def is_allowed(self, urls=None, **kwargs):
        """
        Check if the urls are allowed.

        Args:
            urls (list): A list of urls to check.
            **kwargs: Arbitrary keyword arguments to read args from.

        Returns:
            bool: List of boolean values, respectively indicating if can be used or not
        """

        if urls is None:
            return []

        allowed = [True] * len(urls)
        for rule in self.rules:
            if rule.is_ready():
                rule_results = rule.is_allowed(urls=urls, **kwargs)

                # update allowed list to False only if rule_results is False
                allowed = [a and b for a, b in zip(allowed, rule_results)]

        return allowed
