import hashlib
import logging
import os.path
import time
from collections import OrderedDict
from contextlib import contextmanager
from io import BytesIO

from django.conf import settings
from django.core import checks
from django.core.cache import InvalidCacheBackendError, caches
from django.core.files import File
from django.db import models
from django.forms.utils import flatatt
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from willow.video import Video as WillowVideo

from wagtail.admin.models import get_object_usage
from wagtail.core import hooks
from wagtail.core.models import CollectionMember
from wagtail.core.utils import string_to_ascii
from wagtail.videos.exceptions import InvalidFilterSpecError
from wagtail.videos.video_operations import (
    FilterOperation,
    VideoTransform,
    TransformOperation,
)
from wagtail.videos.rect import Rect
from wagtail.search import index
from wagtail.search.queryset import SearchableQuerySetMixin

logger = logging.getLogger("wagtail.videos")


class SourceVideoIOError(IOError):
    """
    Custom exception to distinguish IOErrors that were thrown while opening the source video
    """

    pass


class VideoQuerySet(SearchableQuerySetMixin, models.QuerySet):
    pass


def get_upload_to(instance, filename):
    """
    Obtain a valid upload path for an video file.

    This needs to be a module-level function so that it can be referenced within migrations,
    but simply delegates to the `get_upload_to` method of the instance, so that AbstractVideo
    subclasses can override it.
    """
    return instance.get_upload_to(filename)


def get_rendition_upload_to(instance, filename):
    """
    Obtain a valid upload path for an video rendition file.

    This needs to be a module-level function so that it can be referenced within migrations,
    but simply delegates to the `get_upload_to` method of the instance, so that AbstractRendition
    subclasses can override it.
    """
    return instance.get_upload_to(filename)


class VideoFileMixin:
    def is_stored_locally(self):
        """
        Returns True if the video is hosted on the local filesystem
        """
        try:
            self.file.path

            return True
        except NotImplementedError:
            return False

    def get_file_size(self):
        if self.file_size is None:
            try:
                self.file_size = self.file.size
            except Exception as e:
                # File not found
                #
                # Have to catch everything, because the exception
                # depends on the file subclass, and therefore the
                # storage being used.
                raise SourceVideoIOError(str(e))

            self.save(update_fields=["file_size"])

        return self.file_size

    @contextmanager
    def open_file(self):
        # Open file if it is closed
        close_file = False
        try:
            video_file = self.file

            if self.file.closed:
                # Reopen the file
                if self.is_stored_locally():
                    self.file.open("rb")
                else:
                    # Some external storage backends don't allow reopening
                    # the file. Get a fresh file instance. #1397
                    storage = self._meta.get_field("file").storage
                    video_file = storage.open(self.file.name, "rb")

                close_file = True
        except IOError as e:
            # re-throw this as a SourceVideoIOError so that calling code can distinguish
            # these from IOErrors elsewhere in the process
            raise SourceVideoIOError(str(e))

        # Seek to beginning
        video_file.seek(0)

        try:
            yield video_file
        finally:
            if close_file:
                video_file.close()

    @contextmanager
    def get_willow_video(self):
        with self.open_file() as video_file:
            yield WillowVideo.open(video_file)


