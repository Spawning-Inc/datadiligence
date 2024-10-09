"""FileEvaluator evaluator module."""

from .base import Evaluator
from ..rules import C2PAMetadataRule


class FileEvaluator(Evaluator):
    """
    File Evaluator class. Loads C2PAMetadataRule rule by default.
    """
    name = "file"

    def __init__(self):
        super().__init__()
        self.add_rule(C2PAMetadataRule())

    def is_allowed(self, **kwargs):
        """Check if the headers are allowed based on the rules in this evaluator.

        Args:
            **path (str): The path of the file.

        Returns:
            bool: True if the content is allowed, False otherwise.
        """
        for rule in self.rules:
            if rule.is_ready() and not rule.is_allowed(**kwargs):
                return False
        return True
