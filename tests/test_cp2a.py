
from unittest import TestCase
from datadiligence.rules import C2PAMetadataRule


class C2PATests(TestCase):

    def test_c2pa(self):
        rule = C2PAMetadataRule()
        self.assertFalse(rule.is_ready())
        self.assertTrue(rule.is_allowed(body=None))
