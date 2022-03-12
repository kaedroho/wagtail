from io import BytesIO
from unittest.mock import patch

from django.test import TestCase, override_settings

from wagtail.core import hooks
from wagtail.videos import video_operations
from wagtail.videos.exceptions import InvalidFilterSpecError
from wagtail.videos.video_operations import TransformOperation
from wagtail.videos.models import Filter, Video
from wagtail.videos.tests.utils import (
    get_test_video_file,
    get_test_video_file_jpeg,
    get_test_video_file_webp,
)


class DummyVideoTransform:
    """
    This class pretends to be a VideoTransform but instead, it records
    the operations that have been performed on it
    """

    def __init__(self, size):
        self._check_size(size)
        self.size = size
        self.operations = []

    def clone(self):
        clone = DummyVideoTransform(self.size)
        clone.operations = self.operations.copy()
        return clone

    def resize(self, size):
        """
        Change the video size, stretching the transform to make it fit the new size.
        """
        self._check_size(size)
        clone = self.clone()
        clone.operations.append(("resize", size))
        clone.size = size
        return clone

    def crop(self, rect):
        """
        Crop the video to the specified rect.
        """
        self._check_size(tuple(rect.size))
        clone = self.clone()
        clone.operations.append(("crop", tuple(rect)))
        clone.size = tuple(rect.size)
        return clone

    @staticmethod
    def _check_size(size):
        if (
            not isinstance(size, tuple)
            or len(size) != 2
            or int(size[0]) != size[0]
            or int(size[1]) != size[1]
        ):
            raise TypeError("Video size must be a 2-tuple of integers")

        if size[0] < 1 or size[1] < 1:
            raise ValueError("Video width and height must both be 1 or greater")


class VideoTransformOperationTestCase(TestCase):
    operation_class = None
    filter_spec_tests = []
    filter_spec_error_tests = []
    run_tests = []
    norun_tests = []

    @classmethod
    def make_filter_spec_test(cls, filter_spec, expected_output):
        def test_filter_spec(self):
            operation = self.operation_class(*filter_spec.split("-"))

            # Check the attributes are set correctly
            for attr, value in expected_output.items():
                self.assertEqual(getattr(operation, attr), value)

        test_filter_spec.__name__ = str("test_filter_%s" % filter_spec)
        return test_filter_spec

    @classmethod
    def make_filter_spec_error_test(cls, filter_spec):
        def test_filter_spec_error(self):
            self.assertRaises(
                InvalidFilterSpecError, self.operation_class, *filter_spec.split("-")
            )

        test_filter_spec_error.__name__ = str(
            "test_filter_%s_raises_%s" % (filter_spec, InvalidFilterSpecError.__name__)
        )
        return test_filter_spec_error

    @classmethod
    def make_run_test(cls, filter_spec, video_kwargs, expected_output):
        def test_run(self):
            video = Video(**video_kwargs)

            # Make operation
            operation = self.operation_class(*filter_spec.split("-"))

            # Make context
            context = DummyVideoTransform((video.width, video.height))

            # Run
            context = operation.run(context, video)

            # Check
            self.assertEqual(context.operations, expected_output)

        test_run.__name__ = str("test_run_%s" % filter_spec)
        return test_run

    @classmethod
    def make_norun_test(cls, filter_spec, video_kwargs):
        def test_norun(self):
            video = Video(**video_kwargs)

            # Make operation
            operation = self.operation_class(*filter_spec.split("-"))

            # Make operation recorder
            context = DummyVideoTransform((video.width, video.height))

            # Attempt (and hopefully fail) to run
            with self.assertRaises(ValueError):
                operation.run(context, video)

        test_norun.__name__ = str("test_norun_%s" % filter_spec)
        return test_norun

    @classmethod
    def setup_test_methods(cls):
        if cls.operation_class is None:
            return

        # Filter spec tests
        for args in cls.filter_spec_tests:
            filter_spec_test = cls.make_filter_spec_test(*args)
            setattr(cls, filter_spec_test.__name__, filter_spec_test)

        # Filter spec error tests
        for filter_spec in cls.filter_spec_error_tests:
            filter_spec_error_test = cls.make_filter_spec_error_test(filter_spec)
            setattr(cls, filter_spec_error_test.__name__, filter_spec_error_test)

        # Running tests
        for args in cls.run_tests:
            run_test = cls.make_run_test(*args)
            setattr(cls, run_test.__name__, run_test)

        # Runtime error tests
        for args in cls.norun_tests:
            norun_test = cls.make_norun_test(*args)
            setattr(cls, norun_test.__name__, norun_test)


