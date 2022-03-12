"""
editor-html conversion for contenteditable editors
"""
from wagtail.admin.rich_text.converters import editor_html
from wagtail.videos import get_video_model
from wagtail.videos.formats import get_video_format


class VideoEmbedHandler:
    """
    VideoEmbedHandler will be invoked whenever we encounter an element in HTML content
    with an attribute of data-embedtype="video". The resulting element in the database
    representation will be:
    <embed embedtype="video" id="42" format="thumb" alt="some custom alt text">
    """

    @staticmethod
    def get_db_attributes(tag):
        """
        Given a tag that we've identified as an video embed (because it has a
        data-embedtype="video" attribute), return a dict of the attributes we should
        have on the resulting <embed> element.
        """
        return {
            "id": tag["data-id"],
            "format": tag["data-format"],
            "alt": tag["data-alt"],
        }

    @staticmethod
    def expand_db_attributes(attrs):
        """
        Given a dict of attributes from the <embed> tag, return the real HTML
        representation for use within the editor.
        """
        Video = get_video_model()
        try:
            video = Video.objects.get(id=attrs["id"])
        except Video.DoesNotExist:
            return '<img alt="">'

        video_format = get_video_format(attrs["format"])

        return video_format.video_to_editor_html(video, attrs.get("alt", ""))


EditorHTMLVideoConversionRule = [editor_html.EmbedTypeRule("video", VideoEmbedHandler)]
