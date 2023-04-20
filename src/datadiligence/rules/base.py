"""
This module contains the base rule classes.
"""


class Rule:
    """
    Base class for rules. is_allowed and is_ready must be implemented.
    """

    def is_allowed(self, **kwargs):
        """Check if the request is allowed. Must be implemented.

        Args:
            **kwargs: Arbitrary keyword arguments to read args from.
        """
        raise NotImplementedError

    def is_ready(self):
        """Check if the rule is ready to be used."""
        raise NotImplementedError


class BulkRule(Rule):
    """
    Base class for bulk rules. filter_allowed and is_ready must be implemented.
    """

    def filter_allowed(self, **kwargs):
        """Filter a list of entries based on the rules in this evaluator."""
        raise NotImplementedError


class HttpRule(Rule):
    def __init__(self, user_agent=None):
        """Initialize the rule with a user agent.

        Args:
            user_agent (str): The user agent to pass on to the rules.
        """
        super().__init__()
        self.user_agent = user_agent
