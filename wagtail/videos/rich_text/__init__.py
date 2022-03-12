from django.core.exceptions import ObjectDoesNotExist

from wagtail.core.rich_text import EmbedHandler
from wagtail.videos import get_video_model
from wagtail.videos.formats import get_video_format

# Front-end conversion


class VideoEmbedHandler(EmbedHandler):
    identifier = "video"

    @staticmethod
    def get_model():
        return get_video_model()

    @classmethod
    def expand_db_attributes(cls, attrs):
        """
        Given a dict of attributes from the <embed> tag, return the real HTML
        representation for use on the front-end.
        """
        try:
            video = cls.get_instance(attrs)
        except ObjectDoesNotExist:
            return '<img alt="">'

        video_format = get_video_format(attrs["format"])
        return video_format.video_to_html(video, attrs.get("alt", ""))
