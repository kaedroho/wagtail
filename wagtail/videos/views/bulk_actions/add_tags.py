from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from wagtail.admin import widgets
from wagtail.videos.views.bulk_actions.video_bulk_action import VideoBulkAction


class TagForm(forms.Form):
    tags = forms.Field(widget=widgets.AdminTagWidget)


class AddTagsBulkAction(VideoBulkAction):
    display_name = _("Tag")
    action_type = "add_tags"
    aria_label = _("Add tags to the selected videos")
    template_name = "wagtailvideos/bulk_actions/confirm_bulk_add_tags.html"
    action_priority = 20
    form_class = TagForm

    def check_perm(self, video):
        return self.permission_policy.user_has_permission_for_instance(
            self.request.user, "change", video
        )

    def get_execution_context(self):
        return {"tags": self.cleaned_form.cleaned_data["tags"].split(",")}

    @classmethod
    def execute_action(cls, videos, tags=[], **kwargs):
        num_parent_objects = 0
        if not tags:
            return
        for video in videos:
            num_parent_objects += 1
            video.tags.add(*tags)
        return num_parent_objects, 0

    def get_success_message(self, num_parent_objects, num_child_objects):
        return ngettext(
            "New tags have been added to %(num_parent_objects)d video",
            "New tags have been added to %(num_parent_objects)d videos",
            num_parent_objects,
        ) % {"num_parent_objects": num_parent_objects}
