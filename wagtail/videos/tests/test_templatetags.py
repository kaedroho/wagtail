from django.template import Variable
from django.test import TestCase

from wagtail.videos.models import Video, Rendition
from wagtail.videos.templatetags.wagtailvideos_tags import VideoNode
from wagtail.videos.tests.utils import get_test_video_file


class VideoNodeTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create an video for running tests on
        cls.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

    def test_render_valid_video_to_string(self):
        """
        Tests that an VideoNode with a valid video renders an img tag
        """
        context = {"video": self.video}
        node = VideoNode(Variable("video"), "original")

        rendered = node.render(context)

        self.assertIn('<img alt="Test video"', rendered)

    def test_render_none_to_string(self):
        """
        Tests that an VideoNode without video renders an empty string
        """
        context = {"video": None}
        node = VideoNode(Variable("video"), "original")

        rendered = node.render(context)

        self.assertEqual(rendered, "")

    def test_render_valid_video_as_context_variable(self):
        """
        Tests that an VideoNode with a valid video and a context variable name
        renders an empty string and puts a rendition in the context variable
        """
        context = {"video": self.video, "video_node": "fake value"}
        node = VideoNode(Variable("video"), "original", "video_node")

        rendered = node.render(context)

        self.assertEqual(rendered, "")
        self.assertIsInstance(context["video_node"], Rendition)

    def test_render_none_as_context_variable(self):
        """
        Tests that an VideoNode without an video and a context variable name
        renders an empty string and puts None in the context variable
        """
        context = {"video": None, "video_node": "fake value"}
        node = VideoNode(Variable("video"), "original", "video_node")

        rendered = node.render(context)

        self.assertEqual(rendered, "")
        self.assertIsNone(context["video_node"])