class TestFillOperation(VideoTransformOperationTestCase):
    operation_class = video_operations.FillOperation

    filter_spec_tests = [
        ("fill-800x600", {"width": 800, "height": 600, "crop_closeness": 0}),
        ("hello-800x600", {"width": 800, "height": 600, "crop_closeness": 0}),
        ("fill-800x600-c0", {"width": 800, "height": 600, "crop_closeness": 0}),
        ("fill-800x600-c100", {"width": 800, "height": 600, "crop_closeness": 1}),
        ("fill-800x600-c50", {"width": 800, "height": 600, "crop_closeness": 0.5}),
        ("fill-800x600-c1000", {"width": 800, "height": 600, "crop_closeness": 1}),
        ("fill-800000x100", {"width": 800000, "height": 100, "crop_closeness": 0}),
    ]

    filter_spec_error_tests = [
        "fill",
        "fill-800",
        "fill-abc",
        "fill-800xabc",
        "fill-800x600-",
        "fill-800x600x10",
        "fill-800x600-d100",
    ]

    run_tests = [
        # Basic usage
        (
            "fill-800x600",
            {"width": 1000, "height": 1000},
            [
                ("crop", (0, 125, 1000, 875)),
                ("resize", (800, 600)),
            ],
        ),
        # Basic usage with an oddly-sized original video
        # This checks for a rounding precision issue (#968)
        (
            "fill-200x200",
            {"width": 539, "height": 720},
            [
                ("crop", (0, 90, 539, 630)),
                ("resize", (200, 200)),
            ],
        ),
        # Closeness shouldn't have any effect when used without a focal point
        (
            "fill-800x600-c100",
            {"width": 1000, "height": 1000},
            [
                ("crop", (0, 125, 1000, 875)),
                ("resize", (800, 600)),
            ],
        ),
        # Should always crop towards focal point. Even if no closeness is set
        (
            "fill-80x60",
            {
                "width": 1000,
                "height": 1000,
                "focal_point_x": 1000,
                "focal_point_y": 500,
                "focal_point_width": 0,
                "focal_point_height": 0,
            },
            [
                # Crop the largest possible crop box towards the focal point
                ("crop", (0, 125, 1000, 875)),
                # Resize it down to final size
                ("resize", (80, 60)),
            ],
        ),
        # Should crop as close as possible without upscaling
        (
            "fill-80x60-c100",
            {
                "width": 1000,
                "height": 1000,
                "focal_point_x": 1000,
                "focal_point_y": 500,
                "focal_point_width": 0,
                "focal_point_height": 0,
            },
            [
                # Crop as close as possible to the focal point
                ("crop", (920, 470, 1000, 530)),
                # No need to resize, crop should've created an 80x60 video
            ],
        ),
        # Ditto with a wide video
        # Using a different filter so method name doesn't clash
        (
            "fill-100x60-c100",
            {
                "width": 2000,
                "height": 1000,
                "focal_point_x": 2000,
                "focal_point_y": 500,
                "focal_point_width": 0,
                "focal_point_height": 0,
            },
            [
                # Crop to the right hand side
                ("crop", (1900, 470, 2000, 530)),
            ],
        ),
        # Make sure that the crop box never enters the focal point
        (
            "fill-50x50-c100",
            {
                "width": 2000,
                "height": 1000,
                "focal_point_x": 1000,
                "focal_point_y": 500,
                "focal_point_width": 100,
                "focal_point_height": 20,
            },
            [
                # Crop a 100x100 box around the entire focal point
                ("crop", (950, 450, 1050, 550)),
                # Resize it down to 50x50
                ("resize", (50, 50)),
            ],
        ),
        # Test that the video is never upscaled
        (
            "fill-1000x800",
            {"width": 100, "height": 100},
            [
                ("crop", (0, 10, 100, 90)),
            ],
        ),
        # Test that the crop closeness gets capped to prevent upscaling
        (
            "fill-1000x800-c100",
            {
                "width": 1500,
                "height": 1000,
                "focal_point_x": 750,
                "focal_point_y": 500,
                "focal_point_width": 0,
                "focal_point_height": 0,
            },
            [
                # Crop a 1000x800 square out of the video as close to the
                # focal point as possible. Will not zoom too far in to
                # prevent upscaling
                ("crop", (250, 100, 1250, 900)),
            ],
        ),
        # Test for an issue where a ZeroDivisionError would occur when the
        # focal point size, video size and filter size match
        # See: #797
        (
            "fill-1500x1500-c100",
            {
                "width": 1500,
                "height": 1500,
                "focal_point_x": 750,
                "focal_point_y": 750,
                "focal_point_width": 1500,
                "focal_point_height": 1500,
            },
            [
                # This operation could probably be optimised out
                ("crop", (0, 0, 1500, 1500)),
            ],
        ),
        # A few tests for single pixel videos
        (
            "fill-100x100",
            {
                "width": 1,
                "height": 1,
            },
            [
                ("crop", (0, 0, 1, 1)),
            ],
        ),
        # This one once gave a ZeroDivisionError
        (
            "fill-100x150",
            {
                "width": 1,
                "height": 1,
            },
            [
                ("crop", (0, 0, 1, 1)),
            ],
        ),
        (
            "fill-150x100",
            {
                "width": 1,
                "height": 1,
            },
            [
                ("crop", (0, 0, 1, 1)),
            ],
        ),
    ]


