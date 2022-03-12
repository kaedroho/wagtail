# -*- coding: utf-8 -*
import os

from django.conf import settings
from django.core import serializers
from django.test import TestCase

from wagtail.videos.blocks import VideoChooserBlock

from .utils import Video, get_test_video_file


class TestVideoChooserBlock(TestCase):
    def setUp(self):
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

        # Create an video with a missing file, by deserializing fom a python object
        # (which bypasses FileField's attempt to read the file)
        self.bad_video = list(
            serializers.deserialize(
                "python",
                [
                    {
                        "fields": {
                            "title": "missing video",
                            "height": 100,
                            "file": "original_videos/missing-video.jpg",
                            "width": 100,
                        },
                        "model": "wagtailvideos.video",
                    }
                ],
            )
        )[0].object
        self.bad_video.save()

    def get_video_filename(self, video, filterspec):
        """
        Get the generated filename for a resized video
        """
        name, ext = os.path.splitext(os.path.basename(video.file.name))
        return "{}videos/{}.{}{}".format(settings.MEDIA_URL, name, filterspec, ext)

    def test_render(self):
        block = VideoChooserBlock()
        html = block.render(self.video)
        expected_html = (
            '<img alt="Test video" src="{}" width="640" height="480">'.format(
                self.get_video_filename(self.video, "original")
            )
        )

        self.assertHTMLEqual(html, expected_html)

    def test_render_missing(self):
        block = VideoChooserBlock()
        html = block.render(self.bad_video)
        expected_html = (
            '<img alt="missing video" src="/media/not-found" width="0" height="0">'
        )

        self.assertHTMLEqual(html, expected_html)
