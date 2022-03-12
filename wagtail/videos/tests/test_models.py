import unittest

from django.contrib.auth.models import Group, Permission
from django.core.cache import caches
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from willow.video import Video as WillowVideo

from wagtail.core.models import Collection, GroupCollectionPermission, Page
from wagtail.videos.models import Rendition, SourceVideoIOError
from wagtail.videos.rect import Rect
from wagtail.tests.testapp.models import (
    EventPage,
    EventPageCarouselItem,
    ReimportedVideoModel,
)
from wagtail.tests.utils import WagtailTestUtils

from .utils import Video, get_test_video_file


class TestVideo(TestCase):
    def setUp(self):
        # Create an video for running tests on
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(colour="white"),
        )

    def test_get_video_model_at_import_time(self):
        self.assertEqual(ReimportedVideoModel, Video)

    def test_is_portrait(self):
        self.assertFalse(self.video.is_portrait())

    def test_is_landscape(self):
        self.assertTrue(self.video.is_landscape())

    def test_get_rect(self):
        self.assertTrue(self.video.get_rect(), Rect(0, 0, 640, 480))

    def test_get_focal_point(self):
        self.assertIsNone(self.video.get_focal_point())

        # Add a focal point to the video
        self.video.focal_point_x = 100
        self.video.focal_point_y = 200
        self.video.focal_point_width = 50
        self.video.focal_point_height = 20

        # Get it
        self.assertEqual(self.video.get_focal_point(), Rect(75, 190, 125, 210))

    def test_has_focal_point(self):
        self.assertFalse(self.video.has_focal_point())

        # Add a focal point to the video
        self.video.focal_point_x = 100
        self.video.focal_point_y = 200
        self.video.focal_point_width = 50
        self.video.focal_point_height = 20

        self.assertTrue(self.video.has_focal_point())

    def test_set_focal_point(self):
        self.assertIsNone(self.video.focal_point_x)
        self.assertIsNone(self.video.focal_point_y)
        self.assertIsNone(self.video.focal_point_width)
        self.assertIsNone(self.video.focal_point_height)

        self.video.set_focal_point(Rect(100, 150, 200, 350))

        self.assertEqual(self.video.focal_point_x, 150)
        self.assertEqual(self.video.focal_point_y, 250)
        self.assertEqual(self.video.focal_point_width, 100)
        self.assertEqual(self.video.focal_point_height, 200)

        self.video.set_focal_point(None)

        self.assertIsNone(self.video.focal_point_x)
        self.assertIsNone(self.video.focal_point_y)
        self.assertIsNone(self.video.focal_point_width)
        self.assertIsNone(self.video.focal_point_height)

    def test_is_stored_locally(self):
        self.assertTrue(self.video.is_stored_locally())

    @override_settings(
        DEFAULT_FILE_STORAGE="wagtail.tests.dummy_external_storage.DummyExternalStorage"
    )
    def test_is_stored_locally_with_external_storage(self):
        self.assertFalse(self.video.is_stored_locally())

    def test_get_file_size(self):
        file_size = self.video.get_file_size()
        self.assertIsInstance(file_size, int)
        self.assertGreater(file_size, 0)

    def test_get_file_size_on_missing_file_raises_sourcevideoioerror(self):
        self.video.file.delete(save=False)
        with self.assertRaises(SourceVideoIOError):
            self.video.get_file_size()


