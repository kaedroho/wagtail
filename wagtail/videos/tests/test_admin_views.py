import json
import urllib

from django.contrib.auth.models import Group, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.defaultfilters import filesizeformat
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.html import escapejs
from django.utils.http import RFC3986_SUBDELIMS, urlencode
from django.utils.safestring import mark_safe

from wagtail.admin.admin_url_finder import AdminURLFinder
from wagtail.core.models import (
    Collection,
    GroupCollectionPermission,
    get_root_collection_id,
)
from wagtail.videos import get_video_model
from wagtail.videos.models import UploadedVideo
from wagtail.videos.utils import generate_signature
from wagtail.tests.testapp.models import CustomVideo, CustomVideoWithAuthor
from wagtail.tests.utils import WagtailTestUtils

from .utils import Video, get_test_video_file

# Get the chars that Django considers safe to leave unescaped in a URL
urlquote_safechars = RFC3986_SUBDELIMS + str("/~:@")


class TestVideoIndexView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def get(self, params={}):
        return self.client.get(reverse("wagtailvideos:index"), params)

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/index.html")
        self.assertContains(response, "Add an video")

    def test_search(self):
        response = self.get({"q": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query_string"], "Hello")

    def test_pagination(self):
        pages = ["0", "1", "-1", "9999", "Not a page"]
        for page in pages:
            response = self.get({"p": page})
            self.assertEqual(response.status_code, 200)

    def test_pagination_preserves_other_params(self):
        root_collection = Collection.get_first_root_node()
        evil_plans_collection = root_collection.add_child(name="Evil plans")

        for i in range(1, 50):
            self.video = Video.objects.create(
                title="Test video %i" % i,
                file=get_test_video_file(size=(1, 1)),
                collection=evil_plans_collection,
            )

        response = self.get({"collection_id": evil_plans_collection.id, "p": 2})
        self.assertEqual(response.status_code, 200)

        response_body = response.content.decode("utf8")

        # prev link should exist and include collection_id
        self.assertTrue(
            ("?p=1&amp;collection_id=%i" % evil_plans_collection.id) in response_body
            or ("?collection_id=%i&amp;p=1" % evil_plans_collection.id) in response_body
        )
        # next link should exist and include collection_id
        self.assertTrue(
            ("?p=3&amp;collection_id=%i" % evil_plans_collection.id) in response_body
            or ("?collection_id=%i&amp;p=3" % evil_plans_collection.id) in response_body
        )

    def test_ordering(self):
        orderings = ["title", "-created_at"]
        for ordering in orderings:
            response = self.get({"ordering": ordering})
            self.assertEqual(response.status_code, 200)

    def test_collection_order(self):
        root_collection = Collection.get_first_root_node()
        root_collection.add_child(name="Evil plans")
        root_collection.add_child(name="Good plans")

        response = self.get()
        self.assertEqual(
            [collection.name for collection in response.context["collections"]],
            ["Root", "Evil plans", "Good plans"],
        )

    def test_collection_nesting(self):
        root_collection = Collection.get_first_root_node()
        evil_plans = root_collection.add_child(name="Evil plans")
        evil_plans.add_child(name="Eviler plans")

        response = self.get()
        # "Eviler Plans" should be prefixed with &#x21b3 (↳) and 4 non-breaking spaces.
        self.assertContains(response, "&nbsp;&nbsp;&nbsp;&nbsp;&#x21b3 Eviler plans")

    def test_edit_video_link_contains_next_url(self):
        root_collection = Collection.get_first_root_node()
        evil_plans_collection = root_collection.add_child(name="Evil plans")

        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(size=(1, 1)),
            collection=evil_plans_collection,
        )

        response = self.get({"collection_id": evil_plans_collection.id})
        self.assertEqual(response.status_code, 200)

        edit_url = reverse("wagtailvideos:edit", args=(video.id,))
        next_url = urllib.parse.quote(response._request.get_full_path())
        self.assertContains(response, "%s?next=%s" % (edit_url, next_url))

    def test_tags(self):
        video_two_tags = Video.objects.create(
            title="Test video with two tags",
            file=get_test_video_file(),
        )
        video_two_tags.tags.add("one", "two")

        response = self.get()
        self.assertEqual(response.status_code, 200)

        current_tag = response.context["current_tag"]
        self.assertIsNone(current_tag)

        tags = response.context["popular_tags"]
        self.assertTrue(
            [tag.name for tag in tags] == ["one", "two"]
            or [tag.name for tag in tags] == ["two", "one"]
        )

    def test_tag_filtering(self):
        Video.objects.create(
            title="Test video with no tags",
            file=get_test_video_file(),
        )

        video_one_tag = Video.objects.create(
            title="Test video with one tag",
            file=get_test_video_file(),
        )
        video_one_tag.tags.add("one")

        video_two_tags = Video.objects.create(
            title="Test video with two tags",
            file=get_test_video_file(),
        )
        video_two_tags.tags.add("one", "two")

        # no filtering
        response = self.get()
        self.assertEqual(response.context["videos"].paginator.count, 3)

        # filter all videos with tag 'one'
        response = self.get({"tag": "one"})
        self.assertEqual(response.context["videos"].paginator.count, 2)

        # filter all videos with tag 'two'
        response = self.get({"tag": "two"})
        self.assertEqual(response.context["videos"].paginator.count, 1)

    def test_tag_filtering_preserves_other_params(self):
        for i in range(1, 100):
            video = Video.objects.create(
                title="Test video %i" % i,
                file=get_test_video_file(size=(1, 1)),
            )
            if i % 2 != 0:
                video.tags.add("even")
                video.save()

        response = self.get({"tag": "even", "p": 2})
        self.assertEqual(response.status_code, 200)

        response_body = response.content.decode("utf8")

        # prev link should exist and include tag
        self.assertTrue(
            "?p=2&amp;tag=even" in response_body or "?tag=even&amp;p=1" in response_body
        )
        # next link should exist and include tag
        self.assertTrue(
            "?p=3&amp;tag=even" in response_body or "?tag=even&amp;p=3" in response_body
        )


class TestVideoAddView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def get(self, params={}):
        return self.client.get(reverse("wagtailvideos:add"), params)

    def post(self, post_data={}):
        return self.client.post(reverse("wagtailvideos:add"), post_data)

    def test_get(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/add.html")

        # as standard, only the root collection exists and so no 'Collection' option
        # is displayed on the form
        self.assertNotContains(response, '<label for="id_collection">')

        # Ensure the form supports file uploads
        self.assertContains(response, 'enctype="multipart/form-data"')

        # draftail should NOT be a standard JS include on this page
        self.assertNotContains(response, "wagtailadmin/js/draftail.js")

    def test_get_with_collections(self):
        root_collection = Collection.get_first_root_node()
        root_collection.add_child(name="Evil plans")

        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/add.html")

        self.assertContains(response, '<label for="id_collection">')
        self.assertContains(response, "Evil plans")

    def test_get_with_collection_nesting(self):
        root_collection = Collection.get_first_root_node()
        evil_plans = root_collection.add_child(name="Evil plans")
        evil_plans.add_child(name="Eviler plans")

        response = self.get()
        # "Eviler Plans" should be prefixed with &#x21b3 (↳) and 4 non-breaking spaces.
        self.assertContains(response, "&nbsp;&nbsp;&nbsp;&nbsp;&#x21b3 Eviler plans")

    @override_settings(WAGTAILIMAGES_IMAGE_MODEL="tests.CustomVideo")
    def test_get_with_custom_video_model(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/add.html")

        # Ensure the form supports file uploads
        self.assertContains(response, 'enctype="multipart/form-data"')

        # custom fields should be included
        self.assertContains(response, 'name="fancy_caption"')

        # form media should be imported
        self.assertContains(response, "wagtailadmin/js/draftail.js")

    def test_add(self):
        response = self.post(
            {
                "title": "Test video",
                "file": SimpleUploadedFile(
                    "test.png", get_test_video_file().file.getvalue()
                ),
            }
        )

        # Should redirect back to index
        self.assertRedirects(response, reverse("wagtailvideos:index"))

        # Check that the video was created
        videos = Video.objects.filter(title="Test video")
        self.assertEqual(videos.count(), 1)

        # Test that size was populated correctly
        video = videos.first()
        self.assertEqual(video.width, 640)
        self.assertEqual(video.height, 480)

        # Test that the file_size/hash fields were set
        self.assertTrue(video.file_size)
        self.assertTrue(video.file_hash)

        # Test that it was placed in the root collection
        root_collection = Collection.get_first_root_node()
        self.assertEqual(video.collection, root_collection)

    @override_settings(
        DEFAULT_FILE_STORAGE="wagtail.tests.dummy_external_storage.DummyExternalStorage"
    )
    def test_add_with_external_file_storage(self):
        response = self.post(
            {
                "title": "Test video",
                "file": SimpleUploadedFile(
                    "test.png", get_test_video_file().file.getvalue()
                ),
            }
        )

        # Should redirect back to index
        self.assertRedirects(response, reverse("wagtailvideos:index"))

        # Check that the video was created
        self.assertTrue(Video.objects.filter(title="Test video").exists())

    def test_add_no_file_selected(self):
        response = self.post(
            {
                "title": "Test video",
            }
        )

        # Shouldn't redirect anywhere
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/add.html")

        # The form should have an error
        self.assertFormError(response, "form", "file", "This field is required.")

    @override_settings(WAGTAILIMAGES_MAX_UPLOAD_SIZE=1)
    def test_add_too_large_file(self):
        file_content = get_test_video_file().file.getvalue()

        response = self.post(
            {
                "title": "Test video",
                "file": SimpleUploadedFile("test.png", file_content),
            }
        )

        # Shouldn't redirect anywhere
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/add.html")

        # The form should have an error
        self.assertFormError(
            response,
            "form",
            "file",
            "This file is too big ({file_size}). Maximum filesize {max_file_size}.".format(
                file_size=filesizeformat(len(file_content)),
                max_file_size=filesizeformat(1),
            ),
        )

    @override_settings(WAGTAILIMAGES_MAX_IMAGE_PIXELS=1)
    def test_add_too_many_pixels(self):
        file_content = get_test_video_file().file.getvalue()

        response = self.post(
            {
                "title": "Test video",
                "file": SimpleUploadedFile("test.png", file_content),
            }
        )

        # Shouldn't redirect anywhere
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/add.html")

        # The form should have an error
        self.assertFormError(
            response,
            "form",
            "file",
            "This file has too many pixels (307200). Maximum pixels 1.",
        )

    def test_add_with_collections(self):
        root_collection = Collection.get_first_root_node()
        evil_plans_collection = root_collection.add_child(name="Evil plans")

        response = self.post(
            {
                "title": "Test video",
                "file": SimpleUploadedFile(
                    "test.png", get_test_video_file().file.getvalue()
                ),
                "collection": evil_plans_collection.id,
            }
        )

        # Should redirect back to index
        self.assertRedirects(response, reverse("wagtailvideos:index"))

        # Check that the video was created
        videos = Video.objects.filter(title="Test video")
        self.assertEqual(videos.count(), 1)

        # Test that it was placed in the Evil Plans collection
        video = videos.first()
        self.assertEqual(video.collection, evil_plans_collection)

    @override_settings(WAGTAILIMAGES_IMAGE_MODEL="tests.CustomVideo")
    def test_unique_together_validation_error(self):
        root_collection = Collection.get_first_root_node()
        evil_plans_collection = root_collection.add_child(name="Evil plans")

        # another video with a title to collide with
        CustomVideo.objects.create(
            title="Test video",
            file=get_test_video_file(),
            collection=evil_plans_collection,
        )

        response = self.post(
            {
                "title": "Test video",
                "file": SimpleUploadedFile(
                    "test.png", get_test_video_file().file.getvalue()
                ),
                "collection": evil_plans_collection.id,
            }
        )

        # Shouldn't redirect anywhere
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/add.html")

        # error message should be output on the page as a non-field error
        self.assertContains(
            response, "Custom video with this Title and Collection already exists."
        )


class TestVideoAddViewWithLimitedCollectionPermissions(TestCase, WagtailTestUtils):
    def setUp(self):
        add_video_permission = Permission.objects.get(
            content_type__app_label="wagtailvideos", codename="add_video"
        )
        admin_permission = Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )

        root_collection = Collection.get_first_root_node()
        self.evil_plans_collection = root_collection.add_child(name="Evil plans")

        conspirators_group = Group.objects.create(name="Evil conspirators")
        conspirators_group.permissions.add(admin_permission)
        GroupCollectionPermission.objects.create(
            group=conspirators_group,
            collection=self.evil_plans_collection,
            permission=add_video_permission,
        )

        user = self.create_user(
            username="moriarty", email="moriarty@example.com", password="password"
        )
        user.groups.add(conspirators_group)

        self.login(username="moriarty", password="password")

    def get(self, params={}):
        return self.client.get(reverse("wagtailvideos:add"), params)

    def post(self, post_data={}):
        return self.client.post(reverse("wagtailvideos:add"), post_data)

    def test_get(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/add.html")

        # user only has access to one collection, so no 'Collection' option
        # is displayed on the form
        self.assertNotContains(response, '<label for="id_collection">')

    def test_get_with_collection_nesting(self):
        self.evil_plans_collection.add_child(name="Eviler plans")

        response = self.get()
        self.assertEqual(response.status_code, 200)
        # Unlike the above test, the user should have access to multiple Collections.
        self.assertContains(response, '<label for="id_collection">')
        # "Eviler Plans" should be prefixed with &#x21b3 (↳) and 4 non-breaking spaces.
        self.assertContains(response, "&nbsp;&nbsp;&nbsp;&nbsp;&#x21b3 Eviler plans")

    def test_add(self):
        response = self.post(
            {
                "title": "Test video",
                "file": SimpleUploadedFile(
                    "test.png", get_test_video_file().file.getvalue()
                ),
            }
        )

        # User should be redirected back to the index
        self.assertRedirects(response, reverse("wagtailvideos:index"))

        # Video should be created in the 'evil plans' collection,
        # despite there being no collection field in the form, because that's the
        # only one the user has access to
        self.assertTrue(Video.objects.filter(title="Test video").exists())
        self.assertEqual(
            Video.objects.get(title="Test video").collection, self.evil_plans_collection
        )


class TestVideoEditView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.user = self.login()

        # Create an video to edit
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

        self.storage = self.video.file.storage

    def update_from_db(self):
        self.video = Video.objects.get(pk=self.video.pk)

    def get(self, params={}):
        return self.client.get(
            reverse("wagtailvideos:edit", args=(self.video.id,)), params
        )

    def post(self, post_data={}):
        return self.client.post(
            reverse("wagtailvideos:edit", args=(self.video.id,)), post_data
        )

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/edit.html")

        # Ensure the form supports file uploads
        self.assertContains(response, 'enctype="multipart/form-data"')

        # draftail should NOT be a standard JS include on this page
        # (see TestVideoEditViewWithCustomVideoModel - this confirms that form media
        # definitions are being respected)
        self.assertNotContains(response, "wagtailadmin/js/draftail.js")

    def test_simple_with_collection_nesting(self):
        root_collection = Collection.get_first_root_node()
        evil_plans = root_collection.add_child(name="Evil plans")
        evil_plans.add_child(name="Eviler plans")

        response = self.get()
        # "Eviler Plans" should be prefixed with &#x21b3 (↳) and 4 non-breaking spaces.
        self.assertContains(response, "&nbsp;&nbsp;&nbsp;&nbsp;&#x21b3 Eviler plans")

    def test_next_url_is_present_in_edit_form(self):
        root_collection = Collection.get_first_root_node()
        evil_plans_collection = root_collection.add_child(name="Evil plans")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(size=(1, 1)),
            collection=evil_plans_collection,
        )
        expected_next_url = (
            reverse("wagtailvideos:index")
            + "?"
            + urlencode({"collection_id": evil_plans_collection.id})
        )

        response = self.client.get(
            reverse("wagtailvideos:edit", args=(video.id,)), {"next": expected_next_url}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, f'<input type="hidden" value="{expected_next_url}" name="next">'
        )

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_with_usage_count(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/edit.html")
        self.assertContains(response, "Used 0 times")
        expected_url = "/admin/videos/usage/%d/" % self.video.id
        self.assertContains(response, expected_url)

    @override_settings(
        DEFAULT_FILE_STORAGE="wagtail.tests.dummy_external_storage.DummyExternalStorage"
    )
    def test_simple_with_external_storage(self):
        # The view calls get_file_size on the video that closes the file if
        # file_size wasn't previously populated.

        # The view then attempts to reopen the file when rendering the template
        # which caused crashes when certain storage backends were in use.
        # See #1397

        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/edit.html")

    def test_edit(self):
        response = self.post(
            {
                "title": "Edited",
            }
        )

        # Should redirect back to index
        self.assertRedirects(response, reverse("wagtailvideos:index"))

        self.update_from_db()
        self.assertEqual(self.video.title, "Edited")

        url_finder = AdminURLFinder(self.user)
        expected_url = "/admin/videos/%d/" % self.video.id
        self.assertEqual(url_finder.get_edit_url(self.video), expected_url)

    def test_edit_with_next_url(self):
        root_collection = Collection.get_first_root_node()
        evil_plans_collection = root_collection.add_child(name="Evil plans")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(size=(1, 1)),
            collection=evil_plans_collection,
        )
        expected_next_url = (
            reverse("wagtailvideos:index")
            + "?"
            + urlencode({"collection_id": evil_plans_collection.id})
        )

        response = self.client.post(
            reverse("wagtailvideos:edit", args=(video.id,)),
            {
                "title": "Edited",
                "collection": evil_plans_collection.id,
                "next": expected_next_url,
            },
        )
        self.assertRedirects(response, expected_next_url)

        video.refresh_from_db()
        self.assertEqual(video.title, "Edited")

    def test_edit_with_limited_permissions(self):
        self.user.is_superuser = False
        self.user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="wagtailadmin", codename="access_admin"
            )
        )
        self.user.save()

        response = self.post(
            {
                "title": "Edited",
            }
        )
        self.assertEqual(response.status_code, 302)

        url_finder = AdminURLFinder(self.user)
        self.assertIsNone(url_finder.get_edit_url(self.video))

    def test_edit_with_new_video_file(self):
        file_content = get_test_video_file().file.getvalue()

        # Change the file size/hash of the video
        self.video.file_size = 100000
        self.video.file_hash = "abcedf"
        self.video.save()

        response = self.post(
            {
                "title": "Edited",
                "file": SimpleUploadedFile("new.png", file_content),
            }
        )

        # Should redirect back to index
        self.assertRedirects(response, reverse("wagtailvideos:index"))

        self.update_from_db()
        self.assertNotEqual(self.video.file_size, 100000)
        self.assertNotEqual(self.video.file_hash, "abcedf")

    @override_settings(
        DEFAULT_FILE_STORAGE="wagtail.tests.dummy_external_storage.DummyExternalStorage"
    )
    def test_edit_with_new_video_file_and_external_storage(self):
        file_content = get_test_video_file().file.getvalue()

        # Change the file size/hash of the video
        self.video.file_size = 100000
        self.video.file_hash = "abcedf"
        self.video.save()

        response = self.post(
            {
                "title": "Edited",
                "file": SimpleUploadedFile("new.png", file_content),
            }
        )

        # Should redirect back to index
        self.assertRedirects(response, reverse("wagtailvideos:index"))

        self.update_from_db()
        self.assertNotEqual(self.video.file_size, 100000)
        self.assertNotEqual(self.video.file_hash, "abcedf")

    def test_with_missing_video_file(self):
        self.video.file.delete(False)

        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/edit.html")

    def check_get_missing_file_displays_warning(self):
        # Need to recreate video to use a custom storage per test.
        video = Video.objects.create(title="Test video", file=get_test_video_file())
        video.file.storage.delete(video.file.name)

        response = self.client.get(reverse("wagtailvideos:edit", args=(video.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/edit.html")
        self.assertContains(response, "File not found")

    def test_get_missing_file_displays_warning_with_default_storage(self):
        self.check_get_missing_file_displays_warning()

    @override_settings(
        DEFAULT_FILE_STORAGE="wagtail.tests.dummy_external_storage.DummyExternalStorage"
    )
    def test_get_missing_file_displays_warning_with_custom_storage(self):
        self.check_get_missing_file_displays_warning()

    def get_content(self, f=None):
        if f is None:
            f = self.video.file
        try:
            if f.closed:
                f.open("rb")
            return f.read()
        finally:
            f.close()

    def test_reupload_same_name(self):
        """
        Checks that reuploading the video file with the same file name
        changes the file name, to avoid browser cache issues (see #3817).
        """
        old_file = self.video.file
        old_size = self.video.file_size
        old_data = self.get_content()

        old_rendition = self.video.get_rendition("fill-5x5")
        old_rendition_data = self.get_content(old_rendition.file)

        new_name = self.video.filename
        new_file = SimpleUploadedFile(
            new_name, get_test_video_file(colour="red").file.getvalue()
        )
        new_size = new_file.size

        response = self.post(
            {
                "title": self.video.title,
                "file": new_file,
            }
        )
        self.assertRedirects(response, reverse("wagtailvideos:index"))
        self.update_from_db()
        self.assertFalse(self.storage.exists(old_file.name))
        self.assertTrue(self.storage.exists(self.video.file.name))
        self.assertNotEqual(self.video.file.name, "original_videos/" + new_name)
        self.assertNotEqual(self.video.file_size, old_size)
        self.assertEqual(self.video.file_size, new_size)
        self.assertNotEqual(self.get_content(), old_data)

        new_rendition = self.video.get_rendition("fill-5x5")
        self.assertNotEqual(old_rendition.file.name, new_rendition.file.name)
        self.assertNotEqual(self.get_content(new_rendition.file), old_rendition_data)

    def test_reupload_different_name(self):
        """
        Checks that reuploading the video file with a different file name
        correctly uses the new file name.
        """
        old_file = self.video.file
        old_size = self.video.file_size
        old_data = self.get_content()

        old_rendition = self.video.get_rendition("fill-5x5")
        old_rendition_data = self.get_content(old_rendition.file)

        new_name = "test_reupload_different_name.png"
        new_file = SimpleUploadedFile(
            new_name, get_test_video_file(colour="red").file.getvalue()
        )
        new_size = new_file.size

        response = self.post(
            {
                "title": self.video.title,
                "file": new_file,
            }
        )
        self.assertRedirects(response, reverse("wagtailvideos:index"))
        self.update_from_db()
        self.assertFalse(self.storage.exists(old_file.name))
        self.assertTrue(self.storage.exists(self.video.file.name))
        self.assertEqual(self.video.file.name, "original_videos/" + new_name)
        self.assertNotEqual(self.video.file_size, old_size)
        self.assertEqual(self.video.file_size, new_size)
        self.assertNotEqual(self.get_content(), old_data)

        new_rendition = self.video.get_rendition("fill-5x5")
        self.assertNotEqual(old_rendition.file.name, new_rendition.file.name)
        self.assertNotEqual(self.get_content(new_rendition.file), old_rendition_data)

    @override_settings(USE_L10N=True, USE_THOUSAND_SEPARATOR=True)
    def test_no_thousand_separators_in_focal_point_editor(self):
        large_video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(size=(1024, 768)),
        )
        response = self.client.get(
            reverse("wagtailvideos:edit", args=(large_video.id,))
        )
        self.assertContains(response, 'data-original-width="1024"')

    @override_settings(WAGTAILIMAGES_IMAGE_MODEL="tests.CustomVideo")
    def test_unique_together_validation_error(self):
        root_collection = Collection.get_first_root_node()
        evil_plans_collection = root_collection.add_child(name="Evil plans")

        # Create an video to edit
        self.video = CustomVideo.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

        # another video with a title to collide with
        CustomVideo.objects.create(
            title="Edited", file=get_test_video_file(), collection=evil_plans_collection
        )

        response = self.post(
            {
                "title": "Edited",
                "collection": evil_plans_collection.id,
            }
        )

        # Shouldn't redirect anywhere
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/edit.html")

        # error message should be output on the page as a non-field error
        self.assertContains(
            response, "Custom video with this Title and Collection already exists."
        )


@override_settings(WAGTAILIMAGES_IMAGE_MODEL="tests.CustomVideo")
class TestVideoEditViewWithCustomVideoModel(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

        # Create an video to edit
        self.video = CustomVideo.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

        self.storage = self.video.file.storage

    def get(self, params={}):
        return self.client.get(
            reverse("wagtailvideos:edit", args=(self.video.id,)), params
        )

    def test_get_with_custom_video_model(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/edit.html")

        # Ensure the form supports file uploads
        self.assertContains(response, 'enctype="multipart/form-data"')

        # form media should be imported
        self.assertContains(response, "wagtailadmin/js/draftail.js")


class TestVideoDeleteView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.user = self.login()

        # Create an video to edit
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

    def get(self, params={}):
        return self.client.get(
            reverse("wagtailvideos:delete", args=(self.video.id,)), params
        )

    def post(self, post_data={}):
        return self.client.post(
            reverse("wagtailvideos:delete", args=(self.video.id,)), post_data
        )

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=False)
    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/confirm_delete.html")
        self.assertNotIn("Used ", str(response.content))

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_usage_link(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/confirm_delete.html")
        self.assertContains(response, "Used 0 times")
        expected_url = "/admin/videos/usage/%d/" % self.video.id
        self.assertContains(response, expected_url)

    def test_delete(self):
        response = self.post()

        # Should redirect back to index
        self.assertRedirects(response, reverse("wagtailvideos:index"))

        # Check that the video was deleted
        videos = Video.objects.filter(title="Test video")
        self.assertEqual(videos.count(), 0)

    def test_delete_with_limited_permissions(self):
        self.user.is_superuser = False
        self.user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="wagtailadmin", codename="access_admin"
            )
        )
        self.user.save()

        response = self.post()
        self.assertEqual(response.status_code, 302)


class TestVideoChooserView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.user = self.login()

    def get(self, params={}):
        return self.client.get(reverse("wagtailvideos:chooser"), params)

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json["step"], "chooser")
        self.assertTemplateUsed(response, "wagtailvideos/chooser/chooser.html")

        # draftail should NOT be a standard JS include on this page
        self.assertNotIn("wagtailadmin/js/draftail.js", response_json["html"])

    def test_simple_with_collection_nesting(self):
        root_collection = Collection.get_first_root_node()
        evil_plans = root_collection.add_child(name="Evil plans")
        evil_plans.add_child(name="Eviler plans")

        response = self.get()
        # "Eviler Plans" should be prefixed with &#x21b3 (↳) and 4 non-breaking spaces.
        self.assertContains(response, "&nbsp;&nbsp;&nbsp;&nbsp;&#x21b3 Eviler plans")

    def test_choose_permissions(self):
        # Create group with access to admin and Chooser permission on one Collection, but not another.
        bakers_group = Group.objects.create(name="Bakers")
        access_admin_perm = Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )
        bakers_group.permissions.add(access_admin_perm)
        # Create the "Bakery" Collection and grant "choose" permission to the Bakers group.
        root = Collection.objects.get(id=get_root_collection_id())
        bakery_collection = root.add_child(instance=Collection(name="Bakery"))
        GroupCollectionPermission.objects.create(
            group=bakers_group,
            collection=bakery_collection,
            permission=Permission.objects.get(
                content_type__app_label="wagtailvideos", codename="choose_video"
            ),
        )
        # Create the "Office" Collection and _don't_ grant any permissions to the Bakers group.
        office_collection = root.add_child(instance=Collection(name="Office"))

        # Create a new user in the Bakers group, and log in as them.
        # Can't use self.user because it's a superuser.
        baker = self.create_user(username="baker", password="password")
        baker.groups.add(bakers_group)
        self.login(username="baker", password="password")

        # Add an video to each Collection.
        sweet_buns = Video.objects.create(
            title="SweetBuns.jpg",
            file=get_test_video_file(),
            collection=bakery_collection,
        )
        poster = Video.objects.create(
            title="PromotionalPoster.jpg",
            file=get_test_video_file(),
            collection=office_collection,
        )

        # Open the video chooser
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/chooser/chooser.html")

        # Confirm that the Baker can see the sweet buns, but not the promotional poster.
        self.assertContains(response, sweet_buns.title)
        self.assertNotContains(response, poster.title)

        # Confirm that the Collection chooser is not visible, because the Baker cannot
        # choose from multiple Collections.
        self.assertNotContains(response, "Collection:")

        # We now let the Baker choose from the Office collection.
        GroupCollectionPermission.objects.create(
            group=Group.objects.get(name="Bakers"),
            collection=Collection.objects.get(name="Office"),
            permission=Permission.objects.get(
                content_type__app_label="wagtailvideos", codename="choose_video"
            ),
        )

        # Open the video chooser again.
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/chooser/chooser.html")

        # Confirm that the Baker can now see both videos.
        self.assertContains(response, sweet_buns.title)
        self.assertContains(response, poster.title)

        # Ensure that the Collection chooser IS visible, because the Baker can now
        # choose from multiple Collections.
        self.assertContains(response, "Collection:")

    @override_settings(WAGTAILIMAGES_IMAGE_MODEL="tests.CustomVideo")
    def test_with_custom_video_model(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json["step"], "chooser")
        self.assertTemplateUsed(response, "wagtailvideos/chooser/chooser.html")

        # custom form fields should be present
        self.assertIn(
            'name="video-chooser-upload-fancy_caption"', response_json["html"]
        )

        # form media imports should appear on the page
        self.assertIn("wagtailadmin/js/draftail.js", response_json["html"])

    def test_search(self):
        response = self.get({"q": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query_string"], "Hello")

    def test_pagination(self):
        pages = ["0", "1", "-1", "9999", "Not a page"]
        for page in pages:
            response = self.get({"p": page})
            self.assertEqual(response.status_code, 200)

    def test_filter_by_tag(self):
        for i in range(0, 10):
            video = Video.objects.create(
                title="Test video %d is even better than the last one" % i,
                file=get_test_video_file(),
            )
            if i % 2 == 0:
                video.tags.add("even")

        response = self.get({"tag": "even"})
        self.assertEqual(response.status_code, 200)

        # Results should include videos tagged 'even'
        self.assertContains(response, "Test video 2 is even better")

        # Results should not include videos that just have 'even' in the title
        self.assertNotContains(response, "Test video 3 is even better")

    def test_construct_queryset_hook_browse(self):
        video = Video.objects.create(
            title="Test video shown",
            file=get_test_video_file(),
            uploaded_by_user=self.user,
        )
        Video.objects.create(
            title="Test video not shown",
            file=get_test_video_file(),
        )

        def filter_videos(videos, request):
            # Filter on `uploaded_by_user` because it is
            # the only default FilterField in search_fields
            return videos.filter(uploaded_by_user=self.user)

        with self.register_hook("construct_video_chooser_queryset", filter_videos):
            response = self.get()
        self.assertEqual(len(response.context["videos"]), 1)
        self.assertEqual(response.context["videos"][0], video)

    def test_construct_queryset_hook_search(self):
        video = Video.objects.create(
            title="Test video shown",
            file=get_test_video_file(),
            uploaded_by_user=self.user,
        )
        Video.objects.create(
            title="Test video not shown",
            file=get_test_video_file(),
        )

        def filter_videos(videos, request):
            # Filter on `uploaded_by_user` because it is
            # the only default FilterField in search_fields
            return videos.filter(uploaded_by_user=self.user)

        with self.register_hook("construct_video_chooser_queryset", filter_videos):
            response = self.get({"q": "Test"})
        self.assertEqual(len(response.context["videos"]), 1)
        self.assertEqual(response.context["videos"][0], video)


class TestVideoChooserChosenView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

        # Create an video to edit
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

    def get(self, params={}):
        return self.client.get(
            reverse("wagtailvideos:video_chosen", args=(self.video.id,)), params
        )

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)

        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json["step"], "video_chosen")


