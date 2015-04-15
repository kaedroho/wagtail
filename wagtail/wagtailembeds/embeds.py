from datetime import datetime

from wagtail.wagtailembeds.models import Embed
from wagtail.wagtailembeds.finders import get_finders


def get_embed(url, finder=None, **kwargs):
    # Check database
    try:
        return Embed.objects.get(url=url, max_width=max_width)
    except Embed.DoesNotExist:
        pass

    # Get finders
    finders = [finder] if finder else get_finders()

    # Try each finder
    embed_dict = None
    for finder in finders:
        embed_dict = finder(url, **kwargs)

        # Finish search if the finder returned something
        if embed_dict:
            break

    # Quit if no finder found anything
    if not embed_dict:
        return

    # Make sure width and height are valid integers before inserting into database
    try:
        embed_dict['width'] = int(embed_dict['width'])
    except (TypeError, ValueError):
        embed_dict['width'] = None

    try:
        embed_dict['height'] = int(embed_dict['height'])
    except (TypeError, ValueError):
        embed_dict['height'] = None

    # Make sure html field is valid
    if 'html' not in embed_dict or not embed_dict['html']:
        embed_dict['html'] = ''

    embed, created = Embed.objects.get_or_create(
        url=url,
        max_width=max_width,
        defaults=embed_dict,
    )

    # Save
    embed.last_updated = datetime.now()
    embed.save()

    return embed
