import os

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from wagtail.admin import messages
from wagtail.admin.auth import PermissionPolicyChecker
from wagtail.admin.forms.search import SearchForm
from wagtail.admin.models import popular_tags_for_model
from wagtail.admin.views.pages.utils import get_valid_next_url_from_request
from wagtail.core.models import Collection, Site
from wagtail.videos import get_video_model
from wagtail.videos.exceptions import InvalidFilterSpecError
from wagtail.videos.forms import URLGeneratorForm, get_video_form
from wagtail.videos.models import Filter, SourceVideoIOError
from wagtail.videos.permissions import permission_policy
from wagtail.videos.utils import generate_signature
from wagtail.search import index as search_index

permission_checker = PermissionPolicyChecker(permission_policy)

INDEX_PAGE_SIZE = getattr(settings, "WAGTAILIMAGES_INDEX_PAGE_SIZE", 20)
USAGE_PAGE_SIZE = getattr(settings, "WAGTAILIMAGES_USAGE_PAGE_SIZE", 20)


class BaseListingView(TemplateView):
    @method_decorator(permission_checker.require_any("add", "change", "delete"))
    def get(self, request):
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get videos (filtered by user permission)
        videos = (
            permission_policy.instances_user_has_any_permission_for(
                self.request.user, ["change", "delete"]
            )
            .order_by("-created_at")
            .select_related("collection")
        )

        # Search
        query_string = None
        if "q" in self.request.GET:
            self.form = SearchForm(self.request.GET, placeholder=_("Search videos"))
            if self.form.is_valid():
                query_string = self.form.cleaned_data["q"]

                videos = videos.search(query_string)
        else:
            self.form = SearchForm(placeholder=_("Search videos"))

        # Filter by collection
        self.current_collection = None
        collection_id = self.request.GET.get("collection_id")
        if collection_id:
            try:
                self.current_collection = Collection.objects.get(id=collection_id)
                videos = videos.filter(collection=self.current_collection)
            except (ValueError, Collection.DoesNotExist):
                pass

        # Filter by tag
        self.current_tag = self.request.GET.get("tag")
        if self.current_tag:
            try:
                videos = videos.filter(tags__name=self.current_tag)
            except (AttributeError):
                self.current_tag = None

        paginator = Paginator(videos, per_page=INDEX_PAGE_SIZE)
        videos = paginator.get_page(self.request.GET.get("p"))

        context.update(
            {
                "videos": videos,
                "query_string": query_string,
                "is_searching": bool(query_string),
                "next": self.request.get_full_path(),
            }
        )

        return context


class IndexView(BaseListingView):
    template_name = "wagtailvideos/videos/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        collections = permission_policy.collections_user_has_any_permission_for(
            self.request.user, ["add", "change"]
        )
        if len(collections) < 2:
            collections = None

        Video = get_video_model()

        context.update(
            {
                "search_form": self.form,
                "popular_tags": popular_tags_for_model(get_video_model()),
                "current_tag": self.current_tag,
                "collections": collections,
                "current_collection": self.current_collection,
                "user_can_add": permission_policy.user_has_permission(
                    self.request.user, "add"
                ),
                "app_label": Video._meta.app_label,
                "model_name": Video._meta.model_name,
            }
        )
        return context


class ListingResultsView(BaseListingView):
    template_name = "wagtailvideos/videos/results.html"


@permission_checker.require("change")
def edit(request, video_id):
    Video = get_video_model()
    VideoForm = get_video_form(Video)

    video = get_object_or_404(Video, id=video_id)

    if not permission_policy.user_has_permission_for_instance(
        request.user, "change", video
    ):
        raise PermissionDenied

    next_url = get_valid_next_url_from_request(request)

    if request.method == "POST":
        original_file = video.file
        form = VideoForm(request.POST, request.FILES, instance=video, user=request.user)
        if form.is_valid():
            if "file" in form.changed_data:
                # Set new video file size
                video.file_size = video.file.size

                # Set new video file hash
                video.file.seek(0)
                video._set_file_hash(video.file.read())
                video.file.seek(0)

            form.save()

            if "file" in form.changed_data:
                # if providing a new video file, delete the old one and all renditions.
                # NB Doing this via original_file.delete() clears the file field,
                # which definitely isn't what we want...
                original_file.storage.delete(original_file.name)
                video.renditions.all().delete()

            # Reindex the video to make sure all tags are indexed
            search_index.insert_or_update_object(video)

            edit_url = reverse("wagtailvideos:edit", args=(video.id,))
            redirect_url = "wagtailvideos:index"
            if next_url:
                edit_url = f"{edit_url}?{urlencode({'next': next_url})}"
                redirect_url = next_url

            messages.success(
                request,
                _("Video '{0}' updated.").format(video.title),
                buttons=[messages.button(edit_url, _("Edit again"))],
            )
            return redirect(redirect_url)
        else:
            messages.error(request, _("The video could not be saved due to errors."))
    else:
        form = VideoForm(instance=video, user=request.user)

    # Check if we should enable the frontend url generator
    try:
        reverse("wagtailvideos_serve", args=("foo", "1", "bar"))
        url_generator_enabled = True
    except NoReverseMatch:
        url_generator_enabled = False

    if video.is_stored_locally():
        # Give error if video file doesn't exist
        if not os.path.isfile(video.file.path):
            messages.error(
                request,
                _(
                    "The source video file could not be found. Please change the source or delete the video."
                ).format(video.title),
                buttons=[
                    messages.button(
                        reverse("wagtailvideos:delete", args=(video.id,)), _("Delete")
                    )
                ],
            )

    try:
        filesize = video.get_file_size()
    except SourceVideoIOError:
        filesize = None

    return TemplateResponse(
        request,
        "wagtailvideos/videos/edit.html",
        {
            "video": video,
            "form": form,
            "url_generator_enabled": url_generator_enabled,
            "filesize": filesize,
            "user_can_delete": permission_policy.user_has_permission_for_instance(
                request.user, "delete", video
            ),
            "next": next_url,
        },
    )


