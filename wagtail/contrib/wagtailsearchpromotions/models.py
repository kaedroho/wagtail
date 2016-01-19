import warnings

from wagtail.utils.deprecation import RemovedInWagtail16Warning


warnings.warn(
    "The 'wagtail.contrib.wagtailsearchpromotions.models' module has been moved to 'wagtail.contrib.searchpromotions.models.",
    RemovedInWagtail16Warning)


from wagtail.contrib.searchpromotions.models import *  # noqa
