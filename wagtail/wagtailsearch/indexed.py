import warnings

warnings.warn(
    "The wagtail.wagtailsearch.indexed module has been renamed. "
    "Use wagtail.wagtailsearch.index instead.", DeprecationWarning)

from .index import *