class TestVideoQuerySet(TestCase):
    def test_search_method(self):
        # Create an video for running tests on
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

        # Search for it
        results = Video.objects.search("Test")
        self.assertEqual(list(results), [video])

    def test_operators(self):
        aaa_video = Video.objects.create(
            title="AAA Test video",
            file=get_test_video_file(),
        )
        zzz_video = Video.objects.create(
            title="ZZZ Test video",
            file=get_test_video_file(),
        )

        results = Video.objects.search("aaa test", operator="and")
        self.assertEqual(list(results), [aaa_video])

        results = Video.objects.search("aaa test", operator="or")
        sorted_results = sorted(results, key=lambda img: img.title)
        self.assertEqual(sorted_results, [aaa_video, zzz_video])

    def test_custom_ordering(self):
        aaa_video = Video.objects.create(
            title="AAA Test video",
            file=get_test_video_file(),
        )
        zzz_video = Video.objects.create(
            title="ZZZ Test video",
            file=get_test_video_file(),
        )

        results = Video.objects.order_by("title").search("Test")
        self.assertEqual(list(results), [aaa_video, zzz_video])
        results = Video.objects.order_by("-title").search("Test")
        self.assertEqual(list(results), [zzz_video, aaa_video])

    def test_search_indexing_prefetches_tags(self):
        for i in range(0, 10):
            video = Video.objects.create(
                title="Test video %d" % i,
                file=get_test_video_file(),
            )
            video.tags.add("aardvark", "artichoke", "armadillo")

        with self.assertNumQueries(2):
            results = {
                video.title: [tag.name for tag in video.tags.all()]
                for video in Video.get_indexed_objects()
            }
            self.assertIn("aardvark", results["Test video 0"])


class TestVideoPermissions(TestCase, WagtailTestUtils):
    def setUp(self):
        # Create some user accounts for testing permissions
        self.user = self.create_user(
            username="user", email="user@email.com", password="password"
        )
        self.owner = self.create_user(
            username="owner", email="owner@email.com", password="password"
        )
        self.editor = self.create_user(
            username="editor", email="editor@email.com", password="password"
        )
        self.editor.groups.add(Group.objects.get(name="Editors"))
        self.administrator = self.create_superuser(
            username="administrator",
            email="administrator@email.com",
            password="password",
        )

        # Owner user must have the add_video permission
        video_adders_group = Group.objects.create(name="Video adders")
        GroupCollectionPermission.objects.create(
            group=video_adders_group,
            collection=Collection.get_first_root_node(),
            permission=Permission.objects.get(codename="add_video"),
        )
        self.owner.groups.add(video_adders_group)

        # Create an video for running tests on
        self.video = Video.objects.create(
            title="Test video",
            uploaded_by_user=self.owner,
            file=get_test_video_file(),
        )

    def test_administrator_can_edit(self):
        self.assertTrue(self.video.is_editable_by_user(self.administrator))

    def test_editor_can_edit(self):
        self.assertTrue(self.video.is_editable_by_user(self.editor))

    def test_owner_can_edit(self):
        self.assertTrue(self.video.is_editable_by_user(self.owner))

    def test_user_cant_edit(self):
        self.assertFalse(self.video.is_editable_by_user(self.user))


