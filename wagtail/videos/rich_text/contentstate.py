"""
Draftail / contentstate conversion
"""
from draftjs_exporter.dom import DOM

from wagtail.admin.rich_text.converters.contentstate_models import Entity
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    AtomicBlockEntityElementHandler,
)
from wagtail.videos import get_video_model
from wagtail.videos.formats import get_video_format
from wagtail.videos.shortcuts import get_rendition_or_not_found


def video_entity(props):
    """
    Helper to construct elements of the form
    <embed alt="Right-aligned video" embedtype="video" format="right" id="1"/>
    when converting from contentstate data
    """
    return DOM.create_element(
        "embed",
        {
            "embedtype": "video",
            "format": props.get("format"),
            "id": props.get("id"),
            "alt": props.get("alt"),
        },
    )


class VideoElementHandler(AtomicBlockEntityElementHandler):
    """
    Rule for building an video entity when converting from database representation
    to contentstate
    """

    def create_entity(self, name, attrs, state, contentstate):
        Video = get_video_model()
        try:
            video = Video.objects.get(id=attrs["id"])
            video_format = get_video_format(attrs["format"])
            rendition = get_rendition_or_not_found(video, video_format.filter_spec)
            src = rendition.url
        except Video.DoesNotExist:
            src = ""

        return Entity(
            "IMAGE",
            "IMMUTABLE",
            {
                "id": attrs["id"],
                "src": src,
                "alt": attrs.get("alt"),
                "format": attrs["format"],
            },
        )


ContentstateVideoConversionRule = {
    "from_database_format": {
        'embed[embedtype="video"]': VideoElementHandler(),
    },
    "to_database_format": {"entity_decorators": {"IMAGE": video_entity}},
}
