import requests
import urllib.request
from unittest import TestCase
import datadiligence as dd
from datadiligence import HttpEvaluator, PreprocessEvaluator, PostprocessEvaluator
from datadiligence.rules import SpawningAPI, XRobotsTagHeader
import time
import os
from samples.custom import CustomEvaluator, NotReadyRule, CustomRule2

# starting local server to echo back headers
from werkzeug.serving import make_server
from server.app import app
import threading
import datadiligence.exceptions


class EvaluatorTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = make_server('localhost', 5001, app)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.start()
        time.sleep(1)  # wait for server to start

    def test_http_evaluator(self):
        http_evaluator = HttpEvaluator()
        self.assertTrue(len(http_evaluator.rules) > 0)

        response = requests.get("http://localhost:5001/noai")
        self.assertFalse(http_evaluator.is_allowed(response=response))
        self.assertFalse(http_evaluator.is_allowed(headers=response.headers))

        request = urllib.request.Request("http://localhost:5001/noai", data=None)
        with urllib.request.urlopen(request, timeout=3) as response:
            self.assertFalse(http_evaluator.is_allowed(response=response))
            self.assertFalse(http_evaluator.is_allowed(headers=response.headers))

        response = requests.get("http://localhost:5001/ai")
        self.assertTrue(http_evaluator.is_allowed(response=response))
        self.assertTrue(http_evaluator.is_allowed(headers=response.headers))

        http_evaluator_2 = HttpEvaluator(respect_robots=False, respect_tdmrep=False)
        self.assertEqual(len(http_evaluator_2.rules), 0)

    def test_custom_evaluator(self):
        # custom evaluator
        custom_evaluator = CustomEvaluator()
        custom_rule = CustomRule2()
        not_ready_rule = NotReadyRule()
        custom_evaluator.add_rule(custom_rule)
        custom_evaluator.add_rule(not_ready_rule)
        self.assertFalse(custom_evaluator.is_allowed(url="https://www.google.com"))
        self.assertTrue(custom_evaluator.is_allowed(url="https://www.spawning.ai"))

        len_rules = len(custom_evaluator.rules)
        custom_evaluator.add_rule(None)
        self.assertEqual(len(custom_evaluator.rules), len_rules)

    def test_bulk_evaluator(self):
        bulk_evaluator = PreprocessEvaluator()
        bulk_evaluator.rules = []

        # patch to point to local dev
        if os.environ.get(SpawningAPI.API_KEY_ENV_VAR, None) is None:
            os.environ[SpawningAPI.API_KEY_ENV_VAR] = "SAMPLE_KEY"
        spawning_api = SpawningAPI(user_agent="spawningbot")
        spawning_api.SPAWNING_AI_API_URL = "http://localhost:5001/opts"

        self.assertEqual(len(bulk_evaluator.rules), 0)
        bulk_evaluator.add_rule(spawning_api)
        self.assertEqual(len(bulk_evaluator.rules), 1)

        urls = bulk_evaluator.filter_allowed([
            "https://www.spawning.ai",
            "https://www.shutterstock.com",
            "https://open.ai",
            "https://www.google.com",
            "https://laion.ai",
            "https://www.youtube.com",
        ])
        self.assertEqual(len(urls), 3)

        urls = bulk_evaluator.filter_allowed(urls=[
            "https://www.spawning.ai",
            "https://www.shutterstock.com",
            "https://open.ai",
            "https://www.google.com",
            "https://laion.ai",
            "https://www.youtube.com",
        ])
        self.assertEqual(len(urls), 3)

        self.assertEqual(len(bulk_evaluator.rules), 1)
        bulk_evaluator.add_rule(None)
        self.assertEqual(len(bulk_evaluator.rules), 1)

        bulk_evaluator = PreprocessEvaluator()
        self.assertTrue(len(bulk_evaluator.rules) > 0)

        self.assertEqual(bulk_evaluator.filter_allowed([]), [])
        self.assertEqual(bulk_evaluator.filter_allowed(None), [])

        self.assertEqual(bulk_evaluator.is_allowed(), [])

    def test_bulk_evaluator_ready_state(self):
        b = PreprocessEvaluator()
        b.rules = []
        del os.environ[SpawningAPI.API_KEY_ENV_VAR]
        spawning_rule = SpawningAPI()

        self.assertFalse(spawning_rule.is_ready())

        b.add_rule(spawning_rule)

        urls = b.filter_allowed([
            "https://www.spawning.ai",
            "https://www.shutterstock.com",
            "https://open.ai",
            "https://www.google.com",
            "https://laion.ai",
            "https://www.youtube.com",
        ])
        self.assertEqual(len(urls), 6)

    def test_postprocessor(self):
        postprocessor = PostprocessEvaluator()
        postprocessor.rules = []
        not_ready_rule = NotReadyRule()
        custom_rule = CustomRule2()
        postprocessor.add_rule(not_ready_rule)
        postprocessor.add_rule(custom_rule)

        # custom rule is saying it's not ready, so we don't use it to evaluate
        self.assertTrue(postprocessor.is_allowed(url="http://localhost:5001/noai"))

        # but later rules still work correctly
        self.assertFalse(postprocessor.is_allowed(url="http://google.com"))

    def test_default_eval_args(self):
        """
        Testing named variables to root package evaluator routing
        """

        # http defaults
        self.assertFalse(dd.is_allowed(url="http://localhost:5001/noai"))

        # patch to point to local dev
        if os.environ.get(SpawningAPI.API_KEY_ENV_VAR, None) is None:
            os.environ[SpawningAPI.API_KEY_ENV_VAR] = "SAMPLE_KEY"
        spawning_api = SpawningAPI(user_agent="spawningbot")
        spawning_api.SPAWNING_AI_API_URL = "http://localhost:5001/opts"
        evaluator = dd.get_evaluator("preprocess")
        evaluator.rules = []
        evaluator.add_rule(XRobotsTagHeader())
        evaluator.add_rule(spawning_api)
        dd.register_evaluator(evaluator, name="preprocess", overwrite=True)

        # urls defaults
        urls = dd.filter_allowed(urls=[
            "https://www.spawning.ai",
            "https://www.shutterstock.com",
            "https://open.ai",
            "https://www.google.com",
            "https://laion.ai",
            "https://www.youtube.com",
        ])
        self.assertEqual(len(urls), 3)

        bool_urls = dd.is_allowed(urls=[
            "https://www.spawning.ai",
            "https://www.shutterstock.com",
            "https://open.ai",
            "https://www.google.com",
            "https://laion.ai",
            "https://www.youtube.com",
        ])
        self.assertFalse(bool_urls[0])
        self.assertTrue(bool_urls[1])
        self.assertTrue(bool_urls[2])
        self.assertFalse(bool_urls[3])
        self.assertFalse(bool_urls[4])
        self.assertTrue(bool_urls[5])

        # response and headers defaults
        response = requests.get("http://localhost:5001/noai")
        self.assertFalse(dd.is_allowed(response=response))
        self.assertFalse(dd.is_allowed(headers=response.headers))

        response = requests.get("http://localhost:5001/ai")
        self.assertTrue(dd.is_allowed(response=response))
        self.assertTrue(dd.is_allowed(headers=response.headers))

        urls = dd.filter_allowed(name="preprocess", urls=[
            "https://www.spawning.ai",
            "https://www.shutterstock.com",
            "https://open.ai",
            "https://www.google.com",
            "https://laion.ai",
            "https://www.youtube.com",
        ])
        self.assertEqual(len(urls), 3)

        # reload standard evaluators
        dd.load_defaults()

    def test_file_evaluator(self):
        evaluator = dd.get_evaluator("file")
        self.assertFalse(evaluator.is_allowed(path="tests/resources/sample_c2pa.png"))

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server_thread.join()