class TestVideoChooserSelectFormatView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

        # Create an video to edit
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

    def get(self, params={}):
        return self.client.get(
            reverse("wagtailvideos:chooser_select_format", args=(self.video.id,)),
            params,
        )

    def post(self, post_data={}):
        return self.client.post(
            reverse("wagtailvideos:chooser_select_format", args=(self.video.id,)),
            post_data,
        )

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json["step"], "select_format")
        self.assertTemplateUsed(response, "wagtailvideos/chooser/select_format.html")

    def test_with_edit_params(self):
        response = self.get(params={"alt_text": "some previous alt text"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value=\\"some previous alt text\\"')
        self.assertNotContains(
            response, 'id=\\"id_video-chooser-insertion-video_is_decorative\\" checked'
        )

    def test_with_edit_params_no_alt_text_marks_as_decorative(self):
        response = self.get(params={"alt_text": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'id=\\"id_video-chooser-insertion-video_is_decorative\\" checked'
        )

    def test_post_response(self):
        response = self.post(
            {
                "video-chooser-insertion-format": "left",
                "video-chooser-insertion-video_is_decorative": False,
                "video-chooser-insertion-alt_text": 'Arthur "two sheds" Jackson',
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json["step"], "video_chosen")
        result = response_json["result"]

        self.assertEqual(result["id"], self.video.id)
        self.assertEqual(result["title"], "Test video")
        self.assertEqual(result["format"], "left")
        self.assertEqual(result["alt"], 'Arthur "two sheds" Jackson')
        self.assertIn('alt="Arthur &quot;two sheds&quot; Jackson"', result["html"])

    def test_post_response_video_is_decorative_discards_alt_text(self):
        response = self.post(
            {
                "video-chooser-insertion-format": "left",
                "video-chooser-insertion-alt_text": 'Arthur "two sheds" Jackson',
                "video-chooser-insertion-video_is_decorative": True,
            }
        )
        response_json = json.loads(response.content.decode())
        result = response_json["result"]

        self.assertEqual(result["alt"], "")
        self.assertIn('alt=""', result["html"])

    def test_post_response_video_is_not_decorative_missing_alt_text(self):
        response = self.post(
            {
                "video-chooser-insertion-format": "left",
                "video-chooser-insertion-alt_text": "",
                "video-chooser-insertion-video_is_decorative": False,
            }
        )
        response_json = json.loads(response.content.decode())
        self.assertIn(
            "Please add some alt text for your video or mark it as decorative",
            response_json["html"],
        )


class TestVideoChooserUploadView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def get(self, params={}):
        return self.client.get(reverse("wagtailvideos:chooser_upload"), params)

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/chooser/upload_form.html")
        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json["step"], "reshow_upload_form")

    def test_upload(self):
        response = self.client.post(
            reverse("wagtailvideos:chooser_upload"),
            {
                "video-chooser-upload-title": "Test video",
                "video-chooser-upload-file": SimpleUploadedFile(
                    "test.png", get_test_video_file().file.getvalue()
                ),
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)

        # Check that the video was created
        videos = Video.objects.filter(title="Test video")
        self.assertEqual(videos.count(), 1)

        # Test that size was populated correctly
        video = videos.first()
        self.assertEqual(video.width, 640)
        self.assertEqual(video.height, 480)

        # Test that the file_size/hash fields were set
        self.assertTrue(video.file_size)
        self.assertTrue(video.file_hash)

    def test_upload_no_file_selected(self):
        response = self.client.post(
            reverse("wagtailvideos:chooser_upload"),
            {
                "video-chooser-upload-title": "Test video",
            },
        )

        # Shouldn't redirect anywhere
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/chooser/upload_form.html")

        # The form should have an error
        self.assertFormError(response, "form", "file", "This field is required.")

    def test_select_format_flag_after_upload_form_error(self):
        submit_url = reverse("wagtailvideos:chooser_upload") + "?select_format=true"
        response = self.client.post(
            submit_url,
            {
                "video-chooser-upload-title": "Test video",
                "video-chooser-upload-file": SimpleUploadedFile(
                    "not_an_video.txt", b"this is not an video"
                ),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/chooser/upload_form.html")
        self.assertFormError(
            response,
            "form",
            "file",
            "Upload a valid video. The file you uploaded was either not an video or a corrupted video.",
        )

        # the action URL of the re-rendered form should include the select_format=true parameter
        # (NB the HTML in the response is embedded in a JS string, so need to escape accordingly)
        expected_action_attr = 'action=\\"%s\\"' % submit_url
        self.assertContains(response, expected_action_attr)

    def test_select_format_flag_after_upload_form_error_bad_extension(self):
        """
        Check the error message is accruate for a valid imate bug invalid file extension.
        """
        submit_url = reverse("wagtailvideos:chooser_upload") + "?select_format=true"
        response = self.client.post(
            submit_url,
            {
                "video-chooser-upload-title": "accidental markdown extension",
                "video-chooser-upload-file": SimpleUploadedFile(
                    "not-an-video.md", get_test_video_file().file.getvalue()
                ),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/chooser/upload_form.html")
        self.assertFormError(
            response,
            "form",
            "file",
            "Not a supported video format. Supported formats: GIF, JPEG, PNG, WEBP.",
        )

        # the action URL of the re-rendered form should include the select_format=true parameter
        # (NB the HTML in the response is embedded in a JS string, so need to escape accordingly)
        expected_action_attr = 'action=\\"%s\\"' % submit_url
        self.assertContains(response, expected_action_attr)

    @override_settings(
        DEFAULT_FILE_STORAGE="wagtail.tests.dummy_external_storage.DummyExternalStorage"
    )
    def test_upload_with_external_storage(self):
        response = self.client.post(
            reverse("wagtailvideos:chooser_upload"),
            {
                "video-chooser-upload-title": "Test video",
                "video-chooser-upload-file": SimpleUploadedFile(
                    "test.png", get_test_video_file().file.getvalue()
                ),
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)

        # Check that the video was created
        self.assertTrue(Video.objects.filter(title="Test video").exists())

    @override_settings(WAGTAILIMAGES_IMAGE_MODEL="tests.CustomVideo")
    def test_unique_together_validation(self):
        root_collection = Collection.get_first_root_node()
        evil_plans_collection = root_collection.add_child(name="Evil plans")
        # another video with a title to collide with
        CustomVideo.objects.create(
            title="Test video",
            file=get_test_video_file(),
            collection=evil_plans_collection,
        )

        response = self.client.post(
            reverse("wagtailvideos:chooser_upload"),
            {
                "video-chooser-upload-title": "Test video",
                "video-chooser-upload-file": SimpleUploadedFile(
                    "test.png", get_test_video_file().file.getvalue()
                ),
                "video-chooser-upload-collection": evil_plans_collection.id,
            },
        )

        # Shouldn't redirect anywhere
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/chooser/upload_form.html")

        # The form should have an error
        self.assertContains(
            response, "Custom video with this Title and Collection already exists."
        )


class TestVideoChooserUploadViewWithLimitedPermissions(TestCase, WagtailTestUtils):
    def setUp(self):
        add_video_permission = Permission.objects.get(
            content_type__app_label="wagtailvideos", codename="add_video"
        )
        admin_permission = Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )

        root_collection = Collection.get_first_root_node()
        self.evil_plans_collection = root_collection.add_child(name="Evil plans")

        conspirators_group = Group.objects.create(name="Evil conspirators")
        conspirators_group.permissions.add(admin_permission)
        GroupCollectionPermission.objects.create(
            group=conspirators_group,
            collection=self.evil_plans_collection,
            permission=add_video_permission,
        )

        user = self.create_user(
            username="moriarty", email="moriarty@example.com", password="password"
        )
        user.groups.add(conspirators_group)

        self.login(username="moriarty", password="password")

    def test_get(self):
        response = self.client.get(reverse("wagtailvideos:chooser_upload"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/chooser/upload_form.html")

        # user only has access to one collection, so no 'Collection' option
        # is displayed on the form
        self.assertNotContains(response, '<label for="id_collection">')

    def test_get_chooser(self):
        response = self.client.get(reverse("wagtailvideos:chooser"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/chooser/chooser.html")

        # user only has access to one collection, so no 'Collection' option
        # is displayed on the form
        self.assertNotContains(response, '<label for="id_collection">')

    def test_add(self):
        response = self.client.post(
            reverse("wagtailvideos:chooser_upload"),
            {
                "video-chooser-upload-title": "Test video",
                "video-chooser-upload-file": SimpleUploadedFile(
                    "test.png", get_test_video_file().file.getvalue()
                ),
            },
        )

        self.assertEqual(response.status_code, 200)

        # Check that the video was created
        videos = Video.objects.filter(title="Test video")
        self.assertEqual(videos.count(), 1)

        # Video should be created in the 'evil plans' collection,
        # despite there being no collection field in the form, because that's the
        # only one the user has access to
        self.assertTrue(Video.objects.filter(title="Test video").exists())
        self.assertEqual(
            Video.objects.get(title="Test video").collection, self.evil_plans_collection
        )


class TestMultipleVideoUploader(TestCase, WagtailTestUtils):
    """
    This tests the multiple video upload views located in wagtailvideos/views/multiple.py
    """

    def setUp(self):
        self.user = self.login()

        # Create an video for running tests on
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

    def test_add(self):
        """
        This tests that the add view responds correctly on a GET request
        """
        # Send request
        response = self.client.get(reverse("wagtailvideos:add_multiple"))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/multiple/add.html")

        # draftail should NOT be a standard JS include on this page
        # (see TestMultipleVideoUploaderWithCustomVideoModel - this confirms that form media
        # definitions are being respected)
        self.assertNotContains(response, "wagtailadmin/js/draftail.js")

    @override_settings(WAGTAILIMAGES_MAX_UPLOAD_SIZE=1000)
    def test_add_max_file_size_context_variables(self):
        response = self.client.get(reverse("wagtailvideos:add_multiple"))

        self.assertEqual(response.context["max_filesize"], 1000)
        self.assertEqual(
            response.context["error_max_file_size"],
            "This file is too big. Maximum filesize 1000\xa0bytes.",
        )

    def test_add_error_max_file_size_escaped(self):
        url = reverse("wagtailvideos:add_multiple")
        template_name = "wagtailvideos/multiple/add.html"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)

        value = "Too big. <br/><br/><a href='/admin/videos/add/'>Try this.</a>"
        response_content = force_str(response.content)
        self.assertNotIn(value, response_content)
        self.assertNotIn(escapejs(value), response_content)

        request = RequestFactory().get(url)
        request.user = self.user
        context = response.context_data.copy()
        context["error_max_file_size"] = mark_safe(force_str(value))
        data = render_to_string(
            template_name,
            context=context,
            request=request,
        )
        self.assertNotIn(value, data)
        self.assertIn(escapejs(value), data)

    def test_add_error_accepted_file_types_escaped(self):
        url = reverse("wagtailvideos:add_multiple")
        template_name = "wagtailvideos/multiple/add.html"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)

        value = "Invalid video type. <a href='/help'>Get help.</a>"
        response_content = force_str(response.content)
        self.assertNotIn(value, response_content)
        self.assertNotIn(escapejs(value), response_content)

        request = RequestFactory().get(url)
        request.user = self.user
        context = response.context_data.copy()
        context["error_accepted_file_types"] = mark_safe(force_str(value))
        data = render_to_string(
            template_name,
            context=context,
            request=request,
        )
        self.assertNotIn(value, data)
        self.assertIn(escapejs(value), data)

    def test_add_post(self):
        """
        This tests that a POST request to the add view saves the video and returns an edit form
        """
        response = self.client.post(
            reverse("wagtailvideos:add_multiple"),
            {
                "title": "test title",
                "files[]": SimpleUploadedFile(
                    "test.png", get_test_video_file().file.getvalue()
                ),
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertTemplateUsed(
            response, "wagtailadmin/generic/multiple_upload/edit_form.html"
        )

        # Check video
        self.assertIn("video", response.context)
        self.assertEqual(response.context["video"].title, "test title")
        self.assertTrue(response.context["video"].file_size)
        self.assertTrue(response.context["video"].file_hash)

        # Check video title
        video = get_video_model().objects.get(title="test title")
        self.assertNotIn("title", video.filename)
        self.assertIn(".png", video.filename)

        # Check form
        self.assertIn("form", response.context)
        self.assertEqual(
            response.context["edit_action"],
            "/admin/videos/multiple/%d/" % response.context["video"].id,
        )
        self.assertEqual(
            response.context["delete_action"],
            "/admin/videos/multiple/%d/delete/" % response.context["video"].id,
        )
        self.assertEqual(response.context["form"].initial["title"], "test title")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("form", response_json)
        self.assertIn("video_id", response_json)
        self.assertIn("success", response_json)
        self.assertEqual(response_json["video_id"], response.context["video"].id)
        self.assertTrue(response_json["success"])

    def test_add_post_no_title(self):
        """
        A POST request to the add view without the title value saves the video and uses file title if needed
        """
        response = self.client.post(
            reverse("wagtailvideos:add_multiple"),
            {
                "files[]": SimpleUploadedFile(
                    "no-title.png", get_test_video_file().file.getvalue()
                ),
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Check video
        self.assertIn("video", response.context)
        self.assertTrue(response.context["video"].file_size)
        self.assertTrue(response.context["video"].file_hash)

        # Check video title
        video = get_video_model().objects.get(title="no-title.png")
        self.assertEqual("no-title.png", video.filename)
        self.assertIn(".png", video.filename)

        # Check form
        self.assertIn("form", response.context)
        self.assertEqual(response.context["form"].initial["title"], "no-title.png")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("form", response_json)
        self.assertIn("success", response_json)

    def test_add_post_nofile(self):
        """
        This tests that the add view checks for a file when a user POSTs to it
        """
        response = self.client.post(reverse("wagtailvideos:add_multiple"), {})

        # Check response
        self.assertEqual(response.status_code, 400)

    def test_add_post_badfile(self):
        """
        The add view must check that the uploaded file is a valid video
        """
        response = self.client.post(
            reverse("wagtailvideos:add_multiple"),
            {
                "files[]": SimpleUploadedFile("test.png", b"This is not an video!"),
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertNotIn("video_id", response_json)
        self.assertNotIn("form", response_json)
        self.assertIn("success", response_json)
        self.assertIn("error_message", response_json)
        self.assertFalse(response_json["success"])
        self.assertEqual(
            response_json["error_message"],
            "Upload a valid video. The file you uploaded was either not an video or a corrupted video.",
        )

    def test_add_post_bad_extension(self):
        """
        The add view must check that the uploaded file extension is a valid
        """
        response = self.client.post(
            reverse("wagtailvideos:add_multiple"),
            {
                "files[]": SimpleUploadedFile(
                    "test.txt", get_test_video_file().file.getvalue()
                ),
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertNotIn("video_id", response_json)
        self.assertNotIn("form", response_json)
        self.assertIn("success", response_json)
        self.assertIn("error_message", response_json)
        self.assertFalse(response_json["success"])
        self.assertEqual(
            response_json["error_message"],
            "Not a supported video format. Supported formats: GIF, JPEG, PNG, WEBP.",
        )

    def test_edit_get(self):
        """
        This tests that a GET request to the edit view returns a 405 "METHOD NOT ALLOWED" response
        """
        # Send request
        response = self.client.get(
            reverse("wagtailvideos:edit_multiple", args=(self.video.id,))
        )

        # Check response
        self.assertEqual(response.status_code, 405)

    def test_edit_post(self):
        """
        This tests that a POST request to the edit view edits the video
        """
        # Send request
        response = self.client.post(
            reverse("wagtailvideos:edit_multiple", args=(self.video.id,)),
            {
                ("video-%d-title" % self.video.id): "New title!",
                ("video-%d-tags" % self.video.id): "cromarty, finisterre",
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("video_id", response_json)
        self.assertNotIn("form", response_json)
        self.assertIn("success", response_json)
        self.assertEqual(response_json["video_id"], self.video.id)
        self.assertTrue(response_json["success"])

        # test that changes have been applied to the video
        video = Video.objects.get(id=self.video.id)
        self.assertEqual(video.title, "New title!")
        self.assertIn("cromarty", video.tags.names())

    def test_edit_post_validation_error(self):
        """
        This tests that a POST request to the edit page returns a json document with "success=False"
        and a form with the validation error indicated
        """
        # Send request
        response = self.client.post(
            reverse("wagtailvideos:edit_multiple", args=(self.video.id,)),
            {
                ("video-%d-title" % self.video.id): "",  # Required
                ("video-%d-tags" % self.video.id): "",
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertTemplateUsed(
            response, "wagtailadmin/generic/multiple_upload/edit_form.html"
        )

        # Check that a form error was raised
        self.assertFormError(response, "form", "title", "This field is required.")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("video_id", response_json)
        self.assertIn("form", response_json)
        self.assertIn("success", response_json)
        self.assertEqual(response_json["video_id"], self.video.id)
        self.assertFalse(response_json["success"])

    def test_delete_get(self):
        """
        This tests that a GET request to the delete view returns a 405 "METHOD NOT ALLOWED" response
        """
        # Send request
        response = self.client.get(
            reverse("wagtailvideos:delete_multiple", args=(self.video.id,))
        )

        # Check response
        self.assertEqual(response.status_code, 405)

    def test_delete_post(self):
        """
        This tests that a POST request to the delete view deletes the video
        """
        # Send request
        response = self.client.post(
            reverse("wagtailvideos:delete_multiple", args=(self.video.id,))
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Make sure the video is deleted
        self.assertFalse(Video.objects.filter(id=self.video.id).exists())

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("video_id", response_json)
        self.assertIn("success", response_json)
        self.assertEqual(response_json["video_id"], self.video.id)
        self.assertTrue(response_json["success"])


@override_settings(WAGTAILIMAGES_IMAGE_MODEL="tests.CustomVideo")
class TestMultipleVideoUploaderWithCustomVideoModel(TestCase, WagtailTestUtils):
    """
    This tests the multiple video upload views located in wagtailvideos/views/multiple.py
    with a custom video model
    """

    def setUp(self):
        self.login()

        # Create an video for running tests on
        self.video = CustomVideo.objects.create(
            title="test-video.png",
            file=get_test_video_file(),
        )

    def test_add(self):
        """
        This tests that the add view responds correctly on a GET request
        """
        # Send request
        response = self.client.get(reverse("wagtailvideos:add_multiple"))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/multiple/add.html")

        # response should include form media for the video edit form
        self.assertContains(response, "wagtailadmin/js/draftail.js")

    def test_add_post(self):
        """
        This tests that a POST request to the add view saves the video and returns an edit form
        """
        response = self.client.post(
            reverse("wagtailvideos:add_multiple"),
            {
                "files[]": SimpleUploadedFile(
                    "test.png", get_test_video_file().file.getvalue()
                ),
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertTemplateUsed(
            response, "wagtailadmin/generic/multiple_upload/edit_form.html"
        )

        # Check video
        self.assertIn("video", response.context)
        self.assertEqual(response.context["video"].title, "test.png")
        self.assertTrue(response.context["video"].file_size)
        self.assertTrue(response.context["video"].file_hash)

        # Check form
        self.assertIn("form", response.context)
        self.assertEqual(response.context["form"].initial["title"], "test.png")
        self.assertIn("caption", response.context["form"].fields)
        self.assertNotIn("not_editable_field", response.context["form"].fields)
        self.assertEqual(
            response.context["edit_action"],
            "/admin/videos/multiple/%d/" % response.context["video"].id,
        )
        self.assertEqual(
            response.context["delete_action"],
            "/admin/videos/multiple/%d/delete/" % response.context["video"].id,
        )

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("form", response_json)
        self.assertIn("success", response_json)
        self.assertTrue(response_json["success"])

    def test_add_post_badfile(self):
        """
        The add view must check that the uploaded file is a valid video
        """
        response = self.client.post(
            reverse("wagtailvideos:add_multiple"),
            {
                "files[]": SimpleUploadedFile("test.png", b"This is not an video!"),
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertNotIn("video_id", response_json)
        self.assertNotIn("form", response_json)
        self.assertIn("success", response_json)
        self.assertIn("error_message", response_json)
        self.assertFalse(response_json["success"])
        self.assertEqual(
            response_json["error_message"],
            "Upload a valid video. The file you uploaded was either not an video or a corrupted video.",
        )

    def test_unique_together_validation_error(self):
        """
        If unique_together validation fails, create an UploadedVideo and return a form so the
        user can fix it
        """
        root_collection = Collection.get_first_root_node()
        new_collection = root_collection.add_child(name="holiday snaps")
        self.video.collection = new_collection
        self.video.save()

        video_count_before = CustomVideo.objects.count()
        uploaded_video_count_before = UploadedVideo.objects.count()

        response = self.client.post(
            reverse("wagtailvideos:add_multiple"),
            {
                "files[]": SimpleUploadedFile(
                    "test-video.png", get_test_video_file().file.getvalue()
                ),
                "collection": new_collection.id,
            },
        )

        video_count_after = CustomVideo.objects.count()
        uploaded_video_count_after = UploadedVideo.objects.count()

        # an UploadedVideo should have been created now, but not a CustomVideo
        self.assertEqual(video_count_after, video_count_before)
        self.assertEqual(uploaded_video_count_after, uploaded_video_count_before + 1)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertTemplateUsed(
            response, "wagtailadmin/generic/multiple_upload/edit_form.html"
        )

    def test_edit_post(self):
        """
        This tests that a POST request to the edit view edits the video
        """
        # Send request
        response = self.client.post(
            reverse("wagtailvideos:edit_multiple", args=(self.video.id,)),
            {
                ("video-%d-title" % self.video.id): "New title!",
                ("video-%d-tags" % self.video.id): "footwear, dystopia",
                (
                    "video-%d-caption" % self.video.id
                ): "a boot stamping on a human face, forever",
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("video_id", response_json)
        self.assertNotIn("form", response_json)
        self.assertIn("success", response_json)
        self.assertEqual(response_json["video_id"], self.video.id)
        self.assertTrue(response_json["success"])

        # check that video has been updated
        new_video = CustomVideo.objects.get(id=self.video.id)
        self.assertEqual(new_video.title, "New title!")
        self.assertEqual(new_video.caption, "a boot stamping on a human face, forever")
        self.assertIn("footwear", new_video.tags.names())

    def test_edit_fails_unique_together_validation(self):
        """
        Check that the form returned on failing a unique-together validation error
        includes that error message, despite it being a non-field error
        """
        root_collection = Collection.get_first_root_node()
        new_collection = root_collection.add_child(name="holiday snaps")
        # create another video for the edited title to collide with
        CustomVideo.objects.create(
            title="The Eiffel Tower",
            file=get_test_video_file(),
            collection=new_collection,
        )

        response = self.client.post(
            reverse("wagtailvideos:edit_multiple", args=(self.video.id,)),
            {
                ("video-%d-title" % self.video.id): "The Eiffel Tower",
                ("video-%d-collection" % self.video.id): new_collection.id,
                ("video-%d-tags" % self.video.id): "",
                ("video-%d-caption" % self.video.id): "ooh la la",
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertTemplateUsed(
            response, "wagtailadmin/generic/multiple_upload/edit_form.html"
        )

        response_json = json.loads(response.content.decode())
        # Check JSON
        self.assertEqual(response_json["video_id"], self.video.id)
        self.assertFalse(response_json["success"])

        # Check that a form error was raised
        self.assertIn(
            "Custom video with this Title and Collection already exists.",
            response_json["form"],
        )

    def test_delete_post(self):
        """
        This tests that a POST request to the delete view deletes the video
        """
        # Send request
        response = self.client.post(
            reverse("wagtailvideos:delete_multiple", args=(self.video.id,))
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Make sure the video is deleted
        self.assertFalse(Video.objects.filter(id=self.video.id).exists())

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("video_id", response_json)
        self.assertIn("success", response_json)
        self.assertEqual(response_json["video_id"], self.video.id)
        self.assertTrue(response_json["success"])

        # check that video has been deleted
        self.assertEqual(CustomVideo.objects.filter(id=self.video.id).count(), 0)


@override_settings(WAGTAILIMAGES_IMAGE_MODEL="tests.CustomVideoWithAuthor")
class TestMultipleVideoUploaderWithCustomRequiredFields(TestCase, WagtailTestUtils):
    """
    This tests the multiple video upload views located in wagtailvideos/views/multiple.py
    with a custom video model
    """

    def setUp(self):
        self.user = self.login()

        # Create an UploadedVideo for running tests on
        self.uploaded_video = UploadedVideo.objects.create(
            file=get_test_video_file(),
            uploaded_by_user=self.user,
        )

    def test_add(self):
        """
        This tests that the add view responds correctly on a GET request
        """
        # Send request
        response = self.client.get(reverse("wagtailvideos:add_multiple"))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/multiple/add.html")

    def test_add_post(self):
        """
        A POST request to the add view should create an UploadedVideo rather than an video,
        as we do not have enough data to pass CustomVideoWithAuthor's validation yet
        """
        video_count_before = CustomVideoWithAuthor.objects.count()
        uploaded_video_count_before = UploadedVideo.objects.count()

        response = self.client.post(
            reverse("wagtailvideos:add_multiple"),
            {
                "files[]": SimpleUploadedFile(
                    "test.png", get_test_video_file().file.getvalue()
                ),
            },
        )

        video_count_after = CustomVideoWithAuthor.objects.count()
        uploaded_video_count_after = UploadedVideo.objects.count()

        # an UploadedVideo should have been created now, but not a CustomVideoWithAuthor
        self.assertEqual(video_count_after, video_count_before)
        self.assertEqual(uploaded_video_count_after, uploaded_video_count_before + 1)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertTemplateUsed(
            response, "wagtailadmin/generic/multiple_upload/edit_form.html"
        )

        # Check video
        self.assertIn("uploaded_video", response.context)
        self.assertTrue(response.context["uploaded_video"].file.name)

        # Check form
        self.assertIn("form", response.context)
        self.assertEqual(response.context["form"].initial["title"], "test.png")
        self.assertIn("author", response.context["form"].fields)
        self.assertEqual(
            response.context["edit_action"],
            "/admin/videos/multiple/create_from_uploaded_video/%d/"
            % response.context["uploaded_video"].id,
        )
        self.assertEqual(
            response.context["delete_action"],
            "/admin/videos/multiple/delete_upload/%d/"
            % response.context["uploaded_video"].id,
        )

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("form", response_json)
        self.assertIn("success", response_json)
        self.assertTrue(response_json["success"])

    def test_add_post_badfile(self):
        """
        The add view must check that the uploaded file is a valid video
        """
        response = self.client.post(
            reverse("wagtailvideos:add_multiple"),
            {
                "files[]": SimpleUploadedFile("test.png", b"This is not an video!"),
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertNotIn("video_id", response_json)
        self.assertNotIn("form", response_json)
        self.assertIn("success", response_json)
        self.assertIn("error_message", response_json)
        self.assertFalse(response_json["success"])
        self.assertEqual(
            response_json["error_message"],
            "Upload a valid video. The file you uploaded was either not an video or a corrupted video.",
        )

    def test_create_from_upload_invalid_post(self):
        """
        Posting an invalid form to the create_from_uploaded_video view throws a validation error and leaves the
        UploadedVideo intact
        """
        video_count_before = CustomVideoWithAuthor.objects.count()
        uploaded_video_count_before = UploadedVideo.objects.count()

        # Send request
        response = self.client.post(
            reverse(
                "wagtailvideos:create_multiple_from_uploaded_video",
                args=(self.uploaded_video.id,),
            ),
            {
                ("uploaded-video-%d-title" % self.uploaded_video.id): "New title!",
                ("uploaded-video-%d-tags" % self.uploaded_video.id): "",
                ("uploaded-video-%d-author" % self.uploaded_video.id): "",
            },
        )

        video_count_after = CustomVideoWithAuthor.objects.count()
        uploaded_video_count_after = UploadedVideo.objects.count()

        # no changes to video / UploadedVideo count
        self.assertEqual(video_count_after, video_count_before)
        self.assertEqual(uploaded_video_count_after, uploaded_video_count_before)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Check form
        self.assertIn("form", response.context)
        self.assertIn("author", response.context["form"].fields)
        self.assertEqual(
            response.context["edit_action"],
            "/admin/videos/multiple/create_from_uploaded_video/%d/"
            % response.context["uploaded_video"].id,
        )
        self.assertEqual(
            response.context["delete_action"],
            "/admin/videos/multiple/delete_upload/%d/"
            % response.context["uploaded_video"].id,
        )
        self.assertFormError(response, "form", "author", "This field is required.")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("form", response_json)
        self.assertIn("New title!", response_json["form"])
        self.assertFalse(response_json["success"])

    def test_create_from_upload(self):
        """
        Posting a valid form to the create_from_uploaded_video view will create the video
        """
        video_count_before = CustomVideoWithAuthor.objects.count()
        uploaded_video_count_before = UploadedVideo.objects.count()

        # Send request
        response = self.client.post(
            reverse(
                "wagtailvideos:create_multiple_from_uploaded_video",
                args=(self.uploaded_video.id,),
            ),
            {
                ("uploaded-video-%d-title" % self.uploaded_video.id): "New title!",
                (
                    "uploaded-video-%d-tags" % self.uploaded_video.id
                ): "abstract, squares",
                ("uploaded-video-%d-author" % self.uploaded_video.id): "Piet Mondrian",
            },
        )

        video_count_after = CustomVideoWithAuthor.objects.count()
        uploaded_video_count_after = UploadedVideo.objects.count()

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("video_id", response_json)
        self.assertTrue(response_json["success"])

        # Video should have been created, UploadedVideo deleted
        self.assertEqual(video_count_after, video_count_before + 1)
        self.assertEqual(uploaded_video_count_after, uploaded_video_count_before - 1)

        video = CustomVideoWithAuthor.objects.get(id=response_json["video_id"])
        self.assertEqual(video.title, "New title!")
        self.assertEqual(video.author, "Piet Mondrian")
        self.assertTrue(video.file.name)
        self.assertTrue(video.file_hash)
        self.assertTrue(video.file_size)
        self.assertEqual(video.width, 640)
        self.assertEqual(video.height, 480)
        self.assertIn("abstract", video.tags.names())

    def test_delete_uploaded_video(self):
        """
        This tests that a POST request to the delete view deletes the UploadedVideo
        """
        # Send request
        response = self.client.post(
            reverse(
                "wagtailvideos:delete_upload_multiple", args=(self.uploaded_video.id,)
            )
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Make sure the video is deleted
        self.assertFalse(
            UploadedVideo.objects.filter(id=self.uploaded_video.id).exists()
        )

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertTrue(response_json["success"])


class TestURLGeneratorView(TestCase, WagtailTestUtils):
    def setUp(self):
        # Create an video for running tests on
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

        # Login
        self.user = self.login()

    def test_get(self):
        """
        This tests that the view responds correctly for a user with edit permissions on this video
        """
        # Get
        response = self.client.get(
            reverse("wagtailvideos:url_generator", args=(self.video.id,))
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/url_generator.html")

    def test_get_bad_permissions(self):
        """
        This tests that the view returns a "permission denied" redirect if a user without correct
        permissions attempts to access it
        """
        # Remove privileges from user
        self.user.is_superuser = False
        self.user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="wagtailadmin", codename="access_admin"
            )
        )
        self.user.save()

        # Get
        response = self.client.get(
            reverse("wagtailvideos:url_generator", args=(self.video.id,))
        )

        # Check response
        self.assertRedirects(response, reverse("wagtailadmin_home"))


class TestGenerateURLView(TestCase, WagtailTestUtils):
    def setUp(self):
        # Create an video for running tests on
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

        # Login
        self.user = self.login()

    def test_get(self):
        """
        This tests that the view responds correctly for a user with edit permissions on this video
        """
        # Get
        response = self.client.get(
            reverse("wagtailvideos:generate_url", args=(self.video.id, "fill-800x600"))
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Check JSON
        content_json = json.loads(response.content.decode())

        self.assertEqual(set(content_json.keys()), {"url", "preview_url"})

        expected_url = (
            "http://localhost/videos/%(signature)s/%(video_id)d/fill-800x600/"
            % {
                "signature": urllib.parse.quote(
                    generate_signature(self.video.id, "fill-800x600"),
                    safe=urlquote_safechars,
                ),
                "video_id": self.video.id,
            }
        )
        self.assertEqual(content_json["url"], expected_url)

        expected_preview_url = reverse(
            "wagtailvideos:preview", args=(self.video.id, "fill-800x600")
        )
        self.assertEqual(content_json["preview_url"], expected_preview_url)

    def test_get_bad_permissions(self):
        """
        This tests that the view gives a 403 if a user without correct permissions attempts to access it
        """
        # Remove privileges from user
        self.user.is_superuser = False
        self.user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="wagtailadmin", codename="access_admin"
            )
        )
        self.user.save()

        # Get
        response = self.client.get(
            reverse("wagtailvideos:generate_url", args=(self.video.id, "fill-800x600"))
        )

        # Check response
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response["Content-Type"], "application/json")

        # Check JSON
        self.assertJSONEqual(
            response.content.decode(),
            json.dumps(
                {
                    "error": "You do not have permission to generate a URL for this video.",
                }
            ),
        )

    def test_get_bad_video(self):
        """
        This tests that the view gives a 404 response if a user attempts to use it with an video which doesn't exist
        """
        # Get
        response = self.client.get(
            reverse(
                "wagtailvideos:generate_url", args=(self.video.id + 1, "fill-800x600")
            )
        )

        # Check response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response["Content-Type"], "application/json")

        # Check JSON
        self.assertJSONEqual(
            response.content.decode(),
            json.dumps(
                {
                    "error": "Cannot find video.",
                }
            ),
        )

    def test_get_bad_filter_spec(self):
        """
        This tests that the view gives a 400 response if the user attempts to use it with an invalid filter spec
        """
        # Get
        response = self.client.get(
            reverse(
                "wagtailvideos:generate_url", args=(self.video.id, "bad-filter-spec")
            )
        )

        # Check response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response["Content-Type"], "application/json")

        # Check JSON
        self.assertJSONEqual(
            response.content.decode(),
            json.dumps(
                {
                    "error": "Invalid filter spec.",
                }
            ),
        )


class TestPreviewView(TestCase, WagtailTestUtils):
    def setUp(self):
        # Create an video for running tests on
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

        # Login
        self.user = self.login()

    def test_get(self):
        """
        Test a valid GET request to the view
        """
        # Get the video
        response = self.client.get(
            reverse("wagtailvideos:preview", args=(self.video.id, "fill-800x600"))
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "video/png")

    def test_get_invalid_filter_spec(self):
        """
        Test that an invalid filter spec returns a 400 response

        This is very unlikely to happen in reality. A user would have
        to create signature for the invalid filter spec which can't be
        done with Wagtails built in URL generator. We should test it
        anyway though.
        """
        # Get the video
        response = self.client.get(
            reverse("wagtailvideos:preview", args=(self.video.id, "bad-filter-spec"))
        )

        # Check response
        self.assertEqual(response.status_code, 400)


class TestEditOnlyPermissions(TestCase, WagtailTestUtils):
    def setUp(self):
        # Create an video to edit
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

        # Create a user with change_video permission but not add_video
        user = self.create_user(
            username="changeonly", email="changeonly@example.com", password="password"
        )
        change_permission = Permission.objects.get(
            content_type__app_label="wagtailvideos", codename="change_video"
        )
        admin_permission = Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )

        video_changers_group = Group.objects.create(name="Video changers")
        video_changers_group.permissions.add(admin_permission)
        GroupCollectionPermission.objects.create(
            group=video_changers_group,
            collection=Collection.get_first_root_node(),
            permission=change_permission,
        )

        user.groups.add(video_changers_group)
        self.login(username="changeonly", password="password")

    def test_get_index(self):
        response = self.client.get(reverse("wagtailvideos:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/index.html")

        # user should not get an "Add an video" button
        self.assertNotContains(response, "Add an video")

        # user should be able to see videos not owned by them
        self.assertContains(response, "Test video")

    def test_search(self):
        response = self.client.get(reverse("wagtailvideos:index"), {"q": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query_string"], "Hello")

    def test_get_add(self):
        response = self.client.get(reverse("wagtailvideos:add"))
        # permission should be denied
        self.assertRedirects(response, reverse("wagtailadmin_home"))

    def test_get_edit(self):
        response = self.client.get(reverse("wagtailvideos:edit", args=(self.video.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/edit.html")

    def test_get_delete(self):
        response = self.client.get(
            reverse("wagtailvideos:delete", args=(self.video.id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/confirm_delete.html")

    def test_get_add_multiple(self):
        response = self.client.get(reverse("wagtailvideos:add_multiple"))
        # permission should be denied
        self.assertRedirects(response, reverse("wagtailadmin_home"))


class TestVideoAddMultipleView(TestCase, WagtailTestUtils):
    def test_as_superuser(self):
        self.login()
        response = self.client.get(reverse("wagtailvideos:add_multiple"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/multiple/add.html")

    def test_as_ordinary_editor(self):
        user = self.create_user(username="editor", password="password")

        add_permission = Permission.objects.get(
            content_type__app_label="wagtailvideos", codename="add_video"
        )
        admin_permission = Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )
        video_adders_group = Group.objects.create(name="Video adders")
        video_adders_group.permissions.add(admin_permission)
        GroupCollectionPermission.objects.create(
            group=video_adders_group,
            collection=Collection.get_first_root_node(),
            permission=add_permission,
        )
        user.groups.add(video_adders_group)

        self.login(username="editor", password="password")

        response = self.client.get(reverse("wagtailvideos:add_multiple"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/multiple/add.html")
