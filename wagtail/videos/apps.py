from django.apps import AppConfig
from django.db.models import ForeignKey
from django.utils.translation import gettext_lazy as _

from . import checks, get_video_model  # NOQA
from .signal_handlers import register_signal_handlers


class WagtailVideosAppConfig(AppConfig):
    name = "wagtail.videos"
    label = "wagtailvideos"
    verbose_name = _("Wagtail videos")
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        register_signal_handlers()

        # Set up model forms to use AdminVideoChooser for any ForeignKey to the video model
        from wagtail.admin.forms.models import register_form_field_override

        from .widgets import AdminVideoChooser

        Video = get_video_model()
        register_form_field_override(
            ForeignKey, to=Video, override={"widget": AdminVideoChooser}
        )

        # Set up video ForeignKeys to use VideoFieldComparison as the comparison class
        # when comparing page revisions
        from wagtail.admin.compare import register_comparison_class

        from .edit_handlers import VideoFieldComparison

        register_comparison_class(
            ForeignKey, to=Video, comparison_class=VideoFieldComparison
        )
