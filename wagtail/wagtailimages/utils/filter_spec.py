import re


class InvalidFilterSpecError(RuntimeError):
    pass


# TODO: Cache results from this method in something like Python 3.2s LRU cache (available in Django 1.7 as django.utils.lru_cache)
def parse_filter_spec(filter_spec):
    # parse the spec string and save the results to
    # self.method_name and self.method_arg. There are various possible
    # formats to match against:
    # 'original'
    # 'width-200'
    # 'max-320x200'

    OPERATION_NAMES = {
        'max': 'resize_to_max',
        'min': 'resize_to_min',
        'width': 'resize_to_width',
        'height': 'resize_to_height',
        'fill': 'resize_to_fill',
        'smart': 'smart_crop',
        'original': 'no_operation',
    }

    # original
    if filter_spec == 'original':
        return OPERATION_NAMES['original'], None

    # width/height
    match = re.match(r'(width|height)-(\d+)$', filter_spec)
    if match:
        return OPERATION_NAMES[match.group(1)], int(match.group(2))

    # max/min/fill/smart
    match = re.match(r'(max|min|fill|smart)-(\d+)x(\d+)$', filter_spec)
    if match:
        width = int(match.group(2))
        height = int(match.group(3))
        return OPERATION_NAMES[match.group(1)], (width, height)

    raise InvalidFilterSpecError(filter_spec)