def url_generator(request, video_id):
    video = get_object_or_404(get_video_model(), id=video_id)

    if not permission_policy.user_has_permission_for_instance(
        request.user, "change", video
    ):
        raise PermissionDenied

    form = URLGeneratorForm(
        initial={
            "filter_method": "original",
            "width": video.width,
            "height": video.height,
        }
    )

    return TemplateResponse(
        request,
        "wagtailvideos/videos/url_generator.html",
        {
            "video": video,
            "form": form,
        },
    )


def generate_url(request, video_id, filter_spec):
    # Get the video
    Video = get_video_model()
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return JsonResponse({"error": "Cannot find video."}, status=404)

    # Check if this user has edit permission on this video
    if not permission_policy.user_has_permission_for_instance(
        request.user, "change", video
    ):
        return JsonResponse(
            {"error": "You do not have permission to generate a URL for this video."},
            status=403,
        )

    # Parse the filter spec to make sure its valid
    try:
        Filter(spec=filter_spec).operations
    except InvalidFilterSpecError:
        return JsonResponse({"error": "Invalid filter spec."}, status=400)

    # Generate url
    signature = generate_signature(video_id, filter_spec)
    url = reverse("wagtailvideos_serve", args=(signature, video_id, filter_spec))

    # Get site root url
    try:
        site_root_url = Site.objects.get(is_default_site=True).root_url
    except Site.DoesNotExist:
        site_root_url = Site.objects.first().root_url

    # Generate preview url
    preview_url = reverse("wagtailvideos:preview", args=(video_id, filter_spec))

    return JsonResponse(
        {"url": site_root_url + url, "preview_url": preview_url}, status=200
    )


def preview(request, video_id, filter_spec):
    video = get_object_or_404(get_video_model(), id=video_id)

    try:
        response = HttpResponse()
        video = Filter(spec=filter_spec).run(video, response)
        response["Content-Type"] = "video/" + video.format_name
        return response
    except InvalidFilterSpecError:
        return HttpResponse(
            "Invalid filter spec: " + filter_spec, content_type="text/plain", status=400
        )


@permission_checker.require("delete")
def delete(request, video_id):
    video = get_object_or_404(get_video_model(), id=video_id)

    if not permission_policy.user_has_permission_for_instance(
        request.user, "delete", video
    ):
        raise PermissionDenied

    next_url = get_valid_next_url_from_request(request)

    if request.method == "POST":
        video.delete()
        messages.success(request, _("Video '{0}' deleted.").format(video.title))
        return redirect(next_url) if next_url else redirect("wagtailvideos:index")

    return TemplateResponse(
        request,
        "wagtailvideos/videos/confirm_delete.html",
        {
            "video": video,
            "next": next_url,
        },
    )


@permission_checker.require("add")
def add(request):
    VideoModel = get_video_model()
    VideoForm = get_video_form(VideoModel)

    if request.method == "POST":
        video = VideoModel(uploaded_by_user=request.user)
        form = VideoForm(request.POST, request.FILES, instance=video, user=request.user)
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

            messages.success(
                request,
                _("Video '{0}' added.").format(video.title),
                buttons=[
                    messages.button(
                        reverse("wagtailvideos:edit", args=(video.id,)), _("Edit")
                    )
                ],
            )
            return redirect("wagtailvideos:index")
        else:
            messages.error(request, _("The video could not be created due to errors."))
    else:
        form = VideoForm(user=request.user)

    return TemplateResponse(
        request,
        "wagtailvideos/videos/add.html",
        {
            "form": form,
        },
    )


def usage(request, video_id):
    video = get_object_or_404(get_video_model(), id=video_id)

    paginator = Paginator(video.get_usage(), per_page=USAGE_PAGE_SIZE)
    used_by = paginator.get_page(request.GET.get("p"))

    return TemplateResponse(
        request, "wagtailvideos/videos/usage.html", {"video": video, "used_by": used_by}
    )
