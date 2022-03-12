from django import forms
from django.conf import settings
from django.forms.models import modelform_factory
from django.utils.text import capfirst
from django.utils.translation import gettext as _

from wagtail.admin import widgets
from wagtail.admin.forms.collections import (
    BaseCollectionMemberForm,
    CollectionChoiceField,
    collection_member_permission_formset_factory,
)
from wagtail.core.models import Collection
from wagtail.videos.fields import WagtailVideoField
from wagtail.videos.formats import get_video_formats
from wagtail.videos.models import Video
from wagtail.videos.permissions import permission_policy as videos_permission_policy


# Callback to allow us to override the default form field for the video file field and collection field.
def formfield_for_dbfield(db_field, **kwargs):
    # Check if this is the file field
    if db_field.name == "file":
        return WagtailVideoField(label=capfirst(db_field.verbose_name), **kwargs)
    elif db_field.name == "collection":
        return CollectionChoiceField(
            label=_("Collection"),
            queryset=Collection.objects.all(),
            empty_label=None,
            **kwargs,
        )

    # For all other fields, just call its formfield() method.
    return db_field.formfield(**kwargs)


class BaseVideoForm(BaseCollectionMemberForm):
    permission_policy = videos_permission_policy

    class Meta:
        # set the 'file' widget to a FileInput rather than the default ClearableFileInput
        # so that when editing, we don't get the 'currently: ...' banner which is
        # a bit pointless here
        widgets = {
            "tags": widgets.AdminTagWidget,
            "file": forms.FileInput(),
            "focal_point_x": forms.HiddenInput(attrs={"class": "focal_point_x"}),
            "focal_point_y": forms.HiddenInput(attrs={"class": "focal_point_y"}),
            "focal_point_width": forms.HiddenInput(
                attrs={"class": "focal_point_width"}
            ),
            "focal_point_height": forms.HiddenInput(
                attrs={"class": "focal_point_height"}
            ),
        }


def get_video_base_form():
    base_form_override = getattr(settings, "WAGTAILIMAGES_IMAGE_FORM_BASE", "")
    if base_form_override:
        from django.utils.module_loading import import_string

        base_form = import_string(base_form_override)
    else:
        base_form = BaseVideoForm
    return base_form


def get_video_form(model):
    fields = model.admin_form_fields
    if "collection" not in fields:
        # force addition of the 'collection' field, because leaving it out can
        # cause dubious results when multiple collections exist (e.g adding the
        # document to the root collection where the user may not have permission) -
        # and when only one collection exists, it will get hidden anyway.
        fields = list(fields) + ["collection"]

    return modelform_factory(
        model,
        form=get_video_base_form(),
        fields=fields,
        formfield_callback=formfield_for_dbfield,
    )


def get_video_multi_form(model_class):
    # edit form for use within the multiple uploader
    VideoForm = get_video_form(model_class)

    # Make a new form with the file and focal point fields excluded
    class VideoEditForm(VideoForm):
        class Meta(VideoForm.Meta):
            model = model_class
            exclude = (
                "file",
                "focal_point_x",
                "focal_point_y",
                "focal_point_width",
                "focal_point_height",
            )

    return VideoEditForm


class VideoInsertionForm(forms.Form):
    """
    Form for selecting parameters of the video (e.g. format) prior to insertion
    into a rich text area
    """

    format = forms.ChoiceField(
        label=_("Format"),
        choices=[(format.name, format.label) for format in get_video_formats()],
        widget=forms.RadioSelect,
    )
    video_is_decorative = forms.BooleanField(
        required=False, label=_("Video is decorative")
    )
    alt_text = forms.CharField(required=False, label=_("Alt text"))

    def clean_alt_text(self):
        alt_text = self.cleaned_data["alt_text"]
        video_is_decorative = self.cleaned_data["video_is_decorative"]

        # Empty the alt text value if the video is set to be decorative
        if video_is_decorative:
            return ""
        else:
            # Alt text is required if video is not decorative.
            if not alt_text:
                msg = _(
                    "Please add some alt text for your video or mark it as decorative"
                )
                self.add_error("alt_text", msg)
        return alt_text


class URLGeneratorForm(forms.Form):
    filter_method = forms.ChoiceField(
        label=_("Filter"),
        choices=(
            ("original", _("Original size")),
            ("width", _("Resize to width")),
            ("height", _("Resize to height")),
            ("min", _("Resize to min")),
            ("max", _("Resize to max")),
            ("fill", _("Resize to fill")),
        ),
    )
    width = forms.IntegerField(label=_("Width"), min_value=0)
    height = forms.IntegerField(label=_("Height"), min_value=0)
    closeness = forms.IntegerField(label=_("Closeness"), min_value=0, initial=0)


GroupVideoPermissionFormSet = collection_member_permission_formset_factory(
    Video,
    [
        ("add_video", _("Add"), _("Add/edit videos you own")),
        ("change_video", _("Edit"), _("Edit any video")),
        ("choose_video", _("Choose"), _("Select videos in choosers")),
    ],
    "wagtailvideos/permissions/includes/video_permissions_formset.html",
)
