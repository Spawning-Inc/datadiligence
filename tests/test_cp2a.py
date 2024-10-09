
from unittest import TestCase
from datadiligence.rules import C2PAMetadataRule
import requests
import os
import c2pa


class C2PATests(TestCase):
    rule = C2PAMetadataRule()

    def setUp(self):
        # save to a tmp file
        url = "https://c2pa.org/public-testfiles/image/jpeg/adobe-20220124-C.jpg"
        response = requests.get(url)
        with open("test.jpg", "wb") as f:
            f.write(response.content)

    def test_c2pa(self):
        # make sure c2pa is working as we expect
        reader = c2pa.Reader.from_file("test.jpg")
        manifest = reader.get_active_manifest()
        self.assertIsNotNone(manifest)

    def test_is_ready(self):
        # should always be ready
        self.assertTrue(self.rule.is_ready())

    def test_c2pa_image_url(self):
        # pass in url directly
        url = "https://c2pa.org/public-testfiles/image/jpeg/adobe-20220124-C.jpg"
        self.assertTrue(self.rule.is_allowed(url=url))

        # make sure 404 throws error
        with self.assertRaises(ValueError):
            url = "https://c2pa.org/public-testfiles/image/jpeg/none.jpg"
            self.rule.is_allowed(url=url)

    def test_c2pa_image_file(self):
        # pass in local file path
        self.assertTrue(self.rule.is_allowed(path="test.jpg"))

        # make sure file which doesn't exist fails
        with self.assertRaises(FileNotFoundError):
            self.rule.is_allowed(path="test2.jpg")

        # manifest which blocks AI usage
        self.assertFalse(self.rule.is_allowed(path="tests/resources/sample_c2pa.png"))

    def test_c2pa_image_body(self):
        # download and pass in body
        url = "https://c2pa.org/public-testfiles/image/jpeg/adobe-20220124-C.jpg"
        response = requests.get(url)
        body = response.content
        self.assertTrue(self.rule.is_allowed(body=body))

        # error with invalid image data
        with self.assertRaises(ValueError):
            self.rule.is_allowed(body=b"invalid image data")

        # no manifest
        url = "https://c2pa.org/public-testfiles/image/jpeg/adobe-20220124-A.jpg"
        response = requests.get(url)
        body = response.content
        self.assertTrue(self.rule.is_allowed(body=body))

    def tearDown(self):
        # delete test file
        os.remove("test.jpg")


