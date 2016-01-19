import warnings

from wagtail.utils.deprecation import RemovedInWagtail16Warning


warnings.warn(
    "The 'wagtail.contrib.wagtailsitemaps' app has been renamed to 'wagtail.contrib.sitemaps'. "
    "Please update INSTALLED_APPS.", RemovedInWagtail16Warning)


from wagtail.contrib.sitemaps.apps import WagtailSitemapsAppConfig  # noqa
