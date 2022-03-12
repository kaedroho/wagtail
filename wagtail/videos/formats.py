from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from wagtail.utils.apps import get_app_submodules

from .shortcuts import get_rendition_or_not_found


class Format:
    def __init__(self, name, label, classnames, filter_spec):
        self.name = name
        self.label = label
        self.classnames = classnames
        self.filter_spec = filter_spec

    def __str__(self):
        return (
            f'"{self.name}", "{self.label}", "{self.classnames}", "{self.filter_spec}"'
        )

    def __repr__(self):
        return f"Format({self})"

    def editor_attributes(self, video, alt_text):
        """
        Return additional attributes to go on the HTML element
        when outputting this video within a rich text editor field
        """
        return {
            "data-embedtype": "video",
            "data-id": video.id,
            "data-format": self.name,
            "data-alt": escape(alt_text),
        }

    def video_to_editor_html(self, video, alt_text):
        return self.video_to_html(
            video, alt_text, self.editor_attributes(video, alt_text)
        )

    def video_to_html(self, video, alt_text, extra_attributes=None):
        if extra_attributes is None:
            extra_attributes = {}
        rendition = get_rendition_or_not_found(video, self.filter_spec)

        extra_attributes["alt"] = escape(alt_text)
        if self.classnames:
            extra_attributes["class"] = "%s" % escape(self.classnames)

        return rendition.img_tag(extra_attributes)


FORMATS = []
FORMATS_BY_NAME = {}


def register_video_format(format):
    if format.name in FORMATS_BY_NAME:
        raise KeyError("Video format '%s' is already registered" % format.name)
    FORMATS_BY_NAME[format.name] = format
    FORMATS.append(format)


def unregister_video_format(format_name):
    global FORMATS
    # handle being passed a format object rather than a format name string
    try:
        format_name = format_name.name
    except AttributeError:
        pass

    try:
        del FORMATS_BY_NAME[format_name]
        FORMATS = [fmt for fmt in FORMATS if fmt.name != format_name]
    except KeyError:
        raise KeyError("Video format '%s' is not registered" % format_name)


def get_video_formats():
    search_for_video_formats()
    return FORMATS


def get_video_format(name):
    search_for_video_formats()
    return FORMATS_BY_NAME[name]


_searched_for_video_formats = False


def search_for_video_formats():
    global _searched_for_video_formats
    if not _searched_for_video_formats:
        list(get_app_submodules("video_formats"))
        _searched_for_video_formats = True


# Define default video formats
register_video_format(
    Format("fullwidth", _("Full width"), "richtext-video full-width", "width-800")
)
register_video_format(
    Format("left", _("Left-aligned"), "richtext-video left", "width-500")
)
register_video_format(
    Format("right", _("Right-aligned"), "richtext-video right", "width-500")
)
