"""
This module contains the base Evaluator class.
"""
from ..rules import Rule


class Evaluator:
    """
    Base class for evaluators. is_allowed must be implemented.
    """
    name = "base_evaluator"

    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        """Add a rule to the evaluator."""
        if isinstance(rule, Rule):
            self.rules.append(rule)

    def is_allowed(self, **kwargs):
        """Check each rule to see if the request is allowed.

        Args:
            **kwargs (any): Keyword args to pass to rule

        Returns:
            bool: True if the content is allowed, False otherwise.
        """
        for rule in self.rules:
            if rule.is_ready() and not rule.is_allowed(**kwargs):
                return False
        return True

    def filter_allowed(self, **kwargs):
        """Filter a list of entries based on the rules in this evaluator."""
        raise NotImplementedError
