import warnings

from wagtail.utils.deprecation import RemovedInWagtail16Warning


warnings.warn(
    "The 'wagtail.contrib.wagtailapi.urls' module has been moved to 'wagtail.contrib.api.urls'.",
    RemovedInWagtail16Warning)


from wagtail.contrib.api.urls import *  # noqa
