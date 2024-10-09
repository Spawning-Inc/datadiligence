"""
This module contains the C2PA Metadata Rule class.
"""

import c2pa
from io import BytesIO
from PIL import Image
from .base import HttpRule
import os
import logging


class C2PAMetadataRule(HttpRule):
    """
    This class wraps calls to the Adobe Content Authenticity Initiative c2pa tool. TODO.
    """
    assertion_label = "c2pa.training-mining"
    manifest_flags = [
        "c2pa.ai_generative_training",
        "c2pa.ai_inference",
        "c2pa.ai_training",
        "c2pa.data_mining",
    ]

    def is_allowed(self, path=None, url=None, body=None, **kwargs):
        """Check if the C2PA AI reservations exists.

        Args:
            path (str): The path to the image file.
            url (str): The URL to the image file.
            body (bytes): The bytes for the image file.

        Returns:
            bool: True if access is allowed for the resource, False otherwise.
        """
        if body is None:
            if path is not None:
                # retrieve the body from the file path
                if not os.path.exists(path):
                    raise FileNotFoundError(f"File not found: {path}")
                img_data = open(path, "rb")
                file_format = path.split(".")[-1]  # use file extension for format
            elif url is not None:
                # retrieve the body from the URL
                response = self._handle_url(url)
                if response.status_code != 200:
                    raise ValueError(f"Invalid response: {response.status_code}")
                img_data = BytesIO(response.content)
                file_format = response.headers.get("Content-Type", "")  # use content type for format
            else:
                # default response
                return True
        else:
            # if body provided, get the data and file format
            try:
                img_data = BytesIO(body)
                with Image.open(img_data) as img:
                    file_format = img.format
            except Exception as e:
                raise ValueError(f"Invalid image data: {e}")

        # attempt to open the manifest
        try:
            reader = c2pa.Reader(file_format, img_data)
            manifest = reader.get_active_manifest()

            # find ai assertions
            for assertion in manifest.get("assertions", []):
                if assertion.get("label", "") == self.assertion_label:
                    # iterate through assertion entries
                    entries = assertion.get("data", {}).get("entries", {})
                    if len(entries) > 0:
                        for key in self.manifest_flags:
                            if key in entries and entries[key].get("use", "allowed") == "notAllowed":
                                return False
        except Exception as e:
            logging.error(e)
            return True

        return True

    def is_ready(self):
        """Check if the rule is ready to be used."""
        return True
