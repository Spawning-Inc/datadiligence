.. _advanced:

==============
Advanced Usage
==============
For most users, the default settings will be sufficient. However, if you want to create your own `Rules` and `Evaluators`, it's pretty easy.

-------------------
Make your own Rules
-------------------
`Rules` are where the logic to filter out results is performed. A `Rule` should always descend from the `datadiligence.rules.Rule` class::

    from datadiligence.rules import Rule

    class MyRule(Rule)
        def is_ready(self):
            return True

        def is_allowed(self, **kwargs):
            return True

A `Rule` has two functions you need to implement, `is_ready` and `is_allowed`.

The `is_ready` function is used to determine if the rule's dependencies are all present. For example, if the rule requires an API Key in an environment variable::

    def is_ready(self):
        return os.environ.get('MY_ENV_VAR') is not None

The `is_allowed` functions is where the logic is performed to evaluate if the arguments are allowed. For example, if we want to disallow any resource loading over HTTP (instead of HTTPS)::

    def is_allowed(self, url=None, **kwargs):
        if url is None:
            raise Exception("Url is required")

        return url.startswith('https://')

Note this rule will raise an exception if the `url` argument is not provided.This is because we don't want this rule to silently fail if `url` is not provided.
This function could also be receiving other arguments intended for other `Rules`, so we keep the `**kwargs` in the function signature.

It's best to try and keep the arguments sent to the `is_allowed` function as the minimum required to perform the filtering/validation logic. Any additional arguments may be best provided to the Rule constructor::

    def __init__(self, block_http=True, **kwargs):
        self.block_http = block_http

    def is_allowed(self, url=None, **kwargs):
        if url is None:
            raise Exception("Url is required")

        return self.block_http and url.startswith('https://')

Though this is up to the developer to decide, be wary that these arguments could be unintentionally passed to other Rules and evaluated accidentally.

Now that we have our `Rule`, we can add it to the default `Evaluator`, or to one of the existing `Evaluators`::

    from datadiligence.evaluators import Evaluator
    from my_code import MyRule

    my_evaluator = Evaluator()
    my_evaluator.add_rule(MyRule())

And now the `Evaluator` will run your rule like any other!::

    >>> my_evaluator.is_allowed(url='http://example.com')
    False
    >>> my_evaluator.is_allowed(url='https://example.com')
    True

-----------------------
Make your own Evaluator
-----------------------
Sometimes you want to bundle together several `Rules`, and provide default arguments, flags to customize the `Rules`, etc.
In this case, it's best to make your own `Evaluator`::

    from datadiligence.evaluators import Evaluator
    from my_code import MyRule

    class MyEvaluator(Evaluator):
        def __init__(self, check_http=True, block_http=True):
            super().__init__()
            if not self.check_http:
                self.add_rule(MyRule(block_http))

This `Evaluator` will run the `MyRule` if the `check_http` flag is set to `True`.

    >>> my_evaluator = MyEvaluator()
    >>> my_evaluator.is_allowed(url='http://example.com')
    False

All `Rules` in an `Evaluator` should have at least one common keyword argument provided which they can use to evaluate, or else the `Rule` should throw
an exception. In other words, an `Evaluator` should NOT mix-and-match required arguments for any contained `Rules`. Otherwise, unnecessary `Rules` could
populate `Evaluators` and provide a mistaken sense of compliance, when in fact they're not being evaluated at all::

    class MyRule(Rule)
        def is_ready(self):
            return True

        def is_allowed(self, argument=None, **kwargs):
            # please do this
            if argument is None:
                raise Exception("Argument is required")

This also lets `Evaluators` be composed into logical units which can be used in different contexts, instead of one massive
`Evaluator` with all the rules in it which then must be customized further. Instead, we can try to create default `Evaluators`
with sane defaults for given contexts.

For example, `PostprocessEvaluator` and `PreprocessEvaluator` were both created with the **img2dataset** workflow in mind. However,
other workflows may not already have HTTP responses, thus other evaluators may consume a URL and download the response directly.

-----------------------
Make your own Bulk Rule
-----------------------
Bulk `Rules` are handled slightly differently than normal `Rules`. They are intended to be a subclass of `datadiligence.rules.BulkRule` and implement the `filter_allowed` function::

    from datadiligence.rules import BulkRule

    class MyBulkRule(BulkRule):
        def is_ready(self):
            return True

        def filter_allowed(self, **kwargs):
            return []

Notice the ``filter_allowed`` function should be called for ``BulkRule`` classes. The `Evaluator` should also have the ``filter_allowed`` function implemented::

        class MyEvaluator(Evaluator):
            def filter_allowed(self, urls= [] **kwargs):
                # set default to allow everything
                allowed = [True] * len(urls)
                for rule in self.rules:
                    if rule.is_ready():
                        rule_results = rule.is_allowed(urls=urls)

                        # set each url as disallowed, and never re-enable it
                        allowed = [a and b for a, b in zip(allowed, rule_results)]

Notice the response type is also not a boolean, but a list. The responses should be a list of approved URLs. As a best practice,
the rules that will catch the most URLs should be run first, and the rules that will catch the least URLs should be run last.

--------------------------
Only Run the Spawning API
--------------------------
If you only want to check your URLs against the Spawning API, perform the following setup::

    $ export SPAWNING_API_KEY=<your_key>
    $ python
    >>> from datadiligence.rules import SpawningAPI
    >>> urls = ['http://example.com', 'https://example.com']
    >>> spawning_rule = SpawningAPI(user_agent="my-user-agent")
    >>> spawning_rule.filter_allowed(urls=urls)
    []
