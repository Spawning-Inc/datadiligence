
from unittest import TestCase
import datadiligence as dd
import datadiligence.exceptions
from samples.custom import CustomEvaluator, CustomRule
import urllib
import time

# starting local server to confirm api response
from werkzeug.serving import make_server
from server.app import app
import threading
import os
from datadiligence.rules import SpawningAPI


class BootstrapTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = make_server('localhost', 5001, app)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.start()
        time.sleep(2)

        # set up a basic env var so most tests succeed
        if os.environ.get(SpawningAPI.API_KEY_ENV_VAR, None) is None:
            os.environ[SpawningAPI.API_KEY_ENV_VAR] = "SAMPLE_KEY"

        cls.urls = [
            "https://www.spawning.ai",
            "https://www.shutterstock.com",
            "https://open.ai",
            "https://www.google.com",
            "https://laion.ai",
            "https://spawning.ai/éxample.png"
        ]

    def test_exceptions(self):
        self.assertRaises(dd.exceptions.EvaluatorNotRegistered, dd.is_allowed, "x")
        self.assertRaises(dd.exceptions.NotEvaluator, dd.register_evaluator, None, "y")

        custom_evaluator = dd.Evaluator()
        dd.register_evaluator(custom_evaluator, "custom0")
        self.assertRaises(dd.exceptions.EvaluatorAlreadyRegistered,
                          dd.register_evaluator, custom_evaluator, "custom0")
        self.assertRaises(dd.exceptions.EvaluatorNotRegistered, dd.deregister_evaluator, "not-used")
        self.assertRaises(dd.exceptions.EvaluatorNotRegistered, dd.get_evaluator, "not-used")
        self.assertRaises(dd.exceptions.DefaultEvaluatorNotFound, dd.is_allowed, example="not-used")

        with self.assertRaises(datadiligence.exceptions.EvaluatorNotRegistered):
            dd.filter_allowed(name="none", urls=[])

        with self.assertRaises(datadiligence.exceptions.DefaultEvaluatorNotFound):
            dd.filter_allowed(args=None)

    def test_load_defaults(self):
        # reset evaluators
        for key in dd.list_evaluators():
            dd.deregister_evaluator(key)

        dd.load_defaults()
        self.assertTrue(isinstance(dd.get_evaluator("preprocess"), dd.PreprocessEvaluator))
        self.assertTrue(isinstance(dd.get_evaluator("postprocess"), dd.PostprocessEvaluator))
        self.assertTrue(isinstance(dd.get_evaluator("file"), dd.FileEvaluator))
        self.assertEqual(len(dd.list_evaluators()), 3)

    def test_register_evaluator(self):
        custom_evaluator = dd.Evaluator()
        dd.register_evaluator(custom_evaluator, "custom1")
        self.assertEqual(dd.get_evaluator("custom1"), custom_evaluator)

    def test_deregister_evaluator(self):
        custom_evaluator = dd.Evaluator()
        dd.register_evaluator(custom_evaluator, "custom3")
        self.assertEqual(dd.get_evaluator("custom3"), custom_evaluator)
        dd.deregister_evaluator("custom3")
        self.assertRaises(dd.exceptions.EvaluatorNotRegistered, dd.deregister_evaluator, "custom3")

    def test_is_allowed(self):
        custom_evaluator = CustomEvaluator()
        custom_evaluator.add_rule(CustomRule())
        dd.register_evaluator(custom_evaluator, "custom2")
        self.assertFalse(dd.is_allowed("custom2", sample="www.google.com"))
        self.assertTrue(dd.is_allowed("custom2", sample="www.example.com"))

        dd.load_defaults()

        request = urllib.request.Request("http://localhost:5001/noai", data=None)
        with urllib.request.urlopen(request, timeout=3) as response:
            self.assertFalse(dd.is_allowed(response=response))

        # hack to reach local instance
        dd.get_evaluator("preprocess").rules[0].SPAWNING_AI_API_URL = "http://localhost:5001/opts"
        url_results = dd.is_allowed(urls=self.urls)
        self.assertEqual(len(url_results), 6)

        # with user agent arg
        url_results = dd.is_allowed(urls=self.urls, user_agent="UserAgent")
        self.assertEqual(len(url_results), 6)

        # double check C2PA is in default evaluators
        self.assertFalse(dd.is_allowed(path="tests/resources/sample_c2pa.png"))

        dd.load_defaults()

    def test_filter_allowed(self):

        dd.load_defaults()

        request = urllib.request.Request("http://localhost:5001/noai", data=None)
        with urllib.request.urlopen(request, timeout=3) as response:
            self.assertFalse(dd.is_allowed(response=response))

        # hack to reach local instance
        dd.get_evaluator("preprocess").rules[0].SPAWNING_AI_API_URL = "http://localhost:5001/opts"
        filtered_urls = dd.filter_allowed(urls=self.urls)
        self.assertEqual(len(filtered_urls), 3)
        self.assertEqual(filtered_urls[0], self.urls[1])
        self.assertEqual(filtered_urls[1], self.urls[2])
        self.assertEqual(filtered_urls[2], self.urls[5])

        # with user agent arg
        filtered_urls = dd.filter_allowed(urls=self.urls, user_agent="UserAgent")
        self.assertEqual(len(filtered_urls), 3)
        self.assertEqual(filtered_urls[0], self.urls[1])
        self.assertEqual(filtered_urls[1], self.urls[2])
        self.assertEqual(filtered_urls[2], self.urls[5])

        dd.load_defaults()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server_thread.join()
