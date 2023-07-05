"""
This module wraps HTTP calls to the Spawning AI API.
See Spawning API documentation here: https://opts-api.spawningaiapi.com/docs.

"""

import requests
import requests.utils
from requests.adapters import HTTPAdapter, Retry
import aiohttp
import asyncio
import os
from ..exceptions import SpawningAIAPIError, SpawningNoParam
from .base import BulkRule
from concurrent.futures import ThreadPoolExecutor, wait
import itertools
import sys


class SpawningAPI(BulkRule):
    """
    This class wraps basic requests to the Spawning API.
    """

    API_KEY_ENV_VAR = "SPAWNING_OPTS_KEY"
    MAX_CHUNK_SIZE = 10000
    SPAWNING_AI_API_URL = "https://opts-api.spawningaiapi.com/api/v2/query/urls/"
    DEFAULT_TIMEOUT = 20
    MAX_CONCURRENT_REQUESTS = 10

    def __init__(self, user_agent=None, chunk_size=MAX_CHUNK_SIZE, timeout=DEFAULT_TIMEOUT, max_retries=5,
                 max_concurrent_requests=MAX_CONCURRENT_REQUESTS):
        """Create a new SpawningAPI BulkRole instance.

        Args:
            user_agent (str): The user agent to use when making requests to the Spawning AI API.
            chunk_size (int): The maximum number of URLs to submit in a single request.
            timeout (int): The maximum number of seconds to wait for a response from the Spawning AI API.
            max_retries (int): The maximum number of times to retry a request to the Spawning AI API.
            max_concurrent_requests (int): The maximum number of concurrent requests to the Spawning AI API.
        """

        super().__init__()

        # check if API key is installed
        self.api_key = os.environ.get(SpawningAPI.API_KEY_ENV_VAR, "")
        if not self.api_key:
            print(
                "Spawning API key not found. Please set your API key to the environment variable "
                + SpawningAPI.API_KEY_ENV_VAR
            )

        if user_agent is None:
            self.user_agent = requests.utils.default_user_agent()
        else:
            self.user_agent = user_agent

        self.max_retries = max_retries

        if chunk_size > self.MAX_CHUNK_SIZE or chunk_size is None:
            chunk_size = self.MAX_CHUNK_SIZE
        self.chunk_size = chunk_size

        if timeout < 0 or timeout is None:
            timeout = self.DEFAULT_TIMEOUT
        self.timeout = timeout

        if max_concurrent_requests <= 0 \
                or max_concurrent_requests > self.MAX_CONCURRENT_REQUESTS \
                or max_concurrent_requests is None:
            max_concurrent_requests = self.MAX_CONCURRENT_REQUESTS
        self.max_concurrent_requests = max_concurrent_requests

    def filter_allowed(self, urls=None, url=None, **kwargs):
        """Submit a list of URLs to the Spawning AI API.
        Args:
            urls (list): A list of URLs to submit.
            url (str): A single URL to submit.
        Returns:
            list: A list containing the allowed urls of the submission.
        """
        if urls is None:
            if url is not None:
                urls = [url]
            else:
                raise SpawningNoParam()

        results = []

        # thread pool executor to submit chunks in parallel
        with ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as executor:
            futures = [executor.submit(self._submit_chunk, chunk) for chunk in self._chunk(urls)]
            wait(futures)

            for future in futures:
                results.extend([response_url["url"] for response_url in future.result() if not response_url["optOut"]])

        return results

    def is_allowed(self, urls=None, url=None, **kwargs):
        """Submit a list of URLs to the Spawning AI API.
        Args:
            urls (list): A list of URLs to submit.
            url (str): A single URL to submit.
        Returns:
            list: A list containing booleans, indicating if a respective URL is allowed.
        """
        if urls is None:
            if url is not None:
                urls = [url]
            else:
                raise SpawningNoParam()

        results = []

        # thread pool executor to submit chunks in parallel
        with ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as executor:
            futures = [executor.submit(self._submit_chunk, chunk) for chunk in self._chunk(urls)]
            wait(futures)

            for future in futures:
                results.extend([not response_url["optOut"] for response_url in future.result()])

        return results

    async def filter_allowed_async(self, urls=None, url=None, **kwargs):
        """Submit a list of URLs to the Spawning AI API.

        Args:
            urls (list): A list of URLs to submit.
            url (str): A single URL to submit.

        Returns:
            list: A list containing the allowed URLs.

        """
        if urls is None:
            if url is not None:
                urls = [url]
            else:
                raise SpawningNoParam()

        results = await self._submit_chunks_async(urls)
        results = [response_url["url"] for response_url in results if not response_url["optOut"]]
        return results

    async def is_allowed_async(self, urls=None, url=None, **kwargs):
        """Submit a list of URLs to the Spawning AI API.

        Args:
            urls (list): A list of URLs to submit.
            url (str): A single URL to submit.

        Returns:
            list: A list of boolean values indicating if a URL is allowed to be used or not.

        """
        if urls is None:
            if url is not None:
                urls = [url]
            else:
                raise SpawningNoParam()

        results = await self._submit_chunks_async(urls)
        results = [not response_url["optOut"] for response_url in results]
        return results

    def is_ready(self):
        """Check if the Spawning AI API is ready to be used. This is determined by whether or not the API key is set.
        Returns:
            bool: True if the API key is set, False otherwise.
        """
        return bool(self.api_key)

    def _chunk(self, urls):
        """Generator to split a list of URLs into chunks.

        Args:
            urls (list): A list of URLs to split into chunks.

        Yields:
            list: A list of URLs.

        """

        for i in range(0, len(urls), self.chunk_size):
            yield urls[i:i + self.chunk_size]

    async def _submit_chunks_async(self, urls):
        """Submit a list of URLs to the Spawning AI API.

        Args:
            urls (list): A list of URLs to submit.

        Returns:
            list: A list containing the result dicts of the submission.

        """

        # build out http tasks
        tasks = []
        headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "text/plain",
            "Authorization": "API " + self.api_key
        }
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        async with aiohttp.ClientSession(headers=headers) as session:
            # if 3.6 or earlier, run create_task from loop
            if sys.version_info < (3, 7):
                loop = asyncio.get_event_loop()
                for chunk in self._chunk(urls):
                    tasks.append(loop.create_task(self._submit_chunk_async(session, semaphore, chunk)))
            else:
                for chunk in self._chunk(urls):
                    tasks.append(asyncio.create_task(self._submit_chunk_async(session, semaphore, chunk)))

            results = await asyncio.gather(*tasks)

        # flatten
        return [response_url for response_url in itertools.chain(*results)]

    async def _submit_chunk_async(self, session, semaphore, urls):
        """Submit a chunk of URLs to the Spawning AI API asynchronously.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use.
            urls (list): A list of URLs to submit.

        Returns:
            list: A list containing the result dicts of the submission.

        """

        # limit concurrent requests
        async with semaphore:
            # create body
            body = "\n".join(urls).encode("utf-8")

            # make request
            async with session.post(self.SPAWNING_AI_API_URL, data=body) as response:
                try:
                    if response.status != 200:
                        raise SpawningAIAPIError("Spawning AI API returned a non-200 status code: " +
                                                 str(response.status))

                    results = await response.json()
                    return results.get("urls", [])
                except Exception as e:
                    raise SpawningAIAPIError(e)

    def _submit_chunk(self, urls):
        """Submit a chunk of URLs to the Spawning AI API.
        Args:
            urls (list): A list of URLs to submit.
        Returns:
            list: A list containing the result dicts of the submission.
        """

        # create body
        body = "\n".join(urls).encode("utf-8")

        # make request
        try:
            s = requests.Session()
            retries = Retry(total=self.max_retries, backoff_factor=0.1, status_forcelist=[429, 500, 502, 503, 504])
            s.mount("https://", HTTPAdapter(max_retries=retries))
            response = s.post(self.SPAWNING_AI_API_URL,
                              data=body,
                              headers={
                                  "User-Agent": self.user_agent,
                                  "Content-Type": "text/plain",
                                  "Authorization": "API " + self.api_key
                              },
                              timeout=self.timeout
                              )
            if response.status_code != 200:
                raise SpawningAIAPIError("Spawning AI API returned a non-200 status code: " + str(response.status_code))

            return response.json().get("urls", [])
        except Exception as e:
            raise SpawningAIAPIError(e)
