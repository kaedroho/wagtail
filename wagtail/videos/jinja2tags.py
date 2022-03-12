import re

from django import template
from jinja2.ext import Extension

from .shortcuts import get_rendition_or_not_found
from .templatetags.wagtailvideos_tags import video_url

allowed_filter_pattern = re.compile(r"^[A-Za-z0-9_\-\.\|]+$")


def video(video, filterspec, **attrs):
    if not video:
        return ""

    if not allowed_filter_pattern.match(filterspec):
        raise template.TemplateSyntaxError(
            "filter specs in 'video' tag may only contain A-Z, a-z, 0-9, dots, hyphens, pipes and underscores. "
            "(given filter: {})".format(filterspec)
        )

    rendition = get_rendition_or_not_found(video, filterspec)

    if attrs:
        return rendition.img_tag(attrs)
    else:
        return rendition


class WagtailVideosExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)

        self.environment.globals.update(
            {
                "video": video,
                "video_url": video_url,
            }
        )


# Nicer import names
videos = WagtailVideosExtension