class TestRenditions(TestCase):
    def setUp(self):
        # Create an video for running tests on
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

    def test_get_rendition_model(self):
        self.assertIs(Video.get_rendition_model(), Rendition)

    def test_minification(self):
        rendition = self.video.get_rendition("width-400")

        # Check size
        self.assertEqual(rendition.width, 400)
        self.assertEqual(rendition.height, 300)

        # check that the rendition has been recorded under the correct filter,
        # via the Rendition.filter_spec attribute (in active use as of Wagtail 1.8)
        self.assertEqual(rendition.filter_spec, "width-400")

    def test_resize_to_max(self):
        rendition = self.video.get_rendition("max-100x100")

        # Check size
        self.assertEqual(rendition.width, 100)
        self.assertEqual(rendition.height, 75)

    def test_resize_to_min(self):
        rendition = self.video.get_rendition("min-120x120")

        # Check size
        self.assertEqual(rendition.width, 160)
        self.assertEqual(rendition.height, 120)

    def test_resize_to_original(self):
        rendition = self.video.get_rendition("original")

        # Check size
        self.assertEqual(rendition.width, 640)
        self.assertEqual(rendition.height, 480)

    def test_cache(self):
        # Get two renditions with the same filter
        first_rendition = self.video.get_rendition("width-400")
        second_rendition = self.video.get_rendition("width-400")

        # Check that they are the same object
        self.assertEqual(first_rendition, second_rendition)

    def test_alt_attribute(self):
        rendition = self.video.get_rendition("width-400")
        self.assertEqual(rendition.alt, "Test video")

    def test_full_url(self):
        ren_img = self.video.get_rendition("original")
        full_url = ren_img.full_url
        img_name = ren_img.file.name.split("/")[1]
        self.assertEqual(full_url, "http://testserver/media/videos/{}".format(img_name))

    @override_settings(
        CACHES={
            "renditions": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            },
        },
    )
    def test_renditions_cache_backend(self):
        cache = caches["renditions"]
        rendition = self.video.get_rendition("width-500")
        rendition_cache_key = "video-{}-{}-{}".format(
            rendition.video.id, rendition.focal_point_key, rendition.filter_spec
        )

        # Check rendition is saved to cache
        self.assertEqual(cache.get(rendition_cache_key), rendition)

        # Mark a rendition to check it comes from cache
        rendition._from_cache = "original"
        cache.set(rendition_cache_key, rendition)

        # Check if get_rendition returns the rendition from cache
        with self.assertNumQueries(0):
            new_rendition = self.video.get_rendition("width-500")
        self.assertEqual(new_rendition._from_cache, "original")

        # changing the video file should invalidate the cache
        self.video.file = get_test_video_file(colour="green")
        self.video.save()
        # deleting renditions would normally happen within the 'edit' view on file change -
        # we're bypassing that here, so have to do it manually
        self.video.renditions.all().delete()
        new_rendition = self.video.get_rendition("width-500")
        self.assertFalse(hasattr(new_rendition, "_from_cache"))

        # changing it back should also generate a new rendition and not re-use
        # the original one (because that file has now been deleted in the change)
        self.video.file = get_test_video_file(colour="white")
        self.video.save()
        self.video.renditions.all().delete()
        new_rendition = self.video.get_rendition("width-500")
        self.assertFalse(hasattr(new_rendition, "_from_cache"))

    def test_focal_point(self):
        self.video.focal_point_x = 100
        self.video.focal_point_y = 200
        self.video.focal_point_width = 50
        self.video.focal_point_height = 20
        self.video.save()

        # Generate a rendition that's half the size of the original
        rendition = self.video.get_rendition("width-320")

        self.assertEqual(rendition.focal_point.round(), Rect(37, 95, 63, 105))
        self.assertEqual(rendition.focal_point.centroid.x, 50)
        self.assertEqual(rendition.focal_point.centroid.y, 100)
        self.assertEqual(rendition.focal_point.width, 25)
        self.assertEqual(rendition.focal_point.height, 10)

        self.assertEqual(
            rendition.background_position_style, "background-position: 15% 41%;"
        )

    def test_background_position_style_default(self):
        # Generate a rendition that's half the size of the original
        rendition = self.video.get_rendition("width-320")

        self.assertEqual(
            rendition.background_position_style, "background-position: 50% 50%;"
        )


class TestUsageCount(TestCase):
    fixtures = ["test.json"]

    def setUp(self):
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_unused_video_usage_count(self):
        self.assertEqual(self.video.get_usage().count(), 0)

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_used_video_document_usage_count(self):
        page = EventPage.objects.get(id=4)
        event_page_carousel_item = EventPageCarouselItem()
        event_page_carousel_item.page = page
        event_page_carousel_item.video = self.video
        event_page_carousel_item.save()
        self.assertEqual(self.video.get_usage().count(), 1)


class TestGetUsage(TestCase):
    fixtures = ["test.json"]

    def setUp(self):
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

    def test_video_get_usage_not_enabled(self):
        self.assertEqual(list(self.video.get_usage()), [])

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_unused_video_get_usage(self):
        self.assertEqual(list(self.video.get_usage()), [])

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_used_video_document_get_usage(self):
        page = EventPage.objects.get(id=4)
        event_page_carousel_item = EventPageCarouselItem()
        event_page_carousel_item.page = page
        event_page_carousel_item.video = self.video
        event_page_carousel_item.save()
        self.assertTrue(issubclass(Page, type(self.video.get_usage()[0])))


