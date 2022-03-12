import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if django.VERSION >= (3, 2):
    # The declaration is only needed for older Django versions
    pass
else:
    default_app_config = "wagtail.videos.apps.WagtailVideosAppConfig"


def get_video_model_string():
    """
    Get the dotted ``app.Model`` name for the video model as a string.
    Useful for developers making Wagtail plugins that need to refer to the
    video model, such as in foreign keys, but the model itself is not required.
    """
    return getattr(settings, "WAGTAILIMAGES_IMAGE_MODEL", "wagtailvideos.Video")


def get_video_model():
    """
    Get the video model from the ``WAGTAILIMAGES_IMAGE_MODEL`` setting.
    Useful for developers making Wagtail plugins that need the video model.
    Defaults to the standard :class:`~wagtail.videos.models.Video` model
    if no custom model is defined.
    """
    from django.apps import apps

    model_string = get_video_model_string()
    try:
        return apps.get_model(model_string, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "WAGTAILIMAGES_IMAGE_MODEL must be of the form 'app_label.model_name'"
        )
    except LookupError:
        raise ImproperlyConfigured(
            "WAGTAILIMAGES_IMAGE_MODEL refers to model '%s' that has not been installed"
            % model_string
        )
