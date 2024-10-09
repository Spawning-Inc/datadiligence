"""
    Respect generative AI opt-outs in your ML and training pipeline.
"""


import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "datadiligence"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from .evaluators import HttpEvaluator, PostprocessEvaluator, PreprocessEvaluator, FileEvaluator, Evaluator

# bootstrap methods
from .bootstrap import load_defaults, register_evaluator, is_allowed, filter_allowed, get_evaluator, deregister_evaluator, list_evaluators