class TestGetWillowVideo(TestCase):
    fixtures = ["test.json"]

    def setUp(self):
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

    def test_willow_video_object_returned(self):
        with self.video.get_willow_video() as willow_video:
            self.assertIsInstance(willow_video, WillowVideo)

    def test_with_missing_video(self):
        # Video id=1 in test fixtures has a missing video file
        bad_video = Video.objects.get(id=1)

        # Attempting to get the Willow video for videos without files
        # should raise a SourceVideoIOError
        with self.assertRaises(SourceVideoIOError):
            with bad_video.get_willow_video():
                self.fail()  # Shouldn't get here

    def test_closes_video(self):
        # This tests that willow closes videos after use
        with self.video.get_willow_video():
            self.assertFalse(self.video.file.closed)

        self.assertTrue(self.video.file.closed)

    def test_closes_video_on_exception(self):
        # This tests that willow closes videos when the with is exited with an exception
        try:
            with self.video.get_willow_video():
                self.assertFalse(self.video.file.closed)
                raise ValueError("Something went wrong!")
        except ValueError:
            pass

        self.assertTrue(self.video.file.closed)

    def test_doesnt_close_open_video(self):
        # This tests that when the video file is already open, get_willow_video doesn't close it (#1256)
        self.video.file.open("rb")

        with self.video.get_willow_video():
            pass

        self.assertFalse(self.video.file.closed)

        self.video.file.close()


class TestIssue573(TestCase):
    """
    This tests for a bug which causes filename limit on Renditions to be reached
    when the Video has a long original filename and a big focal point key
    """

    def test_issue_573(self):
        # Create an video with a big filename and focal point
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(
                "thisisaverylongfilename-abcdefghijklmnopqrstuvwxyz-supercalifragilisticexpialidocious.png"
            ),
            focal_point_x=1000,
            focal_point_y=1000,
            focal_point_width=1000,
            focal_point_height=1000,
        )

        # Try creating a rendition from that video
        # This would crash if the bug is present
        video.get_rendition("fill-800x600")


@override_settings(_WAGTAILSEARCH_FORCE_AUTO_UPDATE=["elasticsearch"])
class TestIssue613(TestCase, WagtailTestUtils):
    def get_elasticsearch_backend(self):
        from django.conf import settings

        from wagtail.search.backends import get_search_backend

        if "elasticsearch" not in settings.WAGTAILSEARCH_BACKENDS:
            raise unittest.SkipTest("No elasticsearch backend active")

        return get_search_backend("elasticsearch")

    def setUp(self):
        self.search_backend = self.get_elasticsearch_backend()
        self.login()

    def add_video(self, **params):
        post_data = {
            "title": "Test video",
            "file": SimpleUploadedFile(
                "test.png", get_test_video_file().file.getvalue()
            ),
        }
        post_data.update(params)
        response = self.client.post(reverse("wagtailvideos:add"), post_data)

        # Should redirect back to index
        self.assertRedirects(response, reverse("wagtailvideos:index"))

        # Check that the video was created
        videos = Video.objects.filter(title="Test video")
        self.assertEqual(videos.count(), 1)

        # Test that size was populated correctly
        video = videos.first()
        self.assertEqual(video.width, 640)
        self.assertEqual(video.height, 480)

        return video

    def edit_video(self, **params):
        # Create an video to edit
        self.video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

        # Edit it
        post_data = {
            "title": "Edited",
        }
        post_data.update(params)
        response = self.client.post(
            reverse("wagtailvideos:edit", args=(self.video.id,)), post_data
        )

        # Should redirect back to index
        self.assertRedirects(response, reverse("wagtailvideos:index"))

        # Check that the video was edited
        video = Video.objects.get(id=self.video.id)
        self.assertEqual(video.title, "Edited")
        return video

    def test_issue_613_on_add(self):
        # Reset the search index
        self.search_backend.reset_index()
        self.search_backend.add_type(Video)

        # Add an video with some tags
        video = self.add_video(tags="hello")
        self.search_backend.refresh_index()

        # Search for it by tag
        results = self.search_backend.search("hello", Video)

        # Check
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, video.id)

    def test_issue_613_on_edit(self):
        # Reset the search index
        self.search_backend.reset_index()
        self.search_backend.add_type(Video)

        # Add an video with some tags
        video = self.edit_video(tags="hello")
        self.search_backend.refresh_index()

        # Search for it by tag
        results = self.search_backend.search("hello", Video)

        # Check
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, video.id)


