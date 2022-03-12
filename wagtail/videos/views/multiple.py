import os.path

from wagtail.admin.views.generic.multiple_upload import AddView as BaseAddView
from wagtail.admin.views.generic.multiple_upload import (
    CreateFromUploadView as BaseCreateFromUploadView,
)
from wagtail.admin.views.generic.multiple_upload import (
    DeleteUploadView as BaseDeleteUploadView,
)
from wagtail.admin.views.generic.multiple_upload import DeleteView as BaseDeleteView
from wagtail.admin.views.generic.multiple_upload import EditView as BaseEditView
from wagtail.videos import get_video_model
from wagtail.videos.fields import ALLOWED_EXTENSIONS
from wagtail.videos.forms import get_video_form, get_video_multi_form
from wagtail.videos.models import UploadedVideo
from wagtail.videos.permissions import permission_policy
from wagtail.search.backends import get_search_backends


class AddView(BaseAddView):
    permission_policy = permission_policy
    template_name = "wagtailvideos/multiple/add.html"
    upload_model = UploadedVideo

    edit_object_url_name = "wagtailvideos:edit_multiple"
    delete_object_url_name = "wagtailvideos:delete_multiple"
    edit_object_form_prefix = "video"
    context_object_name = "video"
    context_object_id_name = "video_id"

    edit_upload_url_name = "wagtailvideos:create_multiple_from_uploaded_video"
    delete_upload_url_name = "wagtailvideos:delete_upload_multiple"
    edit_upload_form_prefix = "uploaded-video"
    context_upload_name = "uploaded_video"
    context_upload_id_name = "uploaded_video_id"

    def get_model(self):
        return get_video_model()

    def get_upload_form_class(self):
        return get_video_form(self.model)

    def get_edit_form_class(self):
        return get_video_multi_form(self.model)

    def save_object(self, form):
        video = form.save(commit=False)
        video.uploaded_by_user = self.request.user
        video.file_size = video.file.size
        video.file.seek(0)
        video._set_file_hash(video.file.read())
        video.file.seek(0)
        video.save()
        return video

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "max_filesize": self.form.fields["file"].max_upload_size,
                "max_title_length": self.form.fields["title"].max_length,
                "allowed_extensions": ALLOWED_EXTENSIONS,
                "error_max_file_size": self.form.fields["file"].error_messages[
                    "file_too_large_unknown_size"
                ],
                "error_accepted_file_types": self.form.fields["file"].error_messages[
                    "invalid_video_extension"
                ],
            }
        )

        return context


class EditView(BaseEditView):
    permission_policy = permission_policy
    pk_url_kwarg = "video_id"
    edit_object_form_prefix = "video"
    context_object_name = "video"
    context_object_id_name = "video_id"
    edit_object_url_name = "wagtailvideos:edit_multiple"
    delete_object_url_name = "wagtailvideos:delete_multiple"

    def get_model(self):
        return get_video_model()

    def get_edit_form_class(self):
        return get_video_multi_form(self.model)

    def save_object(self, form):
        form.save()

        # Reindex the video to make sure all tags are indexed
        for backend in get_search_backends():
            backend.add(self.object)


class DeleteView(BaseDeleteView):
    permission_policy = permission_policy
    pk_url_kwarg = "video_id"
    context_object_id_name = "video_id"

    def get_model(self):
        return get_video_model()


class CreateFromUploadedVideoView(BaseCreateFromUploadView):
    edit_upload_url_name = "wagtailvideos:create_multiple_from_uploaded_video"
    delete_upload_url_name = "wagtailvideos:delete_upload_multiple"
    upload_model = UploadedVideo
    upload_pk_url_kwarg = "uploaded_video_id"
    edit_upload_form_prefix = "uploaded-video"
    context_object_id_name = "video_id"
    context_upload_name = "uploaded_video"

    def get_model(self):
        return get_video_model()

    def get_edit_form_class(self):
        return get_video_multi_form(self.model)

    def save_object(self, form):
        # assign the file content from uploaded_video to the video object, to ensure it gets saved to
        # Video's storage

        self.object.file.save(
            os.path.basename(self.upload.file.name), self.upload.file.file, save=False
        )
        self.object.uploaded_by_user = self.request.user
        self.object.file_size = self.object.file.size
        self.object.file.open()
        self.object.file.seek(0)
        self.object._set_file_hash(self.object.file.read())
        self.object.file.seek(0)
        form.save()

        # Reindex the video to make sure all tags are indexed
        for backend in get_search_backends():
            backend.add(self.object)


class DeleteUploadView(BaseDeleteUploadView):
    upload_model = UploadedVideo
    upload_pk_url_kwarg = "uploaded_video_id"
