import warnings

from wagtail.utils.deprecation import RemovedInWagtail16Warning


warnings.warn(
    "The 'wagtail.contrib.wagtailsitemaps.sitemap_generator' module has been moved to 'wagtail.contrib.sitemaps.sitemap_generator'.",
    RemovedInWagtail16Warning)


from wagtail.contrib.sitemaps.sitemap_generator import *  # noqa
