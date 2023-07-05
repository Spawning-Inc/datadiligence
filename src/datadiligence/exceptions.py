"""
Exceptions for the package.
"""


class XRobotsTagNoParam(Exception):
    """
    Raised when XRobotsTagHeader isn't provided with either an url, response, or headers object.
    """

    def __init__(self):
        super().__init__("XRobotsTagHeader must be provided with either an url, response, or headers object.")


class TDMRepNoParam(Exception):
    """
    Raised when TDMRepHeader isn't provided with either an url, response, or headers object.
    """

    def __init__(self):
        super().__init__("TDMRepHeader must be provided with either an url, response, or headers object.")


class HttpUnknownHeaderObject(Exception):
    """
    Raised when an HTTPRule is provided with an unknown header object.
    """

    def __init__(self):
        super().__init__(
            "HTTPRule must be provided with a header object of types "
            "dict|CaseInsensitiveDict|http.client.HTTPMessage.")


class HttpUnknownResponseObject(Exception):
    """
    Raised when HTTPRule is provided with an unknown response object.
    """

    def __init__(self):
        super().__init__(
            "HTTPRule must be provided with a response object of types "
            "http.client.HTTPResponse|requests.Response.")


class SpawningAIAPIError(Exception):
    """
    Raised when the Spawning AI API returns an error.
    """

    def __init__(self, message):
        super().__init__(message)


class EvaluatorNotRegistered(Exception):
    """
    Raised when an evaluator is not registered.
    """

    def __init__(self, name):
        super().__init__(f"Evaluator {name} not registered.")


class DefaultEvaluatorNotFound(Exception):
    """
    Raised when aa default evaluator can't be determined.
    """

    def __init__(self, args):
        super().__init__(f"No default evaluator found which can handle the following arguments {args}.")


class NotEvaluator(Exception):
    """
    Raised when an object is not an evaluator.
    """

    def __init__(self):
        super().__init__("Object must be of type Evaluator.")


class EvaluatorAlreadyRegistered(Exception):
    """
    Raised when an evaluator is already registered.
    """

    def __init__(self, name):
        super().__init__(f"Evaluator {name} already registered.")


class SpawningNoParam(Exception):
    """
    Raised when SpawningAPI isn't provided with a list of urls.
    """

    def __init__(self):
        super().__init__("SpawningAPI must be provided with a list of urls.")