TestFillOperation.setup_test_methods()


class TestMinMaxOperation(VideoTransformOperationTestCase):
    operation_class = video_operations.MinMaxOperation

    filter_spec_tests = [
        ("min-800x600", {"method": "min", "width": 800, "height": 600}),
        ("max-800x600", {"method": "max", "width": 800, "height": 600}),
    ]

    filter_spec_error_tests = [
        "min",
        "min-800",
        "min-abc",
        "min-800xabc",
        "min-800x600-",
        "min-800x600-c100",
        "min-800x600x10",
    ]

    run_tests = [
        # Basic usage of min
        (
            "min-800x600",
            {"width": 1000, "height": 1000},
            [
                ("resize", (800, 800)),
            ],
        ),
        # Basic usage of max
        (
            "max-800x600",
            {"width": 1000, "height": 1000},
            [
                ("resize", (600, 600)),
            ],
        ),
        # Resize doesn't try to set zero height
        (
            "max-400x400",
            {"width": 1000, "height": 1},
            [
                ("resize", (400, 1)),
            ],
        ),
        # Resize doesn't try to set zero width
        (
            "max-400x400",
            {"width": 1, "height": 1000},
            [
                ("resize", (1, 400)),
            ],
        ),
    ]


TestMinMaxOperation.setup_test_methods()


class TestWidthHeightOperation(VideoTransformOperationTestCase):
    operation_class = video_operations.WidthHeightOperation

    filter_spec_tests = [
        ("width-800", {"method": "width", "size": 800}),
        ("height-600", {"method": "height", "size": 600}),
    ]

    filter_spec_error_tests = [
        "width",
        "width-800x600",
        "width-abc",
        "width-800-c100",
    ]

    run_tests = [
        # Basic usage of width
        (
            "width-400",
            {"width": 1000, "height": 500},
            [
                ("resize", (400, 200)),
            ],
        ),
        # Basic usage of height
        (
            "height-400",
            {"width": 1000, "height": 500},
            [
                ("resize", (800, 400)),
            ],
        ),
        # Resize doesn't try to set zero height
        (
            "width-400",
            {"width": 1000, "height": 1},
            [
                ("resize", (400, 1)),
            ],
        ),
        # Resize doesn't try to set zero width
        (
            "height-400",
            {"width": 1, "height": 800},
            [
                ("resize", (1, 400)),
            ],
        ),
    ]


TestWidthHeightOperation.setup_test_methods()


class TestScaleOperation(VideoTransformOperationTestCase):
    operation_class = video_operations.ScaleOperation

    filter_spec_tests = [
        ("scale-100", {"method": "scale", "percent": 100}),
        ("scale-50", {"method": "scale", "percent": 50}),
    ]

    filter_spec_error_tests = [
        "scale",
        "scale-800x600",
        "scale-abc",
        "scale-800-c100",
    ]

    run_tests = [
        # Basic almost a no-op of scale
        (
            "scale-100",
            {"width": 1000, "height": 500},
            [
                ("resize", (1000, 500)),
            ],
        ),
        # Basic usage of scale
        (
            "scale-50",
            {"width": 1000, "height": 500},
            [
                ("resize", (500, 250)),
            ],
        ),
        # Rounded usage of scale
        (
            "scale-83.0322",
            {"width": 1000, "height": 500},
            [
                ("resize", (int(1000 * 0.830322), int(500 * 0.830322))),
            ],
        ),
        # Resize doesn't try to set zero height
        (
            "scale-50",
            {"width": 1000, "height": 1},
            [
                ("resize", (500, 1)),
            ],
        ),
        # Resize doesn't try to set zero width
        (
            "scale-50",
            {"width": 1, "height": 500},
            [
                ("resize", (1, 250)),
            ],
        ),
    ]