class AbstractVideo(VideoFileMixin, CollectionMember, index.Indexed, models.Model):
    title = models.CharField(max_length=255, verbose_name=_("title"))
    file = models.VideoField(
        verbose_name=_("file"),
        upload_to=get_upload_to,
        width_field="width",
        height_field="height",
    )
    width = models.IntegerField(verbose_name=_("width"), editable=False)
    height = models.IntegerField(verbose_name=_("height"), editable=False)
    created_at = models.DateTimeField(
        verbose_name=_("created at"), auto_now_add=True, db_index=True
    )
    uploaded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("uploaded by user"),
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
    )

    tags = TaggableManager(help_text=None, blank=True, verbose_name=_("tags"))

    focal_point_x = models.PositiveIntegerField(null=True, blank=True)
    focal_point_y = models.PositiveIntegerField(null=True, blank=True)
    focal_point_width = models.PositiveIntegerField(null=True, blank=True)
    focal_point_height = models.PositiveIntegerField(null=True, blank=True)

    file_size = models.PositiveIntegerField(null=True, editable=False)
    # A SHA-1 hash of the file contents
    file_hash = models.CharField(max_length=40, blank=True, editable=False)

    objects = VideoQuerySet.as_manager()

    def _set_file_hash(self, file_contents):
        self.file_hash = hashlib.sha1(file_contents).hexdigest()

    def get_file_hash(self):
        if self.file_hash == "":
            with self.open_file() as f:
                self._set_file_hash(f.read())

            self.save(update_fields=["file_hash"])

        return self.file_hash

    def get_upload_to(self, filename):
        folder_name = "original_videos"
        filename = self.file.field.storage.get_valid_name(filename)

        # do a unidecode in the filename and then
        # replace non-ascii characters in filename with _ , to sidestep issues with filesystem encoding
        filename = "".join(
            (i if ord(i) < 128 else "_") for i in string_to_ascii(filename)
        )

        # Truncate filename so it fits in the 100 character limit
        # https://code.djangoproject.com/ticket/9893
        full_path = os.path.join(folder_name, filename)
        if len(full_path) >= 95:
            chars_to_trim = len(full_path) - 94
            prefix, extension = os.path.splitext(filename)
            filename = prefix[:-chars_to_trim] + extension
            full_path = os.path.join(folder_name, filename)

        return full_path

    def get_usage(self):
        return get_object_usage(self)

    @property
    def usage_url(self):
        return reverse("wagtailvideos:video_usage", args=(self.id,))

    search_fields = CollectionMember.search_fields + [
        index.SearchField("title", partial_match=True, boost=10),
        index.AutocompleteField("title"),
        index.FilterField("title"),
        index.RelatedFields(
            "tags",
            [
                index.SearchField("name", partial_match=True, boost=10),
                index.AutocompleteField("name"),
            ],
        ),
        index.FilterField("uploaded_by_user"),
    ]

    def __str__(self):
        return self.title

    def get_rect(self):
        return Rect(0, 0, self.width, self.height)

    def get_focal_point(self):
        if (
            self.focal_point_x is not None
            and self.focal_point_y is not None
            and self.focal_point_width is not None
            and self.focal_point_height is not None
        ):
            return Rect.from_point(
                self.focal_point_x,
                self.focal_point_y,
                self.focal_point_width,
                self.focal_point_height,
            )

    def has_focal_point(self):
        return self.get_focal_point() is not None

    def set_focal_point(self, rect):
        if rect is not None:
            self.focal_point_x = rect.centroid_x
            self.focal_point_y = rect.centroid_y
            self.focal_point_width = rect.width
            self.focal_point_height = rect.height
        else:
            self.focal_point_x = None
            self.focal_point_y = None
            self.focal_point_width = None
            self.focal_point_height = None

    def get_suggested_focal_point(self):
        with self.get_willow_video() as willow:
            faces = willow.detect_faces()

            if faces:
                # Create a bounding box around all faces
                left = min(face[0] for face in faces)
                top = min(face[1] for face in faces)
                right = max(face[2] for face in faces)
                bottom = max(face[3] for face in faces)
                focal_point = Rect(left, top, right, bottom)
            else:
                features = willow.detect_features()
                if features:
                    # Create a bounding box around all features
                    left = min(feature[0] for feature in features)
                    top = min(feature[1] for feature in features)
                    right = max(feature[0] for feature in features)
                    bottom = max(feature[1] for feature in features)
                    focal_point = Rect(left, top, right, bottom)
                else:
                    return None

        # Add 20% to width and height and give it a minimum size
        x, y = focal_point.centroid
        width, height = focal_point.size

        width *= 1.20
        height *= 1.20

        width = max(width, 100)
        height = max(height, 100)

        return Rect.from_point(x, y, width, height)

    @classmethod
    def get_rendition_model(cls):
        """Get the Rendition model for this Video model"""
        return cls.renditions.rel.related_model

    def get_rendition(self, filter):
        if isinstance(filter, str):
            filter = Filter(spec=filter)

        cache_key = filter.get_cache_key(self)
        Rendition = self.get_rendition_model()

        try:
            rendition_caching = True
            cache = caches["renditions"]
            rendition_cache_key = Rendition.construct_cache_key(
                self.id, cache_key, filter.spec
            )
            cached_rendition = cache.get(rendition_cache_key)
            if cached_rendition:
                return cached_rendition
        except InvalidCacheBackendError:
            rendition_caching = False

        try:
            rendition = self.renditions.get(
                filter_spec=filter.spec,
                focal_point_key=cache_key,
            )
        except Rendition.DoesNotExist:
            # Generate the rendition video
            try:
                logger.debug(
                    "Generating '%s' rendition for video %d",
                    filter.spec,
                    self.pk,
                )

                start_time = time.time()
                generated_video = filter.run(self, BytesIO())

                logger.debug(
                    "Generated '%s' rendition for video %d in %.1fms",
                    filter.spec,
                    self.pk,
                    (time.time() - start_time) * 1000,
                )
            except:  # noqa:B901,E722
                logger.debug(
                    "Failed to generate '%s' rendition for video %d",
                    filter.spec,
                    self.pk,
                )
                raise

            # Generate filename
            input_filename = os.path.basename(self.file.name)
            input_filename_without_extension, input_extension = os.path.splitext(
                input_filename
            )

            # A mapping of video formats to extensions
            FORMAT_EXTENSIONS = {
                "jpeg": ".jpg",
                "png": ".png",
                "gif": ".gif",
                "webp": ".webp",
            }

            output_extension = (
                filter.spec.replace("|", ".")
                + FORMAT_EXTENSIONS[generated_video.format_name]
            )
            if cache_key:
                output_extension = cache_key + "." + output_extension

            # Truncate filename to prevent it going over 60 chars
            output_filename_without_extension = input_filename_without_extension[
                : (59 - len(output_extension))
            ]
            output_filename = output_filename_without_extension + "." + output_extension

            rendition, created = self.renditions.get_or_create(
                filter_spec=filter.spec,
                focal_point_key=cache_key,
                defaults={"file": File(generated_video.f, name=output_filename)},
            )

        if rendition_caching:
            cache.set(rendition_cache_key, rendition)

        return rendition

    def is_portrait(self):
        return self.width < self.height

    def is_landscape(self):
        return self.height < self.width

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def default_alt_text(self):
        # by default the alt text field (used in rich text insertion) is populated
        # from the title. Subclasses might provide a separate alt field, and
        # override this
        return self.title

    def is_editable_by_user(self, user):
        from wagtail.videos.permissions import permission_policy

        return permission_policy.user_has_permission_for_instance(user, "change", self)

    class Meta:
        abstract = True


