from django import template
from django.utils.safestring import mark_safe

from wagtail.wagtailembeds import embeds


register = template.Library()


@register.filter
def embed(url, max_width=None):
    try:
        embed = embeds.get_embed(url, max_width=max_width)
        return mark_safe(embed.html)
    except embeds.EmbedException:
        return ''


@register.simple_tag(name='embed')
def embed_tag(url, max_width=None):
    try:
        return embeds.get_embed(url, max_width=max_width)
    except embeds.EmbedException:
        pass
