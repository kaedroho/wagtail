import warnings

from wagtail.utils.deprecation import RemovedInWagtail16Warning


warnings.warn(
    "The 'wagtail.contrib.wagtailsearchpromotions' app has been renamed to 'wagtail.contrib.searchpromotions'. "
    "Please update INSTALLED_APPS.", RemovedInWagtail16Warning)


from wagtail.contrib.searchpromotions.apps import WagtailSearchPromotionsAppConfig  # noqa
