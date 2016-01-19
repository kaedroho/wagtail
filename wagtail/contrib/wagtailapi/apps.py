import warnings

from wagtail.utils.deprecation import RemovedInWagtail16Warning


warnings.warn(
    "The 'wagtail.contrib.wagtailapi' app has been renamed to 'wagtail.contrib.api'. "
    "Please update INSTALLED_APPS.", RemovedInWagtail16Warning)


from wagtail.contrib.api.apps import WagtailAPIAppConfig  # noqa
