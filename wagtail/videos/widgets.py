import json

from django import forms
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from wagtail.admin.staticfiles import versioned_static
from wagtail.admin.widgets import AdminChooser
from wagtail.core.telepath import register
from wagtail.core.widget_adapters import WidgetAdapter
from wagtail.videos import get_video_model
from wagtail.videos.shortcuts import get_rendition_or_not_found


class AdminVideoChooser(AdminChooser):
    choose_one_text = _("Choose an video")
    choose_another_text = _("Change video")
    link_to_chosen_text = _("Edit this video")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_model = get_video_model()

    def get_value_data(self, value):
        if value is None:
            return None
        elif isinstance(value, self.video_model):
            video = value
        else:  # assume video ID
            video = self.video_model.objects.get(pk=value)

        preview_video = get_rendition_or_not_found(video, "max-165x165")

        return {
            "id": video.pk,
            "title": video.title,
            "preview": {
                "url": preview_video.url,
                "width": preview_video.width,
                "height": preview_video.height,
            },
            "edit_url": reverse("wagtailvideos:edit", args=[video.id]),
        }

    def render_html(self, name, value_data, attrs):
        value_data = value_data or {}
        original_field_html = super().render_html(name, value_data.get("id"), attrs)

        return render_to_string(
            "wagtailvideos/widgets/video_chooser.html",
            {
                "widget": self,
                "original_field_html": original_field_html,
                "attrs": attrs,
                "value": bool(
                    value_data
                ),  # only used by chooser.html to identify blank values
                "title": value_data.get("title", ""),
                "preview": value_data.get("preview", {}),
                "edit_url": value_data.get("edit_url", ""),
            },
        )

    def render_js_init(self, id_, name, value_data):
        return "createVideoChooser({0});".format(json.dumps(id_))

    @property
    def media(self):
        return forms.Media(
            js=[
                versioned_static("wagtailvideos/js/video-chooser-modal.js"),
                versioned_static("wagtailvideos/js/video-chooser.js"),
            ]
        )


class VideoChooserAdapter(WidgetAdapter):
    js_constructor = "wagtail.videos.widgets.VideoChooser"

    def js_args(self, widget):
        return [
            widget.render_html("__NAME__", None, attrs={"id": "__ID__"}),
            widget.id_for_label("__ID__"),
        ]

    @cached_property
    def media(self):
        return forms.Media(
            js=[
                versioned_static("wagtailvideos/js/video-chooser-telepath.js"),
            ]
        )


register(VideoChooserAdapter(), AdminVideoChooser)
