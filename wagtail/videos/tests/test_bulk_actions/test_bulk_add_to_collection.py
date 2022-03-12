from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from wagtail.core.models import Collection
from wagtail.videos import get_video_model
from wagtail.videos.tests.utils import get_test_video_file
from wagtail.tests.utils import WagtailTestUtils

Video = get_video_model()
test_file = get_test_video_file()


class TestBulkAddVideosToCollection(TestCase, WagtailTestUtils):
    def setUp(self):
        self.user = self.login()
        self.root_collection = Collection.get_first_root_node()
        self.dest_collection = self.root_collection.add_child(name="Destination")
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
                    "add_to_collection",
                ),
            )
            + "?"
        )
        for video in self.videos:
            self.url += f"id={video.id}&"
        self.post_data = {"collection": str(self.dest_collection.id)}

    def test_add_to_collection_with_limited_permissions(self):
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
            "<p>You don't have permission to add these videos to a collection</p>", html
        )

        for video in self.videos:
            self.assertInHTML(
                "<li>{video_title}</li>".format(video_title=video.title), html
            )

        response = self.client.post(self.url, self.post_data)

        # Videos should not be moved to new collection
        for video in self.videos:
            self.assertEqual(
                Video.objects.get(id=video.id).collection_id, self.root_collection.id
            )

    def test_simple(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "wagtailvideos/bulk_actions/confirm_bulk_add_to_collection.html"
        )

    def test_add_to_collection(self):
        # Make post request
        response = self.client.post(self.url, self.post_data)

        # User should be redirected back to the index
        self.assertEqual(response.status_code, 302)

        # Videos should be moved to new collection
        for video in self.videos:
            self.assertEqual(
                Video.objects.get(id=video.id).collection_id, self.dest_collection.id
            )
