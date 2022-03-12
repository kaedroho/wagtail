from rest_framework.fields import Field

from wagtail.api.v2.serializers import BaseSerializer


class VideoDownloadUrlField(Field):
    """
    Serializes the "download_url" field for videos.

    Example:
    "download_url": "/media/videos/a_test_video.jpg"
    """

    def get_attribute(self, instance):
        return instance

    def to_representation(self, video):
        return video.file.url


class VideoSerializer(BaseSerializer):
    download_url = VideoDownloadUrlField(read_only=True)