class TestIssue312(TestCase):
    def test_duplicate_renditions(self):
        # Create an video
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

        # Get two renditions and check that they're the same
        rend1 = video.get_rendition("fill-100x100")
        rend2 = video.get_rendition("fill-100x100")
        self.assertEqual(rend1, rend2)

        # Now manually duplicate the renditon and check that the database blocks it
        self.assertRaises(
            IntegrityError,
            Rendition.objects.create,
            video=rend1.video,
            filter_spec=rend1.filter_spec,
            width=rend1.width,
            height=rend1.height,
            focal_point_key=rend1.focal_point_key,
        )


class TestFilenameReduction(TestCase):
    """
    This tests for a bug which results in filenames without extensions
    causing an infinite loop
    """

    def test_filename_reduction_no_ext(self):
        # Create an video with a big filename and no extension
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(
                "thisisaverylongfilename-abcdefghijklmnopqrstuvwxyz-supercalifragilisticexpialidocioussuperlong"
            ),
        )

        # Saving file will result in infinite loop when bug is present
        video.save()
        self.assertEqual(
            "original_videos/thisisaverylongfilename-abcdefghijklmnopqrstuvwxyz-supercalifragilisticexpiali",
            video.file.name,
        )

    # Test for happy path. Long filename with extension
    def test_filename_reduction_ext(self):
        # Create an video with a big filename and extensions
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(
                "thisisaverylongfilename-abcdefghijklmnopqrstuvwxyz-supercalifragilisticexpialidocioussuperlong.png"
            ),
        )

        video.save()
        self.assertEqual(
            "original_videos/thisisaverylongfilename-abcdefghijklmnopqrstuvwxyz-supercalifragilisticexp.png",
            video.file.name,
        )


