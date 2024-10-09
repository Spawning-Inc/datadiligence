
.. image:: https://readthedocs.org/projects/datadiligence/badge/?version=latest
  :alt: ReadTheDocs
  :target: https://datadiligence.readthedocs.io/en/stable/
.. image:: https://img.shields.io/pypi/v/datadiligence.svg
  :alt: PyPI-Server
  :target: https://pypi.org/project/datadiligence
.. image:: https://img.shields.io/pypi/l/datadiligence
  :target: https://opensource.org/licenses/MIT
  :alt: PyPI - License
.. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
   :alt: Twitter
   :target: https://twitter.com/spawning_

=============
datadiligence
=============

    Respect generative AI opt-outs in your ML training pipeline.

``datadiligence`` aims to make it simple for ML practitioners to respect opt-outs in their training by
providing a consistent interface to check if a given work is opted-out using any known method. The goal of this
project is to make respecting opt-outs as painless as possible, while being flexible enough to support new opt-out
methods as they are developed.

-------------------
Why is this needed?
-------------------

ML training datasets are often harvested without consent from the data or content owners, meaning any ML models
trained with these datasets could be violating the wishes of content creators on how their content is used. With the
absence of an opt-out standard, many platforms and individuals have come up with their own methods of stating
their consent.

Additionally, consent can change over time, and static datasets obviously cannot. A work which was
consenting at the time of the dataset's creation may not be consenting at the time of training. Keeping up
with the current state of opt-outs is unrealistic for most practitioners, and so this project aims to make it
as easy as possible to respect opt-outs in your training pipeline.

-----------
Basic Usage
-----------

To install::

   pip install datadiligence

Add bulk pre-processing for URLs in your pipeline (requires Spawning API Key)::

   >>> import datadiligence as dd
   >>> urls = ["https://www.example.com/art-123456789.jpg", "https://www.example.com/art-987654321.jpg"]
   >>> dd.filter_allowed(urls=urls)
    ["https://www.example.com/art-123456789.jpg"]
   >>> dd.is_allowed(urls=urls)
    [True, False]


Check HTTP responses in post-processing::

   >>> response = requests.get("https://www.example.com/art-123456789.jpg")
   >>> is_allowed = dd.is_allowed(response=response)
   True
   >>> if is_allowed:
   >>>     process_image(response.content)

Full documentation is available on `readthedocs <https://datadiligence.readthedocs.io/en/latest/quickstart.html>`_.

Check a local file::

   >>> dd.is_allowed(path="path/to/file.jpg")
   False

-------------------------
Respected Opt-Out Methods
-------------------------

This project currently supports the following opt-out methods:

* The Spawning API. See https://spawning.ai/api for more information.
* The DeviantArt X-Robots-Tag HTTP Headers. See https://www.deviantart.com/team/journal/UPDATE-All-Deviations-Are-Opted-Out-of-AI-Datasets-934500371 for more information.
* C2PA/CAI metadata. See https://c2pa.org/ for more information.

------------
Contributing
------------
See contribution guidelines `here <https://datadiligence.readthedocs.io/en/latest/contributing.html>`_.
