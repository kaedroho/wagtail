from django.test import TestCase

from wagtail.videos.api.fields import VideoThumbnailField

from .utils import Video, get_test_video_file


class TestVideoThumbnailField(TestCase):
    def setUp(self):
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

    def test_api_representation(self):
        rendition = self.video.get_rendition("width-400")
        representation = VideoThumbnailField("width-400").to_representation(self.video)
        self.assertEqual(set(representation.keys()), {"url", "width", "height", "alt"})
        self.assertEqual(representation["url"], rendition.url)
        self.assertEqual(representation["width"], rendition.width)
        self.assertEqual(representation["height"], rendition.height)
        self.assertEqual(representation["alt"], rendition.alt)