class TestRenditionOrientation(TestCase):
    """
    This tests for a bug where videos with exif orientations which
    required rotation for display were cropped and sized based on the
    unrotated video dimensions.

    For example videos with specified dimensions of 640x450 but an exif orientation of 6
    should appear as a 450x640 portrait, but instead were still cropped to 640x450.

    Actual video files are used so that exif orientation data will exist for the rotation to function correctly.
    """

    def assert_orientation_landscape_video_is_correct(self, rendition):
        """
        Check that the video has the correct colored pixels in the right places
        so that we know the video did not physically rotate.
        """

        from willow.plugins.pillow import PillowVideo

        with rendition.get_willow_video() as willow_video:
            video = PillowVideo.open(willow_video)
        # Check that the video is the correct size (and not rotated)
        self.assertEqual(video.get_size(), (600, 450))
        # Check that the red flower is in the bottom left
        # The JPEGs have compressed slightly differently so the colours won't be spot on
        colour = video.video.convert("RGB").getpixel((155, 282))
        self.assertAlmostEqual(colour[0], 217, delta=25)
        self.assertAlmostEqual(colour[1], 38, delta=25)
        self.assertAlmostEqual(colour[2], 46, delta=25)

        # Check that the water is at the bottom
        colour = video.video.convert("RGB").getpixel((377, 434))
        self.assertAlmostEqual(colour[0], 85, delta=25)
        self.assertAlmostEqual(colour[1], 93, delta=25)
        self.assertAlmostEqual(colour[2], 65, delta=25)

    def test_jpeg_with_orientation_1(self):
        with open("wagtail/videos/tests/video_files/landscape_1.jpg", "rb") as f:
            video = Video.objects.create(title="Test video", file=File(f))

        # check preconditions
        self.assertEqual(video.width, 600)
        self.assertEqual(video.height, 450)
        rendition = video.get_rendition("original")
        # Check dimensions stored on the model
        self.assertEqual(rendition.width, 600)
        self.assertEqual(rendition.height, 450)
        # Check actual video dimensions and orientation
        self.assert_orientation_landscape_video_is_correct(rendition)

    def test_jpeg_with_orientation_2(self):
        with open("wagtail/videos/tests/video_files/landscape_2.jpg", "rb") as f:
            video = Video.objects.create(title="Test video", file=File(f))

        # check preconditions
        self.assertEqual(video.width, 600)
        self.assertEqual(video.height, 450)
        rendition = video.get_rendition("original")
        # Check dimensions stored on the model
        self.assertEqual(rendition.width, 600)
        self.assertEqual(rendition.height, 450)
        # Check actual video dimensions and orientation
        self.assert_orientation_landscape_video_is_correct(rendition)

    def test_jpeg_with_orientation_3(self):
        with open("wagtail/videos/tests/video_files/landscape_3.jpg", "rb") as f:
            video = Video.objects.create(title="Test video", file=File(f))

        # check preconditions
        self.assertEqual(video.width, 600)
        self.assertEqual(video.height, 450)
        rendition = video.get_rendition("original")
        # Check dimensions stored on the model
        self.assertEqual(rendition.width, 600)
        self.assertEqual(rendition.height, 450)
        # Check actual video dimensions and orientation
        self.assert_orientation_landscape_video_is_correct(rendition)

    def test_jpeg_with_orientation_4(self):
        with open("wagtail/videos/tests/video_files/landscape_4.jpg", "rb") as f:
            video = Video.objects.create(title="Test video", file=File(f))

        # check preconditions
        self.assertEqual(video.width, 600)
        self.assertEqual(video.height, 450)
        rendition = video.get_rendition("original")
        # Check dimensions stored on the model
        self.assertEqual(rendition.width, 600)
        self.assertEqual(rendition.height, 450)
        # Check actual video dimensions and orientation
        self.assert_orientation_landscape_video_is_correct(rendition)

    # tests below here have a specified width x height in portrait but
    # an orientation specified of landscape, so the original shows a height > width
    # but the rendition is corrected to height < width.
    def test_jpeg_with_orientation_5(self):
        with open("wagtail/videos/tests/video_files/landscape_6.jpg", "rb") as f:
            video = Video.objects.create(title="Test video", file=File(f))

        # check preconditions
        self.assertEqual(video.width, 450)
        self.assertEqual(video.height, 600)
        rendition = video.get_rendition("original")
        # Check dimensions stored on the model
        self.assertEqual(rendition.width, 600)
        self.assertEqual(rendition.height, 450)
        # Check actual video dimensions and orientation
        self.assert_orientation_landscape_video_is_correct(rendition)

    def test_jpeg_with_orientation_6(self):
        with open("wagtail/videos/tests/video_files/landscape_6.jpg", "rb") as f:
            video = Video.objects.create(title="Test video", file=File(f))

        # check preconditions
        self.assertEqual(video.width, 450)
        self.assertEqual(video.height, 600)
        rendition = video.get_rendition("original")
        # Check dimensions stored on the model
        self.assertEqual(rendition.width, 600)
        self.assertEqual(rendition.height, 450)
        # Check actual video dimensions and orientation
        self.assert_orientation_landscape_video_is_correct(rendition)

    def test_jpeg_with_orientation_7(self):
        with open("wagtail/videos/tests/video_files/landscape_7.jpg", "rb") as f:
            video = Video.objects.create(title="Test video", file=File(f))

        # check preconditions
        self.assertEqual(video.width, 450)
        self.assertEqual(video.height, 600)
        rendition = video.get_rendition("original")
        # Check dimensions stored on the model
        self.assertEqual(rendition.width, 600)
        self.assertEqual(rendition.height, 450)
        # Check actual video dimensions and orientation
        self.assert_orientation_landscape_video_is_correct(rendition)

    def test_jpeg_with_orientation_8(self):
        with open("wagtail/videos/tests/video_files/landscape_8.jpg", "rb") as f:
            video = Video.objects.create(title="Test video", file=File(f))

        # check preconditions
        self.assertEqual(video.width, 450)
        self.assertEqual(video.height, 600)
        rendition = video.get_rendition("original")
        # Check dimensions stored on the model
        self.assertEqual(rendition.width, 600)
        self.assertEqual(rendition.height, 450)
        # Check actual video dimensions and orientation
        self.assert_orientation_landscape_video_is_correct(rendition)
