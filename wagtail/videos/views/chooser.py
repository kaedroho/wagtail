from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic.base import View

from wagtail.admin.auth import PermissionPolicyChecker
from wagtail.admin.forms.search import SearchForm
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.admin.models import popular_tags_for_model
from wagtail.core import hooks
from wagtail.videos import get_video_model
from wagtail.videos.formats import get_video_format
from wagtail.videos.forms import VideoInsertionForm, get_video_form
from wagtail.videos.permissions import permission_policy
from wagtail.search import index as search_index

permission_checker = PermissionPolicyChecker(permission_policy)

CHOOSER_PAGE_SIZE = getattr(settings, "WAGTAILIMAGES_CHOOSER_PAGE_SIZE", 12)


def get_video_result_data(video):
    """
    helper function: given an video, return the json data to pass back to the
    video chooser panel
    """
    preview_video = video.get_rendition("max-165x165")

    return {
        "id": video.id,
        "edit_link": reverse("wagtailvideos:edit", args=(video.id,)),
        "title": video.title,
        "preview": {
            "url": preview_video.url,
            "width": preview_video.width,
            "height": preview_video.height,
        },
    }


class BaseChooseView(View):
    def get(self, request):
        self.video_model = get_video_model()

        videos = permission_policy.instances_user_has_any_permission_for(
            request.user, ["choose"]
        ).order_by("-created_at")

        # allow hooks to modify the queryset
        for hook in hooks.get_hooks("construct_video_chooser_queryset"):
            videos = hook(videos, request)

        collection_id = request.GET.get("collection_id")
        if collection_id:
            videos = videos.filter(collection=collection_id)

        self.is_searching = False
        self.q = None

        if "q" in request.GET:
            self.search_form = SearchForm(request.GET)
            if self.search_form.is_valid():
                self.q = self.search_form.cleaned_data["q"]
                self.is_searching = True
                videos = videos.search(self.q)
        else:
            self.search_form = SearchForm()

        if not self.is_searching:
            tag_name = request.GET.get("tag")
            if tag_name:
                videos = videos.filter(tags__name=tag_name)

        # Pagination
        paginator = Paginator(videos, per_page=CHOOSER_PAGE_SIZE)
        self.videos = paginator.get_page(request.GET.get("p"))
        return self.render_to_response()

    def get_context_data(self):
        return {
            "videos": self.videos,
            "is_searching": self.is_searching,
            "query_string": self.q,
            "will_select_format": self.request.GET.get("select_format"),
        }

    def render_to_response(self):
        raise NotImplementedError()


class ChooseView(BaseChooseView):
    def get_context_data(self):
        context = super().get_context_data()

        if permission_policy.user_has_permission(self.request.user, "add"):
            VideoForm = get_video_form(self.video_model)
            uploadform = VideoForm(
                user=self.request.user, prefix="video-chooser-upload"
            )
        else:
            uploadform = None

        collections = permission_policy.collections_user_has_permission_for(
            self.request.user, "choose"
        )
        if len(collections) < 2:
            collections = None

        context.update(
            {
                "searchform": self.search_form,
                "popular_tags": popular_tags_for_model(self.video_model),
                "collections": collections,
                "uploadform": uploadform,
            }
        )
        return context

    def render_to_response(self):
        return render_modal_workflow(
            self.request,
            "wagtailvideos/chooser/chooser.html",
            None,
            self.get_context_data(),
            json_data={
                "step": "chooser",
                "error_label": _("Server Error"),
                "error_message": _(
                    "Report this error to your website administrator with the following information:"
                ),
                "tag_autocomplete_url": reverse("wagtailadmin_tag_autocomplete"),
            },
        )


class ChooseResultsView(BaseChooseView):
    def render_to_response(self):
        return TemplateResponse(
            self.request, "wagtailvideos/chooser/results.html", self.get_context_data()
        )


def video_chosen(request, video_id):
    video = get_object_or_404(get_video_model(), id=video_id)

    return render_modal_workflow(
        request,
        None,
        None,
        None,
        json_data={"step": "video_chosen", "result": get_video_result_data(video)},
    )


@permission_checker.require("add")
def chooser_upload(request):
    Video = get_video_model()
    VideoForm = get_video_form(Video)

    if request.method == "POST":
        video = Video(uploaded_by_user=request.user)
        form = VideoForm(
            request.POST,
            request.FILES,
            instance=video,
            user=request.user,
            prefix="video-chooser-upload",
        )

        if form.is_valid():
            # Set video file size
            video.file_size = video.file.size

            # Set video file hash
            video.file.seek(0)
            video._set_file_hash(video.file.read())
            video.file.seek(0)

            form.save()

            # Reindex the video to make sure all tags are indexed
            search_index.insert_or_update_object(video)

            if request.GET.get("select_format"):
                form = VideoInsertionForm(
                    initial={"alt_text": video.default_alt_text},
                    prefix="video-chooser-insertion",
                )
                return render_modal_workflow(
                    request,
                    "wagtailvideos/chooser/select_format.html",
                    None,
                    {"video": video, "form": form},
                    json_data={"step": "select_format"},
                )
            else:
                # not specifying a format; return the video details now
                return render_modal_workflow(
                    request,
                    None,
                    None,
                    None,
                    json_data={
                        "step": "video_chosen",
                        "result": get_video_result_data(video),
                    },
                )
    else:
        form = VideoForm(user=request.user, prefix="video-chooser-upload")

    upload_form_html = render_to_string(
        "wagtailvideos/chooser/upload_form.html",
        {
            "form": form,
            "will_select_format": request.GET.get("select_format"),
        },
        request,
    )

    return render_modal_workflow(
        request,
        None,
        None,
        None,
        json_data={"step": "reshow_upload_form", "htmlFragment": upload_form_html},
    )


def chooser_select_format(request, video_id):
    video = get_object_or_404(get_video_model(), id=video_id)

    if request.method == "POST":
        form = VideoInsertionForm(
            request.POST,
            initial={"alt_text": video.default_alt_text},
            prefix="video-chooser-insertion",
        )
        if form.is_valid():

            format = get_video_format(form.cleaned_data["format"])
            preview_video = video.get_rendition(format.filter_spec)

            video_data = {
                "id": video.id,
                "title": video.title,
                "format": format.name,
                "alt": form.cleaned_data["alt_text"],
                "class": format.classnames,
                "edit_link": reverse("wagtailvideos:edit", args=(video.id,)),
                "preview": {
                    "url": preview_video.url,
                    "width": preview_video.width,
                    "height": preview_video.height,
                },
                "html": format.video_to_editor_html(
                    video, form.cleaned_data["alt_text"]
                ),
            }

            return render_modal_workflow(
                request,
                None,
                None,
                None,
                json_data={"step": "video_chosen", "result": video_data},
            )
    else:
        initial = {"alt_text": video.default_alt_text}
        initial.update(request.GET.dict())
        # If you edit an existing video, and there is no alt text, ensure that
        # "video is decorative" is ticked when you open the form
        initial["video_is_decorative"] = initial["alt_text"] == ""
        form = VideoInsertionForm(initial=initial, prefix="video-chooser-insertion")

    return render_modal_workflow(
        request,
        "wagtailvideos/chooser/select_format.html",
        None,
        {"video": video, "form": form},
        json_data={"step": "select_format"},
    )
