"""
This module contains the C2PA Metadata Rule class.
"""

from .base import HttpRule


# TODO: Implement, either with wrapper for CLI or python implementation of C2PA
class C2PAMetadataRule(HttpRule):
    """
    This class wraps calls to the Adobe Content Authenticity Initiative c2pa tool. TODO.
    """

    def is_allowed(self, url=None, response=None, body=None, **kwargs):
        return True

    def is_ready(self):
        return False
