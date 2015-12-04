import warnings

from django.apps import AppConfig, apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from wagtail.utils.deprecation import RemovedInWagtail14Warning


class WagtailAPIAppConfig(AppConfig):
    name = 'wagtail.api'
    label = 'wagtailapi'
    verbose_name = "Wagtail API"

    def ready(self):
        # Install cache purging signal handlers
        if getattr(settings, 'WAGTAILAPI_USE_FRONTENDCACHE', False):
            if apps.is_installed('wagtail.contrib.wagtailfrontendcache'):
                from wagtail.api.v1.signal_handlers import register_signal_handlers as register_signal_handlers_v1
                register_signal_handlers_v1()
            else:
                raise ImproperlyConfigured(
                    "The setting 'WAGTAILAPI_USE_FRONTENDCACHE' is True but "
                    "'wagtail.contrib.wagtailfrontendcache' is not in INSTALLED_APPS."
                )

        if not apps.is_installed('rest_framework'):
            warnings.warn(
                "The 'wagtailapi' module now requires 'rest_framework' to be installed. "
                "Please add 'rest_framework' to INSTALLED_APPS.",
                RemovedInWagtail14Warning)
