from django.template.loader import render_to_string

from wagtail.admin.compare import ForeignObjectComparison
from wagtail.admin.edit_handlers import BaseChooserPanel


class VideoChooserPanel(BaseChooserPanel):
    pass


class VideoFieldComparison(ForeignObjectComparison):
    def htmldiff(self):
        video_a, video_b = self.get_objects()

        return render_to_string(
            "wagtailvideos/widgets/compare.html",
            {
                "video_a": video_a,
                "video_b": video_b,
            },
        )
