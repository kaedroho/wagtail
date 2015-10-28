from django.template.loader import render_to_string

from wagtail.wagtailembeds import embeds


def embed_to_frontend_html(url):
    try:
        embed = embeds.get_embed(url)

        # Render template
        return render_to_string('wagtailembeds/embed_frontend.html', {
            'embed': embed,
        })
    except embeds.EmbedException:
        return ''


def embed_to_editor_html(url):
    try:
        embed = embeds.get_embed(url)

        # Render template
        return render_to_string('wagtailembeds/embed_editor.html', {
            'embed': embed,
        })
    except embeds.EmbedException:
        # Could be replaced with a nice error message
        return ''
