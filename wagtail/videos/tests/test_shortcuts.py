# coding=utf-8
from django.test import TestCase

from wagtail.videos.shortcuts import get_rendition_or_not_found

from .utils import Video, get_test_video_file


class TestShortcuts(TestCase):

    fixtures = ["test.json"]

    def test_fallback_to_not_found(self):
        bad_video = Video.objects.get(id=1)
        good_video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

        rendition = get_rendition_or_not_found(good_video, "width-400")
        self.assertEqual(rendition.width, 400)

        rendition = get_rendition_or_not_found(bad_video, "width-400")
        self.assertEqual(rendition.file.name, "not-found")
