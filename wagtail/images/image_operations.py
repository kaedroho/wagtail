import inspect

from wagtail.images.exceptions import InvalidFilterSpecError
from wagtail.images.rect import Rect
from wagtail.images.utils import parse_color_string
from willow.plugins.pillow import PillowImage
from willow.registry import registry


class Operation:
    def __init__(self, method, *args):
        self.method = method
        self.args = args

        # Check arguments
        try:
            inspect.getcallargs(self.construct, *args)
        except TypeError as e:
            raise InvalidFilterSpecError(e)

        # Call construct
        try:
            self.construct(*args)
        except ValueError as e:
            raise InvalidFilterSpecError(e)

    def construct(self, *args):
        raise NotImplementedError


# Transforms


def multiply_3x3_matrices(a, b):
    # Dear future reader:
    # If we've added numpy as a dependency of Wagtail, please replace this :)
    c = [0] * 9

    for i in range(3):
        for j in range(3):
            for k in range(3):
                c[i * 3 + j] += a[i * 3 + k] * b[k * 3 + j]

    return c


class TransformContext:
    """
    Tracks transformations that are performed on an image by the transform filters below.

    This allows multiple transforms to be processed in a single operation and also
    provides a matrix that can be used to transform the focal point of the image.
    """
    def __init__(self, size):
        self._check_size(size)
        self.size = size
        self.transform_matrix = [
            1, 0, 0,
            0, 1, 0,
            0, 0 ,1
        ]

    def resize(self, size):
        """
        Change the image size, stretching the transform to make it fit the new size.
        """
        self._check_size(size)
        scale_x = size[0] / self.size[0]
        scale_y = size[1] / self.size[1]
        self.transform_matrix = multiply_3x3_matrices(self.transform_matrix, [
            scale_x, 0, 0,
            0, scale_y, 0,
            0, 0 ,1
        ])
        self.size = size

    def crop(self, rect):
        """
        Crop the image to the specified rect
        """
        self._check_size(rect.size)
        # Transform the image so the top left of the rect is at (0, 0), then set the size
        self.transform_matrix = multiply_3x3_matrices(self.transform_matrix, [
            1, 0, -rect.left,
            0, 1, -rect.top,
            0, 0 ,1
        ])
        self.size = rect.size

    @staticmethod
    def _check_size(size):
        if not isinstance(size, tuple) or len(size) != 2 or int(size[0]) != size[0] or int(size[1]) != size[1]:
            raise TypeError("Image size must be a 2-tuple of integers")

        if size[0] < 1 or size[1] < 1:
            raise ValueError("Image width and height must both be 1 or greater")


class TransformOperation(Operation):
    def run(self, image, context):
        raise NotImplementedError


class FillOperation(TransformOperation):
    vary_fields = ('focal_point_width', 'focal_point_height', 'focal_point_x', 'focal_point_y')

    def construct(self, size, *extra):
        # Get width and height
        width_str, height_str = size.split('x')
        self.width = int(width_str)
        self.height = int(height_str)

        # Crop closeness
        self.crop_closeness = 0

        for extra_part in extra:
            if extra_part.startswith('c'):
                self.crop_closeness = int(extra_part[1:])
            else:
                raise ValueError("Unrecognised filter spec part: %s" % extra_part)

        # Divide it by 100 (as it's a percentage)
        self.crop_closeness /= 100

        # Clamp it
        if self.crop_closeness > 1:
            self.crop_closeness = 1

    def run(self, context, image):
        image_width, image_height = context.size
        focal_point = image.get_focal_point()

        # Get crop aspect ratio
        crop_aspect_ratio = self.width / self.height

        # Get crop max
        crop_max_scale = min(image_width, image_height * crop_aspect_ratio)
        crop_max_width = crop_max_scale
        crop_max_height = crop_max_scale / crop_aspect_ratio

        # Initialise crop width and height to max
        crop_width = crop_max_width
        crop_height = crop_max_height

        # Use crop closeness to zoom in
        if focal_point is not None:
            # Get crop min
            crop_min_scale = max(focal_point.width, focal_point.height * crop_aspect_ratio)
            crop_min_width = crop_min_scale
            crop_min_height = crop_min_scale / crop_aspect_ratio

            # Sometimes, the focal point may be bigger than the image...
            if not crop_min_scale >= crop_max_scale:
                # Calculate max crop closeness to prevent upscaling
                max_crop_closeness = max(
                    1 - (self.width - crop_min_width) / (crop_max_width - crop_min_width),
                    1 - (self.height - crop_min_height) / (crop_max_height - crop_min_height)
                )

                # Apply max crop closeness
                crop_closeness = min(self.crop_closeness, max_crop_closeness)

                if 1 >= crop_closeness >= 0:
                    # Get crop width and height
                    crop_width = crop_max_width + (crop_min_width - crop_max_width) * crop_closeness
                    crop_height = crop_max_height + (crop_min_height - crop_max_height) * crop_closeness

        # Find focal point UV
        if focal_point is not None:
            fp_x, fp_y = focal_point.centroid
        else:
            # Fall back to positioning in the centre
            fp_x = image_width / 2
            fp_y = image_height / 2

        fp_u = fp_x / image_width
        fp_v = fp_y / image_height

        # Position crop box based on focal point UV
        crop_x = fp_x - (fp_u - 0.5) * crop_width
        crop_y = fp_y - (fp_v - 0.5) * crop_height

        # Convert crop box into rect
        rect = Rect.from_point(crop_x, crop_y, crop_width, crop_height)

        # Make sure the entire focal point is in the crop box
        if focal_point is not None:
            rect = rect.move_to_cover(focal_point)

        # Don't allow the crop box to go over the image boundary
        rect = rect.move_to_clamp(Rect(0, 0, image_width, image_height))

        # Crop!
        context = context.crop(rect.round())

        # Get scale for resizing
        # The scale should be the same for both the horizontal and
        # vertical axes
        aftercrop_width, aftercrop_height = context.size
        scale = self.width / aftercrop_width

        # Only resize if the image is too big
        if scale < 1.0:
            # Resize!
            context = context.resize((self.width, self.height))

        return context