class Video(AbstractVideo):
    admin_form_fields = (
        "title",
        "file",
        "collection",
        "tags",
        "focal_point_x",
        "focal_point_y",
        "focal_point_width",
        "focal_point_height",
    )

    class Meta(AbstractVideo.Meta):
        verbose_name = _("video")
        verbose_name_plural = _("videos")
        permissions = [
            ("choose_video", "Can choose video"),
        ]


class Filter:
    """
    Represents one or more operations that can be applied to an Video to produce a rendition
    appropriate for final display on the website. Usually this would be a resize operation,
    but could potentially involve colour processing, etc.
    """

    def __init__(self, spec=None):
        # The spec pattern is operation1-var1-var2|operation2-var1
        self.spec = spec

    @cached_property
    def operations(self):
        # Search for operations
        registered_operations = {}
        for fn in hooks.get_hooks("register_video_operations"):
            registered_operations.update(dict(fn()))

        # Build list of operation objects
        operations = []
        for op_spec in self.spec.split("|"):
            op_spec_parts = op_spec.split("-")

            if op_spec_parts[0] not in registered_operations:
                raise InvalidFilterSpecError(
                    "Unrecognised operation: %s" % op_spec_parts[0]
                )

            op_class = registered_operations[op_spec_parts[0]]
            operations.append(op_class(*op_spec_parts))
        return operations

    @property
    def transform_operations(self):
        return [
            operation
            for operation in self.operations
            if isinstance(operation, TransformOperation)
        ]

    @property
    def filter_operations(self):
        return [
            operation
            for operation in self.operations
            if isinstance(operation, FilterOperation)
        ]

    def get_transform(self, video, size=None):
        """
        Returns an VideoTransform with all the transforms in this filter applied.

        The VideoTransform is an object with two attributes:
         - .size - The size of the final video
         - .matrix - An affine transformation matrix that combines any
           transform/scale/rotation operations that need to be applied to the video
        """

        if not size:
            size = (video.width, video.height)

        transform = VideoTransform(size)
        for operation in self.transform_operations:
            transform = operation.run(transform, video)
        return transform

    def run(self, video, output):
        with video.get_willow_video() as willow:
            original_format = willow.format_name

            # Fix orientation of video
            willow = willow.auto_orient()

            # Transform the video
            transform = self.get_transform(
                video, (willow.video.width, willow.video.height)
            )
            willow = willow.crop(transform.get_rect().round())
            willow = willow.resize(transform.size)

            # Apply filters
            env = {
                "original-format": original_format,
            }
            for operation in self.filter_operations:
                willow = operation.run(willow, video, env) or willow

            # Find the output format to use
            if "output-format" in env:
                # Developer specified an output format
                output_format = env["output-format"]
            else:
                # Convert bmp and webp to png by default
                default_conversions = {
                    "bmp": "png",
                    "webp": "png",
                }

                # Convert unanimated GIFs to PNG as well
                if not willow.has_animation():
                    default_conversions["gif"] = "png"

                # Allow the user to override the conversions
                conversion = getattr(settings, "WAGTAILIMAGES_FORMAT_CONVERSIONS", {})
                default_conversions.update(conversion)

                # Get the converted output format falling back to the original
                output_format = default_conversions.get(
                    original_format, original_format
                )

            if output_format == "jpeg":
                # Allow changing of JPEG compression quality
                if "jpeg-quality" in env:
                    quality = env["jpeg-quality"]
                else:
                    quality = getattr(settings, "WAGTAILIMAGES_JPEG_QUALITY", 85)

                # If the video has an alpha channel, give it a white background
                if willow.has_alpha():
                    willow = willow.set_background_color_rgb((255, 255, 255))

                return willow.save_as_jpeg(
                    output, quality=quality, progressive=True, optimize=True
                )
            elif output_format == "png":
                return willow.save_as_png(output, optimize=True)
            elif output_format == "gif":
                return willow.save_as_gif(output)
            elif output_format == "webp":
                # Allow changing of WebP compression quality
                if (
                    "output-format-options" in env
                    and "lossless" in env["output-format-options"]
                ):
                    return willow.save_as_webp(output, lossless=True)
                elif "webp-quality" in env:
                    quality = env["webp-quality"]
                else:
                    quality = getattr(settings, "WAGTAILIMAGES_WEBP_QUALITY", 85)

                return willow.save_as_webp(output, quality=quality)

    def get_cache_key(self, video):
        vary_parts = []

        for operation in self.operations:
            for field in getattr(operation, "vary_fields", []):
                value = getattr(video, field, "")
                vary_parts.append(str(value))

        vary_string = "-".join(vary_parts)

        # Return blank string if there are no vary fields
        if not vary_string:
            return ""

        return hashlib.sha1(vary_string.encode("utf-8")).hexdigest()[:8]


