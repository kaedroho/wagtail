from django.utils.module_loading import import_string
from django.conf import settings

from .embedly import embedly
from .oembed import oembed


def get_finders():
    finder_strings = []

    if hasattr(settings, 'WAGTAILEMBEDS_EMBED_FINDERS'):
        finder_strings.extend(settings.WAGTAILEMBEDS_EMBED_FINDERS)

    if hasattr(settings, 'WAGTAILEMBEDS_EMBED_FINDER'):
        finder_strings.append(settings.WAGTAILEMBEDS_EMBED_FINDER)

        # DEPRECATION WARNING

    # No finders configured, set default value
    if not finder_strings:
        # If EMBEDLY_KEY is set, use embedly
        if hasattr(settings, 'EMBEDLY_KEY'):
            finder_strings.append('wagtail.wagtailembeds.finders.embedly')
        else:
            finder_strings.append('wagtail.wagtailembeds.finder.oembed')

    # Redirect moved finders
    MOVED_FINDERS = {
         'wagtail.wagtailembeds.embeds.embedly': 'wagtail.wagtailembeds.finders.embedly',
         'wagtail.wagtailembeds.embeds.oembed': 'wagtail.wagtailembeds.finders.oembed',
    }
    finder_strings = [
        MOVED_FINDERS[string] if string in MOVED_FINDERS else string
        for string in finder_strings
    ]

    # Import each string and return
    return [
         import_string(string) for string in finder_strings
    ]
