from django.contrib.auth.models import Permission
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from wagtail.videos import get_video_model
from wagtail.videos.tests.utils import get_test_video_file
from wagtail.tests.utils import WagtailTestUtils

Video = get_video_model()
test_file = get_test_video_file()


class TestVideoBulkDeleteView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.user = self.login()

        # Create videos to delete
        self.videos = [
            Video.objects.create(title=f"Test video - {i}", file=test_file)
            for i in range(1, 6)
        ]
        self.url = (
            reverse(
                "wagtail_bulk_action",
                args=(
                    "wagtailvideos",
                    "video",
                    "delete",
                ),
            )
            + "?"
        )
        for video in self.videos:
            self.url += f"id={video.id}&"

    def test_delete_with_limited_permissions(self):
        self.user.is_superuser = False
        self.user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="wagtailadmin", codename="access_admin"
            )
        )
        self.user.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        html = response.content.decode()
        self.assertInHTML(
            "<p>You don't have permission to delete these videos</p>", html
        )

        for video in self.videos:
            self.assertInHTML(
                "<li>{video_title}</li>".format(video_title=video.title), html
            )

        response = self.client.post(self.url)
        # User should be redirected back to the index
        self.assertEqual(response.status_code, 302)

        # Videos should not be deleted
        for video in self.videos:
            self.assertTrue(Video.objects.filter(id=video.id).exists())

    def test_simple(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "wagtailvideos/bulk_actions/confirm_bulk_delete.html"
        )

    def test_delete(self):
        # Make post request
        response = self.client.post(self.url)

        # User should be redirected back to the index
        self.assertEqual(response.status_code, 302)

        # Videos should be deleted
        for video in self.videos:
            self.assertFalse(Video.objects.filter(id=video.id).exists())

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_usage_link(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "wagtailvideos/bulk_actions/confirm_bulk_delete.html"
        )
        for video in self.videos:
            self.assertContains(response, video.usage_url)
        # usage count should be printed for each video
        self.assertContains(response, "Used 0 times", count=5)
