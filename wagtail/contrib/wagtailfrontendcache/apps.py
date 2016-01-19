import warnings

from wagtail.utils.deprecation import RemovedInWagtail16Warning


warnings.warn(
    "The 'wagtail.contrib.wagtailfrontendcache' app has been renamed to 'wagtail.contrib.frontendcache'. "
    "Please update INSTALLED_APPS.", RemovedInWagtail16Warning)


from wagtail.contrib.frontendcache.apps import WagtailFrontendCacheAppConfig  # noqa
