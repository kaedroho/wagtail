import warnings

from wagtail.utils.deprecation import RemovedInWagtail16Warning


warnings.warn(
    "The 'wagtail.contrib.wagtailroutablepage.models' module has been moved to 'wagtail.contrib.routablepage.models.",
    RemovedInWagtail16Warning)


from wagtail.contrib.routablepage.models import *  # noqa
