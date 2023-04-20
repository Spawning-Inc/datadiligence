
from unittest import TestCase
from datadiligence.utils import get_url
import requests


class TestUtils(TestCase):

    def test_get_url(self):
        response = get_url("http://www.google.com")
        self.assertTrue(response.ok)

        self.assertRaises(Exception, get_url, "wesvadsvrwabg")

        user_agent = requests.utils.default_user_agent()
        response = get_url("http://www.google.com", user_agent=user_agent)
        self.assertTrue(response.ok)
