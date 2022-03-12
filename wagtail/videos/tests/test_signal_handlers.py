from django.db import transaction
from django.test import TransactionTestCase, override_settings

from wagtail.core.models import Collection
from wagtail.videos import get_video_model, signal_handlers
from wagtail.videos.tests.utils import get_test_video_file


class TestFilesDeletedForDefaultModels(TransactionTestCase):
    """
    Because we expect file deletion to only happen once a transaction is
    successfully committed, we must run these tests using TransactionTestCase
    per the following documentation:

        Django's TestCase class wraps each test in a transaction and rolls back that
        transaction after each test, in order to provide test isolation. This means
        that no transaction is ever actually committed, thus your on_commit()
        callbacks will never be run. If you need to test the results of an
        on_commit() callback, use a TransactionTestCase instead.
        https://docs.djangoproject.com/en/1.10/topics/db/transactions/#use-in-tests
    """

    def setUp(self):
        # Required to create root collection because the TransactionTestCase
        # does not make initial data loaded in migrations available and
        # serialized_rollback=True causes other problems in the test suite.
        # ref: https://docs.djangoproject.com/en/1.10/topics/testing/overview/#rollback-emulation
        Collection.objects.get_or_create(
            name="Root",
            path="0001",
            depth=1,
            numchild=0,
        )

    def test_video_file_deleted_oncommit(self):
        with transaction.atomic():
            video = get_video_model().objects.create(
                title="Test Video", file=get_test_video_file()
            )
            filename = video.file.name
            self.assertTrue(video.file.storage.exists(filename))
            video.delete()
            self.assertTrue(video.file.storage.exists(filename))
        self.assertFalse(video.file.storage.exists(filename))

    def test_rendition_file_deleted_oncommit(self):
        with transaction.atomic():
            video = get_video_model().objects.create(
                title="Test Video", file=get_test_video_file()
            )
            rendition = video.get_rendition("original")
            filename = rendition.file.name
            self.assertTrue(rendition.file.storage.exists(filename))
            rendition.delete()
            self.assertTrue(rendition.file.storage.exists(filename))
        self.assertFalse(rendition.file.storage.exists(filename))


@override_settings(WAGTAILIMAGES_IMAGE_MODEL="tests.CustomVideo")
class TestFilesDeletedForCustomModels(TestFilesDeletedForDefaultModels):
    def setUp(self):
        # Required to create root collection because the TransactionTestCase
        # does not make initial data loaded in migrations available and
        # serialized_rollback=True causes other problems in the test suite.
        # ref: https://docs.djangoproject.com/en/1.10/topics/testing/overview/#rollback-emulation
        Collection.objects.get_or_create(
            name="Root",
            path="0001",
            depth=1,
            numchild=0,
        )

        #: Sadly signal receivers only get connected when starting django.
        #: We will re-attach them here to mimic the django startup behavior
        #: and get the signals connected to our custom model..
        signal_handlers.register_signal_handlers()

    def test_video_model(self):
        cls = get_video_model()
        self.assertEqual(
            "%s.%s" % (cls._meta.app_label, cls.__name__), "tests.CustomVideo"
        )
