from bs4 import BeautifulSoup
from django.test import TestCase

from wagtail.videos.rich_text import VideoEmbedHandler as FrontendVideoEmbedHandler
from wagtail.videos.rich_text.editor_html import (
    VideoEmbedHandler as EditorHtmlVideoEmbedHandler,
)
from wagtail.tests.utils import WagtailTestUtils

from .utils import Video, get_test_video_file


class TestEditorHtmlVideoEmbedHandler(TestCase, WagtailTestUtils):
    def test_get_db_attributes(self):
        soup = BeautifulSoup(
            '<b data-id="test-id" data-format="test-format" data-alt="test-alt">foo</b>',
            "html5lib",
        )
        tag = soup.b
        result = EditorHtmlVideoEmbedHandler.get_db_attributes(tag)
        self.assertEqual(
            result,
            {
                "alt": "test-alt",
                "id": "test-id",
                "format": "test-format",
            },
        )

    def test_expand_db_attributes_for_editor(self):
        Video.objects.create(id=1, title="Test", file=get_test_video_file())
        result = EditorHtmlVideoEmbedHandler.expand_db_attributes(
            {
                "id": 1,
                "alt": "test-alt",
                "format": "left",
            }
        )
        self.assertTagInHTML(
            (
                '<img data-embedtype="video" data-id="1" data-format="left" '
                'data-alt="test-alt" class="richtext-video left" />'
            ),
            result,
            allow_extra_attrs=True,
        )

    def test_expand_db_attributes_for_editor_nonexistent_video(self):
        self.assertEqual(
            EditorHtmlVideoEmbedHandler.expand_db_attributes({"id": 0}), '<img alt="">'
        )

    def test_expand_db_attributes_for_editor_escapes_alt_text(self):
        Video.objects.create(id=1, title="Test", file=get_test_video_file())
        result = EditorHtmlVideoEmbedHandler.expand_db_attributes(
            {
                "id": 1,
                "alt": 'Arthur "two sheds" Jackson',
                "format": "left",
            }
        )

        self.assertTagInHTML(
            (
                '<img data-embedtype="video" data-id="1" data-format="left" '
                'data-alt="Arthur &quot;two sheds&quot; Jackson" class="richtext-video left" />'
            ),
            result,
            allow_extra_attrs=True,
        )

        self.assertIn('alt="Arthur &quot;two sheds&quot; Jackson"', result)

    def test_expand_db_attributes_for_editor_with_missing_alt(self):
        Video.objects.create(id=1, title="Test", file=get_test_video_file())
        result = EditorHtmlVideoEmbedHandler.expand_db_attributes(
            {
                "id": 1,
                "format": "left",
            }
        )
        self.assertTagInHTML(
            (
                '<img data-embedtype="video" data-id="1" data-format="left" data-alt="" '
                'class="richtext-video left" />'
            ),
            result,
            allow_extra_attrs=True,
        )


class TestFrontendVideoEmbedHandler(TestCase, WagtailTestUtils):
    def test_expand_db_attributes_for_frontend(self):
        Video.objects.create(id=1, title="Test", file=get_test_video_file())
        result = FrontendVideoEmbedHandler.expand_db_attributes(
            {
                "id": 1,
                "alt": "test-alt",
                "format": "left",
            }
        )
        self.assertTagInHTML(
            '<img class="richtext-video left" />', result, allow_extra_attrs=True
        )

    def test_expand_db_attributes_for_frontend_with_nonexistent_video(self):
        result = FrontendVideoEmbedHandler.expand_db_attributes({"id": 0})
        self.assertEqual(result, '<img alt="">')

    def test_expand_db_attributes_for_frontend_escapes_alt_text(self):
        Video.objects.create(id=1, title="Test", file=get_test_video_file())
        result = FrontendVideoEmbedHandler.expand_db_attributes(
            {
                "id": 1,
                "alt": 'Arthur "two sheds" Jackson',
                "format": "left",
            }
        )
        self.assertIn('alt="Arthur &quot;two sheds&quot; Jackson"', result)

    def test_expand_db_attributes_for_frontend_with_missing_alt(self):
        Video.objects.create(id=1, title="Test", file=get_test_video_file())
        result = FrontendVideoEmbedHandler.expand_db_attributes(
            {
                "id": 1,
                "format": "left",
            }
        )
        self.assertTagInHTML(
            '<img class="richtext-video left" alt="" />', result, allow_extra_attrs=True
        )
