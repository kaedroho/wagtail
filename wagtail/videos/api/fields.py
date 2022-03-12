from collections import OrderedDict

from rest_framework.fields import Field

from ..models import SourceVideoIOError


class VideoRenditionField(Field):
    """
    A field that generates a rendition with the specified filter spec, and serialises
    details of that rendition.

    Example:
    "thumbnail": {
        "url": "/media/videos/myvideo.max-165x165.jpg",
        "width": 165,
        "height": 100,
        "alt": "Video alt text"
    }

    If there is an error with the source video. The dict will only contain a single
    key, "error", indicating this error:

    "thumbnail": {
        "error": "SourceVideoIOError"
    }
    """

    def __init__(self, filter_spec, *args, **kwargs):
        self.filter_spec = filter_spec
        super().__init__(*args, **kwargs)

    def to_representation(self, video):
        try:
            thumbnail = video.get_rendition(self.filter_spec)

            return OrderedDict(
                [
                    ("url", thumbnail.url),
                    ("width", thumbnail.width),
                    ("height", thumbnail.height),
                    ("alt", thumbnail.alt),
                ]
            )
        except SourceVideoIOError:
            return OrderedDict(
                [
                    ("error", "SourceVideoIOError"),
                ]
            )
