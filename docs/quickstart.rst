.. _quickstart:

================
Quickstart
================
No fluff or frills, let's get started.

------------
Installation
------------
Easiest way to install is to use pip::

    pip install datadiligence

You could also install from Github if you really want to::

    pip install git+https://github.com/Spawning-Inc/datadiligence.git


------------
How it Works
------------
This package works by providing a set of `Rules`, which are organized into a set of `Evaluators`.
A `Rule` is logic for checking an incoming argument (e.g. a URL, HTTP headers, image metadata, etc) to see if the content is allowed.
An `Evaluator` is composed of a set of Rules, and is responsible for coordinating the evaluation of the parameters against the Rules.

You can imagine an `Evaluator` as a collection of Rules. Arguments are passed through the pipeline, and Rules listen for keyword arguments to check how to evaluate the inputs.

For example, you can have an `Evaluator` with one `Rule` that checks HTTP headers, and another `Rule` that checks for metadata in an image.
The Evaluator can pass the HTTP `Response` object down to the rules, and the `Rules` can check the headers and body as needed.

*****************
Keyword Arguments
*****************
Due to the above, all arguments should be passed by name to make sure the `Rules` evaluate them properly::

    >>> import datadiligence as dd
    >>> url = 'https://www.google.com'

    # do this
    >>> dd.is_allowed(url=url)
    False

    # don't do this
    >>> dd.is_allowed(url)
    True

------------------
Check URLs in Bulk
------------------
Most ML pipelines will run through a large list of URLs. We can use the Spawning API to
check these URLs in bulk.

The first thing we need to do is load the package::

    import datadiligence as dd

This will also instantiate some default Evaluators for you to use. We can pass a list of urls to
the package directly to use one of these defaults::

    >>> urls = ['https://www.google.com', 'https://www.yahoo.com', 'https://www.bing.com']
    >>> approved_urls = dd.filter_allowed(urls=urls)
    >>> approved_urls
    ['https://www.google.com']

The response is a list of the URLs that are allowed. Additionally,
you can use ``is_allowed`` to return a list of boolean responses::

    >>> urls = ['https://www.google.com', 'https://www.yahoo.com', 'https://www.bing.com']
    >>> approved_urls = dd.is_allowed(urls=urls)
    >>> approved_urls
    [True, False, False]

In both cases, only Google is allowed.

If you're using `pyarrow` or `pandas`, you must first convert the urls to a python list::

    >>> # pyarrow example
    >>> import pyarrow as pa
    >>> urls = pa.array(['https://www.google.com', 'https://www.yahoo.com', 'https://www.bing.com'])
    >>> approved_urls = dd.is_allowed(urls=urls.to_pylist())
    >>> approved_urls
    [True]

    >>> # pandas example
    >>> import pandas as pd
    >>> urls = pd.Series(['https://www.google.com', 'https://www.yahoo.com', 'https://www.bing.com'])
    >>> approved_urls = dd.is_allowed(urls=urls.to_list())
    >>> approved_urls
    [True]

Some rules require additional information or dependencies, such as API Keys in the case of Spawning (see below).
If the required dependencies are not met, the related rule will NOT evaluate, and the response will be the same as if the rule was not included.

For example, if the Spawning API Key is not set in your environment variables::

    >>> urls = ['https://www.google.com', 'https://www.yahoo.com', 'https://www.bing.com']
    >>> approved_urls = dd.filter_allowed(urls=urls)
    Spawning API key not found. Please set your API key to the environment variable SPAWNING_API_KEY
    >>> approved_urls
    ['https://www.google.com', 'https://www.yahoo.com', 'https://www.bing.com']

****************
Spawning API Key
****************
The only "bulk" rule currently available is the Spawning API.
In order to use the Spawning API, you must have a valid API key.
See our `API page <https://docs.spawning.io>`_ for more information.

Once you have a valid API key, you must set it in your env before importing ``datadiligence``::

    $ export SPAWNING_API_KEY=<your_api_key_here>
    $ python
    >>> import datadiligence as dd


------------------
Check a single URL
------------------
Sometimes, checking the image at a single URL may be all you need::

    >>> url = 'https://www.google.com'
    >>> dd.is_allowed(url=url)
    True

This evaluator currently uses the Spawning API Rule, and the X-Robots-Tag Rule. If you're checking many URLs, it's
probably best to use the Bulk rules instead.

