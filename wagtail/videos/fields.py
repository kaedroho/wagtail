import os

import willow
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms.fields import VideoField
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _

ALLOWED_EXTENSIONS = ["gif", "jpg", "jpeg", "png", "webp"]
SUPPORTED_FORMATS_TEXT = _("GIF, JPEG, PNG, WEBP")


class WagtailVideoField(VideoField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get max upload size from settings
        self.max_upload_size = getattr(
            settings, "WAGTAILIMAGES_MAX_UPLOAD_SIZE", 10 * 1024 * 1024
        )
        self.max_video_pixels = getattr(
            settings, "WAGTAILIMAGES_MAX_IMAGE_PIXELS", 128 * 1000000
        )
        max_upload_size_text = filesizeformat(self.max_upload_size)

        # Help text
        if self.max_upload_size is not None:
            self.help_text = _(
                "Supported formats: %(supported_formats)s. Maximum filesize: %(max_upload_size)s."
            ) % {
                "supported_formats": SUPPORTED_FORMATS_TEXT,
                "max_upload_size": max_upload_size_text,
            }
        else:
            self.help_text = _("Supported formats: %(supported_formats)s.") % {
                "supported_formats": SUPPORTED_FORMATS_TEXT,
            }

        # Error messages
        self.error_messages["invalid_video_extension"] = (
            _("Not a supported video format. Supported formats: %s.")
            % SUPPORTED_FORMATS_TEXT
        )

        self.error_messages["invalid_video_known_format"] = _("Not a valid %s video.")

        self.error_messages["file_too_large"] = (
            _("This file is too big (%%s). Maximum filesize %s.") % max_upload_size_text
        )

        self.error_messages["file_too_many_pixels"] = (
            _("This file has too many pixels (%%s). Maximum pixels %s.")
            % self.max_video_pixels
        )

        self.error_messages["file_too_large_unknown_size"] = (
            _("This file is too big. Maximum filesize %s.") % max_upload_size_text
        )

    def check_video_file_format(self, f):
        # Check file extension
        extension = os.path.splitext(f.name)[1].lower()[1:]

        if extension not in ALLOWED_EXTENSIONS:
            raise ValidationError(
                self.error_messages["invalid_video_extension"],
                code="invalid_video_extension",
            )

        video_format = extension.upper()
        if video_format == "JPG":
            video_format = "JPEG"

        internal_video_format = f.video.format.upper()
        if internal_video_format == "MPO":
            internal_video_format = "JPEG"

        # Check that the internal format matches the extension
        # It is possible to upload PSD files if their extension is set to jpg, png or gif. This should catch them out
        if internal_video_format != video_format:
            raise ValidationError(
                self.error_messages["invalid_video_known_format"] % (video_format,),
                code="invalid_video_known_format",
            )

    def check_video_file_size(self, f):
        # Upload size checking can be disabled by setting max upload size to None
        if self.max_upload_size is None:
            return

        # Check the filesize
        if f.size > self.max_upload_size:
            raise ValidationError(
                self.error_messages["file_too_large"] % (filesizeformat(f.size),),
                code="file_too_large",
            )

    def check_video_pixel_size(self, f):
        # Upload pixel size checking can be disabled by setting max upload pixel to None
        if self.max_video_pixels is None:
            return

        # Check the pixel size
        video = willow.Video.open(f)
        width, height = video.get_size()
        frames = video.get_frame_count()
        num_pixels = width * height * frames

        if num_pixels > self.max_video_pixels:
            raise ValidationError(
                self.error_messages["file_too_many_pixels"] % (num_pixels),
                code="file_too_many_pixels",
            )

    def to_python(self, data):
        f = super().to_python(data)

        if f is not None:
            self.check_video_file_size(f)
            self.check_video_file_format(f)
            self.check_video_pixel_size(f)

        return f
