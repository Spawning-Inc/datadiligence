
from unittest import TestCase
import datadiligence as dd
from datadiligence.rules import SpawningAPI
import datadiligence.exceptions

import os
import time

# starting local server to confirm api response
from werkzeug.serving import make_server
from server.app import app
import threading
import asyncio
from contextlib import contextmanager


@contextmanager
def run_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        asyncio.set_event_loop(None)


def run_async_in_sync(f, *args, **kwargs):
    coro = f(*args, **kwargs)
    with run_async_loop() as loop:
        result = loop.run_until_complete(coro)
    return result


class SpawningAPITest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = make_server('localhost', 5001, app)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.start()
        time.sleep(2)  # wait for server to start

        # set up a basic env var so most tests succeed
        if os.environ.get(SpawningAPI.API_KEY_ENV_VAR, None) is None:
            os.environ[SpawningAPI.API_KEY_ENV_VAR] = "SAMPLE_KEY"

        cls.rule = SpawningAPI(user_agent="spawningbot", chunk_size=2)
        cls.urls = [
            "https://www.spawning.ai",
            "https://www.shutterstock.com",
            "https://open.ai",
            "https://www.google.com",
            "https://laion.ai",
            "https://spawning.ai/éxample.png"
        ]

    def test_unicode(self):
        unicode_urls = [
            "https://spawning.ai/éxample.png",
            "https://open.ai/image.png"
        ]

        spawning_api = SpawningAPI()
        spawning_api.SPAWNING_AI_API_URL = "http://localhost:5001/unicode/success"
        results = spawning_api.filter_allowed(urls=unicode_urls)
        self.assertEqual(results, unicode_urls)

    def test_chunking(self):
        iter_num = 0
        for chunk in self.rule._chunk(self.urls):
            self.assertEqual(len(chunk), 2)
            self.assertEqual(chunk[0], self.urls[iter_num * 2])
            self.assertEqual(chunk[1], self.urls[iter_num * 2 + 1])
            iter_num += 1

    def test_init(self):
        spawning_api = SpawningAPI(chunk_size=100000, timeout=-10)
        self.assertEqual(spawning_api.chunk_size, SpawningAPI.MAX_CHUNK_SIZE)
        self.assertEqual(spawning_api.timeout, SpawningAPI.DEFAULT_TIMEOUT)

    def test_is_ready(self):
        api_key = os.environ.get(SpawningAPI.API_KEY_ENV_VAR, None)
        self.assertTrue(api_key)
        tmp_spawning = SpawningAPI()
        self.assertTrue(tmp_spawning.is_ready())

        os.environ[SpawningAPI.API_KEY_ENV_VAR+"_TMP"] = api_key
        del os.environ[SpawningAPI.API_KEY_ENV_VAR]

        api_key = os.environ.get(SpawningAPI.API_KEY_ENV_VAR, None)
        self.assertFalse(api_key)
        tmp_spawning = SpawningAPI()
        self.assertFalse(tmp_spawning.is_ready())

        os.environ[SpawningAPI.API_KEY_ENV_VAR] = os.environ[SpawningAPI.API_KEY_ENV_VAR+"_TMP"]
        del os.environ[SpawningAPI.API_KEY_ENV_VAR+"_TMP"]

    def test_filter_allowed(self):
        spawning_api = SpawningAPI(max_concurrent_requests=2000)
        spawning_api.SPAWNING_AI_API_URL = "http://localhost:5001/opts"
        allowed = spawning_api.filter_allowed(urls=self.urls)
        self.assertEqual(len(allowed), 3)
        self.assertEqual(allowed[0], self.urls[1])
        self.assertEqual(allowed[1], self.urls[2])
        self.assertEqual(allowed[2], self.urls[5])

        allowed = spawning_api.filter_allowed(urls=self.urls)
        self.assertEqual(len(allowed), 3)
        self.assertEqual(allowed[0], self.urls[1])
        self.assertEqual(allowed[1], self.urls[2])
        self.assertEqual(allowed[2], self.urls[5])

        allowed = spawning_api.filter_allowed(url=self.urls[1])
        self.assertEqual(allowed[0], self.urls[1])

        with self.assertRaises(datadiligence.exceptions.SpawningNoParam):
            spawning_api.is_allowed(args=None)

    def test_is_allowed(self):
        spawning_api = SpawningAPI()
        spawning_api.SPAWNING_AI_API_URL = "http://localhost:5001/opts"
        allowed = spawning_api.is_allowed(url=self.urls[1])
        self.assertTrue(allowed)

        results = spawning_api.is_allowed(urls=self.urls)
        self.assertEqual(len(results), 6)
        self.assertFalse(results[0])
        self.assertTrue(results[1])
        self.assertTrue(results[2])
        self.assertFalse(results[3])
        self.assertFalse(results[4])
        self.assertTrue(results[5])

    def test_with_useragent(self):
        spawning_api = SpawningAPI()
        spawning_api.SPAWNING_AI_API_URL = "http://localhost:5001/opts"

        allowed = spawning_api.is_allowed(url=self.urls[1], user_agent="New User Agent")
        self.assertTrue(allowed[1])

        spawning_api.SPAWNING_AI_API_URL = "http://localhost:5001/opts"
        allowed = spawning_api.is_allowed(url=self.urls[4], user_agent="New User Agent")
        self.assertFalse(allowed[4])

    def test_api_exception_handling(self):
        spawning_api = SpawningAPI(user_agent="spawningbot")
        spawning_api.SPAWNING_AI_API_URL = "http://localhost:5001/fail"
        self.assertRaises(dd.exceptions.SpawningAIAPIError, spawning_api.filter_allowed, self.urls)

        spawning_api.SPAWNING_AI_API_URL = "http://localhost:5001/fail2"
        self.assertRaises(dd.exceptions.SpawningAIAPIError, spawning_api.filter_allowed, self.urls)

        with self.assertRaises(dd.exceptions.SpawningNoParam):
            spawning_api.filter_allowed(arg=None)

    def test_api_exception_handling_async(self):
        spawning_api = SpawningAPI()
        spawning_api.SPAWNING_AI_API_URL = "http://localhost:5001/opts"
        allowed = run_async_in_sync(spawning_api.filter_allowed_async, urls=self.urls)
        self.assertEqual(len(allowed), 3)

        allowed = run_async_in_sync(spawning_api.filter_allowed_async, url=self.urls[0])
        self.assertEqual(len(allowed), 3)

        allowed = run_async_in_sync(spawning_api.is_allowed_async, urls=self.urls)
        self.assertEqual(len(allowed), 6)
        self.assertFalse(allowed[0])
        self.assertTrue(allowed[1])
        self.assertTrue(allowed[2])
        self.assertFalse(allowed[3])
        self.assertFalse(allowed[4])
        self.assertTrue(allowed[5])

        allowed = run_async_in_sync(spawning_api.is_allowed_async, url=self.urls[0])
        self.assertEqual(len(allowed), 6)

    def test_fails_async(self):
        spawning_api = SpawningAPI(user_agent="spawningbot")
        spawning_api.SPAWNING_AI_API_URL = "http://localhost:5001/fail"
        with self.assertRaises(dd.exceptions.SpawningAIAPIError):
            run_async_in_sync(spawning_api.filter_allowed_async, urls=self.urls)

        spawning_api.SPAWNING_AI_API_URL = "http://localhost:5001/fail2"
        with self.assertRaises(dd.exceptions.SpawningAIAPIError):
            run_async_in_sync(spawning_api.filter_allowed_async, urls=self.urls)

        with self.assertRaises(dd.exceptions.SpawningNoParam):
            run_async_in_sync(spawning_api.filter_allowed_async, arg=None)

        with self.assertRaises(dd.exceptions.SpawningNoParam):
            run_async_in_sync(spawning_api.is_allowed_async, arg=None)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server_thread.join()
