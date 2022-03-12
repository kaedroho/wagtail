from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from wagtail.videos import get_video_model
from wagtail.videos.tests.utils import get_test_video_file
from wagtail.tests.utils import WagtailTestUtils

Video = get_video_model()
test_file = get_test_video_file()


def get_tag_list(video):
    return [tag.name for tag in video.tags.all()]


class TestBulkAddTags(TestCase, WagtailTestUtils):
    def setUp(self):
        self.user = self.login()
        self.new_tags = ["first", "second"]
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
                    "add_tags",
                ),
            )
            + "?"
        )
        for video in self.videos:
            self.url += f"id={video.id}&"
        self.post_data = {"tags": ",".join(self.new_tags)}

    def test_add_tags_with_limited_permissions(self):
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
            "<p>You don't have permission to add tags to these videos</p>", html
        )

        for video in self.videos:
            self.assertInHTML(
                "<li>{video_title}</li>".format(video_title=video.title), html
            )

        response = self.client.post(self.url, self.post_data)

        # New tags should not be added to the videos
        for video in self.videos:
            self.assertCountEqual(get_tag_list(Video.objects.get(id=video.id)), [])

    def test_simple(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "wagtailvideos/bulk_actions/confirm_bulk_add_tags.html"
        )

    def test_add_tags(self):
        # Make post request
        response = self.client.post(self.url, self.post_data)

        # User should be redirected back to the index
        self.assertEqual(response.status_code, 302)

        # New tags should not be added to the videos
        for video in self.videos:
            self.assertCountEqual(
                get_tag_list(Video.objects.get(id=video.id)), self.new_tags
            )