class AbstractRendition(VideoFileMixin, models.Model):
    filter_spec = models.CharField(max_length=255, db_index=True)
    file = models.VideoField(
        upload_to=get_rendition_upload_to, width_field="width", height_field="height"
    )
    width = models.IntegerField(editable=False)
    height = models.IntegerField(editable=False)
    focal_point_key = models.CharField(
        max_length=16, blank=True, default="", editable=False
    )

    @property
    def url(self):
        return self.file.url

    @property
    def alt(self):
        return self.video.default_alt_text

    @property
    def attrs(self):
        """
        The src, width, height, and alt attributes for an <img> tag, as a HTML
        string
        """
        return flatatt(self.attrs_dict)

    @property
    def attrs_dict(self):
        """
        A dict of the src, width, height, and alt attributes for an <img> tag.
        """
        return OrderedDict(
            [
                ("src", self.url),
                ("width", self.width),
                ("height", self.height),
                ("alt", self.alt),
            ]
        )

    @property
    def full_url(self):
        url = self.url
        if hasattr(settings, "BASE_URL") and url.startswith("/"):
            url = settings.BASE_URL + url
        return url

    @property
    def filter(self):
        return Filter(self.filter_spec)

    @cached_property
    def focal_point(self):
        video_focal_point = self.video.get_focal_point()
        if video_focal_point:
            transform = self.filter.get_transform(self.video)
            return video_focal_point.transform(transform)

    @property
    def background_position_style(self):
        """
        Returns a `background-position` rule to be put in the inline style of an element which uses the rendition for its background.

        This positions the rendition according to the value of the focal point. This is helpful for when the element does not have
        the same aspect ratio as the rendition.

        For example:

            {% video page.video fill-1920x600 as video %}
            <div style="background-video: url('{{ video.url }}'); {{ video.background_position_style }}">
            </div>
        """
        focal_point = self.focal_point
        if focal_point:
            horz = int((focal_point.x * 100) // self.width)
            vert = int((focal_point.y * 100) // self.height)
            return "background-position: {}% {}%;".format(horz, vert)
        else:
            return "background-position: 50% 50%;"

    def img_tag(self, extra_attributes={}):
        attrs = self.attrs_dict.copy()
        attrs.update(extra_attributes)
        return mark_safe("<img{}>".format(flatatt(attrs)))

    def __html__(self):
        return self.img_tag()

    def get_upload_to(self, filename):
        folder_name = "videos"
        filename = self.file.field.storage.get_valid_name(filename)
        return os.path.join(folder_name, filename)

    @classmethod
    def check(cls, **kwargs):
        errors = super(AbstractRendition, cls).check(**kwargs)
        if not cls._meta.abstract:
            if not any(
                set(constraint) == {"video", "filter_spec", "focal_point_key"}
                for constraint in cls._meta.unique_together
            ):
                errors.append(
                    checks.Error(
                        "Custom rendition model %r has an invalid unique_together setting"
                        % cls,
                        hint="Custom rendition models must include the constraint "
                        "('video', 'filter_spec', 'focal_point_key') in their unique_together definition.",
                        obj=cls,
                        id="wagtailvideos.E001",
                    )
                )

        return errors

    @staticmethod
    def construct_cache_key(video_id, filter_cache_key, filter_spec):
        return "video-{}-{}-{}".format(video_id, filter_cache_key, filter_spec)

    def purge_from_cache(self):
        try:
            cache = caches["renditions"]
            cache.delete(
                self.construct_cache_key(
                    self.video_id, self.focal_point_key, self.filter_spec
                )
            )
        except InvalidCacheBackendError:
            pass

    class Meta:
        abstract = True


class Rendition(AbstractRendition):
    video = models.ForeignKey(
        Video, related_name="renditions", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (("video", "filter_spec", "focal_point_key"),)


class UploadedVideo(models.Model):
    """
    Temporary storage for videos uploaded through the multiple video uploader, when validation rules (e.g.
    required metadata fields) prevent creating an Video object from the video file alone. In this case,
    the video file is stored against this model, to be turned into an Video object once the full form
    has been filled in.
    """

    file = models.VideoField(upload_to="uploaded_videos", max_length=200)
    uploaded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("uploaded by user"),
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
    )
