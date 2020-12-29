from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WagtailCoreAppConfig(AppConfig):
    name = 'wagtail'
    label = 'wagtailcore'
    verbose_name = _("Wagtail core")

    def ready(self):
        # The edit_handlers module extends Page with some additional attributes required by
        # wagtail admin (namely, base_form_class and get_edit_handler). Importing this within
        # wagtail.admin.models ensures that this happens in advance of running wagtail.admin's
        # system checks.
        from wagtail import edit_handlers  # NOQA

        from wagtail.signal_handlers import register_signal_handlers
        register_signal_handlers()
