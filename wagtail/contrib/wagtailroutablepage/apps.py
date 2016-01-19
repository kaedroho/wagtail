import warnings

from wagtail.utils.deprecation import RemovedInWagtail16Warning


warnings.warn(
    "The 'wagtail.contrib.wagtailroutablepage' app has been renamed to 'wagtail.contrib.routablepage'. "
    "Please update INSTALLED_APPS.", RemovedInWagtail16Warning)


from wagtail.contrib.routablepage.apps import WagtailRoutablePageAppConfig  # noqa
