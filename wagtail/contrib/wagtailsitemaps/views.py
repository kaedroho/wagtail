import warnings

from wagtail.utils.deprecation import RemovedInWagtail16Warning


warnings.warn(
    "The 'wagtail.contrib.wagtailsitemaps.views' module has been moved to 'wagtail.contrib.sitemaps.views'.",
    RemovedInWagtail16Warning)


from wagtail.contrib.sitemaps.views import *  # noqa
