"""
functions to preload default evaluators and make accessible globally
"""

from .exceptions import EvaluatorAlreadyRegistered, EvaluatorNotRegistered, NotEvaluator, DefaultEvaluatorNotFound
from .evaluators import Evaluator, PreprocessEvaluator, PostprocessEvaluator, FileEvaluator

bootstrap_dictionary = {}


def load_defaults(user_agent=None):
    """Load the default evaluators."""
    register_evaluator(PreprocessEvaluator(user_agent=user_agent), overwrite=True)
    register_evaluator(PostprocessEvaluator(user_agent=user_agent), overwrite=True)
    register_evaluator(FileEvaluator(), overwrite=True)


def list_evaluators():
    """List the evaluators."""
    return list(bootstrap_dictionary.keys())


def register_evaluator(evaluator, name=None, overwrite=False):
    """Register an evaluator.

    Args:
        evaluator (Evaluator): The evaluator object.
        name (str): Key name of the evaluator.
        overwrite (bool): Whether or not to overwrite the evaluator if it already exists.
    """
    if not name:
        name = evaluator.name

    if not isinstance(evaluator, Evaluator):
        raise NotEvaluator()

    if name in bootstrap_dictionary and not overwrite:
        raise EvaluatorAlreadyRegistered(name)

    bootstrap_dictionary[name] = evaluator


def deregister_evaluator(name):
    """Deregister an evaluator.

    Args:
        name (str): The name of the evaluator.
    """
    if name not in bootstrap_dictionary:
        raise EvaluatorNotRegistered(name)
    del bootstrap_dictionary[name]


def get_evaluator(name):
    """Get an evaluator.

    Args:
        name (str): The name of the evaluator.
    """
    if name not in bootstrap_dictionary:
        raise EvaluatorNotRegistered(name)
    return bootstrap_dictionary[name]


def is_allowed(name=None, **kwargs):
    """
    Check if the content is allowed.

    Args:
        name (str): The name of a specific evaluator.
        **kwargs: Arbitrary keyword arguments to read args from.
    """
    if name is not None:
        if name not in bootstrap_dictionary:
            raise EvaluatorNotRegistered(name)
        return bootstrap_dictionary[name].is_allowed(**kwargs)
    else:
        # since we are preloading evaluators manually, we can check to see which one to call
        # based on the kwargs
        if "urls" in kwargs:
            return bootstrap_dictionary["preprocess"].is_allowed(**kwargs)
        elif "url" in kwargs or "response" in kwargs or "headers" in kwargs:
            return bootstrap_dictionary["postprocess"].is_allowed(**kwargs)
        elif "path" in kwargs:
            return bootstrap_dictionary["file"].is_allowed(**kwargs)
        else:
            raise DefaultEvaluatorNotFound(list(kwargs.keys()))


def filter_allowed(name=None, **kwargs):
    """
    Filter a list of content.

    Args:
        name (str): The name of a specific evaluator.
        **kwargs: Arbitrary keyword arguments to read args from.
    """
    if name is not None:
        if name not in bootstrap_dictionary:
            raise EvaluatorNotRegistered(name)
        return bootstrap_dictionary[name].filter_allowed(**kwargs)
    else:
        # since we are preloading evaluators manually, we can check to see which one to call
        # based on the kwargs
        if "urls" in kwargs:
            return bootstrap_dictionary["preprocess"].filter_allowed(**kwargs)
        else:
            raise DefaultEvaluatorNotFound(list(kwargs.keys()))


load_defaults()
