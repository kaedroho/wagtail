import warnings

from wagtail.utils.deprecation import RemovedInWagtail16Warning


warnings.warn(
    "The 'wagtail.contrib.wagtailmedusa' app has been renamed to 'wagtail.contrib.medusa'. "
    "Please update INSTALLED_APPS.", RemovedInWagtail16Warning)


from wagtail.contrib.medusa.apps import WagtailMedusaAppConfig  # noqa
