from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WagtailSnippetsTestsAppConfig(AppConfig):
    name = 'wagtail.test.snippets'
    label = 'snippetstests'
    verbose_name = _("Wagtail snippets tests")
