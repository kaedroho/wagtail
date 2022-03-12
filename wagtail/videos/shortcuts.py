from wagtail.videos.models import SourceVideoIOError


def get_rendition_or_not_found(video, specs):
    """
    Tries to get / create the rendition for the video or renders a not-found video if it does not exist.

    :param video: AbstractVideo
    :param specs: str or Filter
    :return: Rendition
    """
    try:
        return video.get_rendition(specs)
    except SourceVideoIOError:
        # Video file is (probably) missing from /media/original_videos - generate a dummy
        # rendition so that we just output a broken video, rather than crashing out completely
        # during rendering.
        Rendition = (
            video.renditions.model
        )  # pick up any custom Video / Rendition classes that may be in use
        rendition = Rendition(video=video, width=0, height=0)
        rendition.file.name = "not-found"
        return rendition
