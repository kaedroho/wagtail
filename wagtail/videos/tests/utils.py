from io import BytesIO

import PIL.Video
from django.core.files.videos import VideoFile

from wagtail.videos import get_video_model

Video = get_video_model()


def get_test_video_file(filename="test.png", colour="white", size=(640, 480)):
    f = BytesIO()
    video = PIL.Video.new("RGBA", size, colour)
    video.save(f, "PNG")
    return VideoFile(f, name=filename)


def get_test_video_file_jpeg(filename="test.jpg", colour="white", size=(640, 480)):
    f = BytesIO()
    video = PIL.Video.new("RGB", size, colour)
    video.save(f, "JPEG")
    return VideoFile(f, name=filename)


def get_test_video_file_webp(filename="test.webp", colour="white", size=(640, 480)):
    f = BytesIO()
    video = PIL.Video.new("RGB", size, colour)
    video.save(f, "WEBP")
    return VideoFile(f, name=filename)