TestScaleOperation.setup_test_methods()


class TestCacheKey(TestCase):
    def test_cache_key(self):
        video = Video(width=1000, height=1000)
        fil = Filter(spec="max-100x100")
        cache_key = fil.get_cache_key(video)

        self.assertEqual(cache_key, "")

    def test_cache_key_fill_filter(self):
        video = Video(width=1000, height=1000)
        fil = Filter(spec="fill-100x100")
        cache_key = fil.get_cache_key(video)

        self.assertEqual(cache_key, "2e16d0ba")

    def test_cache_key_fill_filter_with_focal_point(self):
        video = Video(
            width=1000,
            height=1000,
            focal_point_width=100,
            focal_point_height=100,
            focal_point_x=500,
            focal_point_y=500,
        )
        fil = Filter(spec="fill-100x100")
        cache_key = fil.get_cache_key(video)

        self.assertEqual(cache_key, "0bbe3b2f")


class DummyOperation(TransformOperation):
    def construct(self):
        pass

    def run_mock(self, context, video):
        pass

    def run(self, context, video):
        self.run_mock(context, video)
        return context


def register_video_operations_hook():
    return [("operation1", DummyOperation), ("operation2", DummyOperation)]


class TestFilter(TestCase):
    @patch.object(DummyOperation, "run_mock")
    @hooks.register_temporarily(
        "register_video_operations", register_video_operations_hook
    )
    def test_runs_operations(self, run_mock):
        fil = Filter(spec="operation1|operation2")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )
        fil.run(video, BytesIO())

        self.assertEqual(run_mock.call_count, 2)


class TestFormatFilter(TestCase):
    def test_jpeg(self):
        fil = Filter(spec="width-400|format-jpeg")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )
        out = fil.run(video, BytesIO())

        self.assertEqual(out.format_name, "jpeg")

    def test_png(self):
        fil = Filter(spec="width-400|format-png")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )
        out = fil.run(video, BytesIO())

        self.assertEqual(out.format_name, "png")

    def test_gif(self):
        fil = Filter(spec="width-400|format-gif")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )
        out = fil.run(video, BytesIO())

        self.assertEqual(out.format_name, "gif")

    def test_webp(self):
        fil = Filter(spec="width-400|format-webp")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )
        out = fil.run(video, BytesIO())

        self.assertEqual(out.format_name, "webp")

    def test_webp_lossless(self):
        fil = Filter(spec="width-400|format-webp-lossless")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )

        f = BytesIO()
        with patch("PIL.Video.Video.save") as save:
            fil.run(video, f)

        # quality=80 is default for Williw and PIL libs
        save.assert_called_with(f, "WEBP", quality=80, lossless=True)

    def test_invalid(self):
        fil = Filter(spec="width-400|format-foo")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )
        self.assertRaises(InvalidFilterSpecError, fil.run, video, BytesIO())


class TestJPEGQualityFilter(TestCase):
    def test_default_quality(self):
        fil = Filter(spec="width-400")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_jpeg(),
        )

        f = BytesIO()
        with patch("PIL.Video.Video.save") as save:
            fil.run(video, f)

        save.assert_called_with(f, "JPEG", quality=85, optimize=True, progressive=True)

    def test_jpeg_quality_filter(self):
        fil = Filter(spec="width-400|jpegquality-40")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_jpeg(),
        )

        f = BytesIO()
        with patch("PIL.Video.Video.save") as save:
            fil.run(video, f)

        save.assert_called_with(f, "JPEG", quality=40, optimize=True, progressive=True)

    def test_jpeg_quality_filter_invalid(self):
        fil = Filter(spec="width-400|jpegquality-abc")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_jpeg(),
        )
        self.assertRaises(InvalidFilterSpecError, fil.run, video, BytesIO())

    def test_jpeg_quality_filter_no_value(self):
        fil = Filter(spec="width-400|jpegquality")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_jpeg(),
        )
        self.assertRaises(InvalidFilterSpecError, fil.run, video, BytesIO())

    def test_jpeg_quality_filter_too_big(self):
        fil = Filter(spec="width-400|jpegquality-101")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_jpeg(),
        )
        self.assertRaises(InvalidFilterSpecError, fil.run, video, BytesIO())

    @override_settings(WAGTAILIMAGES_JPEG_QUALITY=50)
    def test_jpeg_quality_setting(self):
        fil = Filter(spec="width-400")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_jpeg(),
        )

        f = BytesIO()
        with patch("PIL.Video.Video.save") as save:
            fil.run(video, f)

        save.assert_called_with(f, "JPEG", quality=50, optimize=True, progressive=True)

    @override_settings(WAGTAILIMAGES_JPEG_QUALITY=50)
    def test_jpeg_quality_filter_overrides_setting(self):
        fil = Filter(spec="width-400|jpegquality-40")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_jpeg(),
        )

        f = BytesIO()
        with patch("PIL.Video.Video.save") as save:
            fil.run(video, f)

        save.assert_called_with(f, "JPEG", quality=40, optimize=True, progressive=True)