------------------------------
Check a File/Response at a URL
------------------------------
If you're downloading many files from URLs, it doesn't make sense to download a URL a second time to evaluate the response. In this case, you can use the HTTP response::

    >>> import requests
    >>> url = 'https://www.google.com'
    >>> response = requests.get(url)
    >>> dd.is_allowed(response=response)
    True

Or you can use the HTTP headers::

    >>> import requests
    >>> url = 'https://www.google.com'
    >>> response = requests.get(url)
    >>> dd.is_allowed(headers=response.headers)
    True

The ``response`` and ``headers`` parameters accept a number of basic types, including response objects from `requests` and `urllib`,
so you should feel comfortable passing in the response object from your favorite HTTP library.

------------------
Check a Local File
------------------
If you have a file available locally, you can pass the file path to the package::

    >>> file_path = "path/to/image.png"
    >>> dd.is_allowed(path=file_path)
    True

-----------------------------
Check against your User-Agent
-----------------------------
Many of the known opt-out methods are allowed to define specific rules for User-Agents. A User-Agent defines
"who", "how", or "in what method" someone is making the request. For example, your Web Browser will send a long string
which includes the browser version, the OS version, etc. Content owners can choose to respect some User-Agents, and not others.

In order to check a URL with a specific User-Agent, you can pass the ``user_agent`` parameter::

    >>> url = 'https://www.google.com'
    >>> dd.is_allowed(url=url, user_agent="my-training-org")
    False

If not provided, the any User-Agent specific directives are ignored. Please note, this may result false-positives. When
you have a User-agent, please provide it. If you don't know, it should be fine to ignore it.

----------------------------
Calling a specific Evaluator
----------------------------
So far, we've been letting the package determine the best `Evaluator` to use based on the keyword arguments. If
you want to call a specific Evaluator, you can initialize it and call it directly::

    >>> fromm datadiligence import HttpEvaluator
    >>> http_evaluator = HttpEvaluator()
    >>> url = 'https://www.google.com'
    >>> http_evaluator.is_allowed(url=url)
    True

----------------------
Customizing Evaluators
----------------------
Some Evaluators allow you to disable specific `Rules`. All `Rules` should be enabled by default,
but if you don't want to respect a rule for a given reason (e.g. you don't have a Spawning API Key), you can disable
the rule by creating the Evaluator directly::

    >>> from datadiligence import HttpEvaluator
    >>> http_evaluator = HttpEvaluator(respect_tdmrep=False)

This evaluator can be called the same as the default Evaluators::

    >>> url = 'https://www.google.com'
    >>> http_evaluator.is_allowed(url=url)
    True

This should normally be done when you're purposefully avoiding a default `Rule`, not due to lack of dependencies. Any
`Rule` which does not have required dependencies (API Keys, CLI tools, etc) will be first check their dependencies, and
will not be evaluated if they are not present.

-----------------
Customizing Rules
-----------------
Evaluators are composed of Rules, and each Rule can have its own options.
We try to set these to sane defaults, but they can also be customized, albeit in a more manual method::

    >>> from datadiligence import PreprocessEvaluator
    >>> from datadiligence.rules import SpawningAPI
    >>> preprocess_evaluator = PreprocessEvaluator()
    >>> preprocess_evaluator.rules = []  # clear the default rules
    >>> preprocess_evaluator.add_rule(SpawningAPI(chunk_size=1000))

This will create a new PreprocessEvaluator with a single SpawningAPI rule, with a chunk size of 1,000 (default is 10,000).
It can be used like normal::

    >>> urls = ['https://www.google.com', 'https://www.yahoo.com', 'https://www.bing.com']
    >>> approved_urls = preprocess_evaluator.is_allowed(urls=urls)
    >>> approved_urls
    ['https://www.google.com']


---------------------
Errors and Exceptions
---------------------

Most errors and exceptions are related to incorrect properties or arguments being passed to the Evaluator.
We try not to hide any Exceptions raised by underlying dependencies (e.g. `requests`) so you can decide
on how to handle those for yourself.

***********

That should cover the most common usages of this package. We've also done our best to build this
package to be extendable. If you have a specific opt-out method you want to add, you can
create your own Rules and Evaluators. See our `Advanced Usage Guide <https://datadiligence.readthedocs.io/en/latest/advanced.html>`_ for more information.