class MinMaxOperation(TransformOperation):
    def construct(self, size):
        # Get width and height
        width_str, height_str = size.split('x')
        self.width = int(width_str)
        self.height = int(height_str)

    def run(self, context, image):
        image_width, image_height = context.size

        horz_scale = self.width / image_width
        vert_scale = self.height / image_height

        if self.method == 'min':
            if image_width <= self.width or image_height <= self.height:
                return context

            if horz_scale > vert_scale:
                width = self.width
                height = int(image_height * horz_scale)
            else:
                width = int(image_width * vert_scale)
                height = self.height

        elif self.method == 'max':
            if image_width <= self.width and image_height <= self.height:
                return context

            if horz_scale < vert_scale:
                width = self.width
                height = int(image_height * horz_scale)
            else:
                width = int(image_width * vert_scale)
                height = self.height

        else:
            # Unknown method
            return context

        # prevent zero width or height, it causes a ValueError on context.resize
        width = width if width > 0 else 1
        height = height if height > 0 else 1

        return context.resize((width, height))


class WidthHeightOperation(TransformOperation):
    def construct(self, size):
        self.size = int(size)

    def run(self, context, image):
        image_width, image_height = context.size

        if self.method == 'width':
            if image_width <= self.size:
                return context

            scale = self.size / image_width

            width = self.size
            height = int(image_height * scale)

        elif self.method == 'height':
            if image_height <= self.size:
                return context

            scale = self.size / image_height

            width = int(image_width * scale)
            height = self.size

        else:
            # Unknown method
            return context

        # prevent zero width or height, it causes a ValueError on context.resize
        width = width if width > 0 else 1
        height = height if height > 0 else 1

        return context.resize((width, height))


class ScaleOperation(TransformOperation):
    def construct(self, percent):
        self.percent = float(percent)

    def run(self, context, image):
        image_width, image_height = context.size

        scale = self.percent / 100
        width = int(image_width * scale)
        height = int(image_height * scale)

        # prevent zero width or height, it causes a ValueError on context.resize
        width = width if width > 0 else 1
        height = height if height > 0 else 1

        return context.resize((width, height))


# Filters


class FilterOperation(Operation):
    def run(self, willow, image, env):
        raise NotImplementedError


class DoNothingOperation(FilterOperation):
    def construct(self):
        pass

    def run(self, willow, image, env):
        return willow


class JPEGQualityOperation(FilterOperation):
    def construct(self, quality):
        self.quality = int(quality)

        if self.quality > 100:
            raise ValueError("JPEG quality must not be higher than 100")

    def run(self, willow, image, env):
        env['jpeg-quality'] = self.quality


class WebPQualityOperation(FilterOperation):
    def construct(self, quality):
        self.quality = int(quality)

        if self.quality > 100:
            raise ValueError("WebP quality must not be higher than 100")

    def run(self, willow, image, env):
        env['webp-quality'] = self.quality


class FormatOperation(FilterOperation):
    def construct(self, format, *options):
        self.format = format
        self.options = options

        if self.format not in ['jpeg', 'png', 'gif', 'webp']:
            raise ValueError(
                "Format must be either 'jpeg', 'png', 'gif', or 'webp'")

    def run(self, willow, image, env):
        env['output-format'] = self.format
        env['output-format-options'] = self.options


class BackgroundColorOperation(FilterOperation):
    def construct(self, color_string):
        self.color = parse_color_string(color_string)

    def run(self, willow, image, env):
        return willow.set_background_color_rgb(self.color)


# TEMPORARY
def affine_transform_pillow_image(image, size, matrix):
    from PIL import Image
    return PillowImage(image.image.transform(size, Image.AFFINE, matrix.flatten()[:6]))


registry.register_operation(PillowImage, 'affine_transform', affine_transform_pillow_image)
