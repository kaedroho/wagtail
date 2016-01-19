import warnings

from wagtail.utils.deprecation import RemovedInWagtail16Warning


warnings.warn(
    "The 'wagtail.contrib.wagtailstyleguide' app has been renamed to 'wagtail.contrib.styleguide'. "
    "Please update INSTALLED_APPS.", RemovedInWagtail16Warning)


from wagtail.contrib.styleguide.apps import WagtailStyleGuideAppConfig  # noqa