class TestWebPQualityFilter(TestCase):
    def test_default_quality(self):
        fil = Filter(spec="width-400|format-webp")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_jpeg(),
        )

        f = BytesIO()
        with patch("PIL.Video.Video.save") as save:
            fil.run(video, f)

        save.assert_called_with(f, "WEBP", quality=85, lossless=False)

    def test_webp_quality_filter(self):
        fil = Filter(spec="width-400|webpquality-40|format-webp")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_jpeg(),
        )

        f = BytesIO()
        with patch("PIL.Video.Video.save") as save:
            fil.run(video, f)

        save.assert_called_with(f, "WEBP", quality=40, lossless=False)

    def test_webp_quality_filter_invalid(self):
        fil = Filter(spec="width-400|webpquality-abc|format-webp")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_jpeg(),
        )
        self.assertRaises(InvalidFilterSpecError, fil.run, video, BytesIO())

    def test_webp_quality_filter_no_value(self):
        fil = Filter(spec="width-400|webpquality")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_jpeg(),
        )
        self.assertRaises(InvalidFilterSpecError, fil.run, video, BytesIO())

    def test_webp_quality_filter_too_big(self):
        fil = Filter(spec="width-400|webpquality-101|format-webp")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_jpeg(),
        )
        self.assertRaises(InvalidFilterSpecError, fil.run, video, BytesIO())

    @override_settings(WAGTAILIMAGES_WEBP_QUALITY=50)
    def test_webp_quality_setting(self):
        fil = Filter(spec="width-400|format-webp")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_jpeg(),
        )

        f = BytesIO()
        with patch("PIL.Video.Video.save") as save:
            fil.run(video, f)

        save.assert_called_with(f, "WEBP", quality=50, lossless=False)

    @override_settings(WAGTAILIMAGES_WEBP_QUALITY=50)
    def test_jpeg_quality_filter_overrides_setting(self):
        fil = Filter(spec="width-400|webpquality-40|format-webp")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_jpeg(),
        )

        f = BytesIO()
        with patch("PIL.Video.Video.save") as save:
            fil.run(video, f)

        save.assert_called_with(f, "WEBP", quality=40, lossless=False)


class TestBackgroundColorFilter(TestCase):
    def test_original_has_alpha(self):
        # Checks that the test video we're using has alpha
        fil = Filter(spec="width-400")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )
        out = fil.run(video, BytesIO())

        self.assertTrue(out.has_alpha())

    def test_3_digit_hex(self):
        fil = Filter(spec="width-400|bgcolor-fff")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )
        out = fil.run(video, BytesIO())

        self.assertFalse(out.has_alpha())

    def test_6_digit_hex(self):
        fil = Filter(spec="width-400|bgcolor-ffffff")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )
        out = fil.run(video, BytesIO())

        self.assertFalse(out.has_alpha())

    def test_invalid(self):
        fil = Filter(spec="width-400|bgcolor-foo")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )
        self.assertRaises(ValueError, fil.run, video, BytesIO())

    def test_invalid_length(self):
        fil = Filter(spec="width-400|bgcolor-1234")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file(),
        )
        self.assertRaises(ValueError, fil.run, video, BytesIO())


class TestWebpFormatConversion(TestCase):
    def test_webp_convert_to_png(self):
        """by default, webp videos will be converted to png"""

        fil = Filter(spec="width-400")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_webp(),
        )
        out = fil.run(video, BytesIO())

        self.assertEqual(out.format_name, "png")

    @override_settings(WAGTAILIMAGES_FORMAT_CONVERSIONS={"webp": "webp"})
    def test_override_webp_convert_to_png(self):
        """WAGTAILIMAGES_FORMAT_CONVERSIONS can be overridden to disable webp conversion"""

        fil = Filter(spec="width-400")
        video = Video.objects.create(
            title="Test video",
            file=get_test_video_file_webp(),
        )
        out = fil.run(video, BytesIO())

        self.assertEqual(out.format_name, "webp")
