import os

from django import template
from django.conf import settings
from django.core import serializers
from django.template import engines
from django.test import TestCase

from wagtail.core.models import Site

from .utils import Video, get_test_video_file


class TestVideosJinja(TestCase):
    def setUp(self):
        self.engine = engines["jinja2"]

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

    def render(self, string, context=None, request_context=True):
        if context is None:
            context = {}

        # Add a request to the template, to simulate a RequestContext
        if request_context:
            site = Site.objects.get(is_default_site=True)
            request = self.client.get("/test/", HTTP_HOST=site.hostname)
            context["request"] = request

        template = self.engine.from_string(string)
        return template.render(context)

    def get_video_filename(self, video, filterspec):
        """
        Get the generated filename for a resized video
        """
        name, ext = os.path.splitext(os.path.basename(video.file.name))
        return "{}videos/{}.{}{}".format(settings.MEDIA_URL, name, filterspec, ext)

    def test_video(self):
        self.assertHTMLEqual(
            self.render('{{ video(myvideo, "width-200") }}', {"myvideo": self.video}),
            '<img alt="Test video" src="{}" width="200" height="150">'.format(
                self.get_video_filename(self.video, "width-200")
            ),
        )

    def test_video_attributes(self):
        self.assertHTMLEqual(
            self.render(
                '{{ video(myvideo, "width-200", alt="alternate", class="test") }}',
                {"myvideo": self.video},
            ),
            '<img alt="alternate" src="{}" width="200" height="150" class="test">'.format(
                self.get_video_filename(self.video, "width-200")
            ),
        )

    def test_video_assignment(self):
        template = (
            '{% set background=video(myvideo, "width-200") %}'
            "width: {{ background.width }}, url: {{ background.url }}"
        )
        output = "width: 200, url: " + self.get_video_filename(self.video, "width-200")
        self.assertHTMLEqual(self.render(template, {"myvideo": self.video}), output)

    def test_missing_video(self):
        self.assertHTMLEqual(
            self.render(
                '{{ video(myvideo, "width-200") }}', {"myvideo": self.bad_video}
            ),
            '<img alt="missing video" src="/media/not-found" width="0" height="0">',
        )

    def test_invalid_character(self):
        with self.assertRaises(template.TemplateSyntaxError):
            self.render('{{ video(myvideo, "fill-200×200") }}', {"myvideo": self.video})

    def test_chaining_filterspecs(self):
        self.assertHTMLEqual(
            self.render(
                '{{ video(myvideo, "width-200|jpegquality-40") }}',
                {"myvideo": self.video},
            ),
            '<img alt="Test video" src="{}" width="200" height="150">'.format(
                self.get_video_filename(self.video, "width-200.jpegquality-40")
            ),
        )

    def test_video_url(self):
        self.assertRegex(
            self.render(
                '{{ video_url(myvideo, "width-200") }}', {"myvideo": self.video}
            ),
            "/videos/.*/width-200/{}".format(self.video.file.name.split("/")[-1]),
        )

    def test_video_url_custom_view(self):
        self.assertRegex(
            self.render(
                '{{ video_url(myvideo, "width-200", "wagtailvideos_serve_custom_view") }}',
                {"myvideo": self.video},
            ),
            "/testvideos/custom_view/.*/width-200/{}".format(
                self.video.file.name.split("/")[-1]
            ),
        )
