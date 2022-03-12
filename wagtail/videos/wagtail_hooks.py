from django.urls import include, path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.admin_url_finder import (
    ModelAdminURLFinder,
    register_admin_url_finder,
)
from wagtail.admin.menu import MenuItem
from wagtail.admin.navigation import get_site_for_user
from wagtail.admin.search import SearchArea
from wagtail.admin.site_summary import SummaryItem
from wagtail.core import hooks
from wagtail.videos import admin_urls, get_video_model, video_operations
from wagtail.videos.api.admin.views import VideosAdminAPIViewSet
from wagtail.videos.forms import GroupVideoPermissionFormSet
from wagtail.videos.permissions import permission_policy
from wagtail.videos.rich_text import VideoEmbedHandler
from wagtail.videos.rich_text.contentstate import ContentstateVideoConversionRule
from wagtail.videos.rich_text.editor_html import EditorHTMLVideoConversionRule
from wagtail.videos.views.bulk_actions import (
    AddTagsBulkAction,
    AddToCollectionBulkAction,
    DeleteBulkAction,
)


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        path("videos/", include(admin_urls, namespace="wagtailvideos")),
    ]


@hooks.register("construct_admin_api")
def construct_admin_api(router):
    router.register_endpoint("videos", VideosAdminAPIViewSet)


class VideosMenuItem(MenuItem):
    def is_shown(self, request):
        return permission_policy.user_has_any_permission(
            request.user, ["add", "change", "delete"]
        )


@hooks.register("register_admin_menu_item")
def register_videos_menu_item():
    return VideosMenuItem(
        _("Videos"),
        reverse("wagtailvideos:index"),
        name="videos",
        icon_name="video",
        order=300,
    )


@hooks.register("insert_editor_js")
def editor_js():
    return format_html(
        """
        <script>
            window.chooserUrls.videoChooser = '{0}';
        </script>
        """,
        reverse("wagtailvideos:chooser"),
    )


@hooks.register("register_rich_text_features")
def register_video_feature(features):
    # define a handler for converting <embed embedtype="video"> tags into frontend HTML
    features.register_embed_type(VideoEmbedHandler)

    # define how to convert between editorhtml's representation of videos and
    # the database representation
    features.register_converter_rule(
        "editorhtml", "video", EditorHTMLVideoConversionRule
    )

    # define a draftail plugin to use when the 'video' feature is active
    features.register_editor_plugin(
        "draftail",
        "video",
        draftail_features.EntityFeature(
            {
                "type": "IMAGE",
                "icon": "video",
                "description": gettext("Video"),
                # We do not want users to be able to copy-paste hotlinked videos into rich text.
                # Keep only the attributes Wagtail needs.
                "attributes": ["id", "src", "alt", "format"],
                # Keep only videos which are from Wagtail.
                "whitelist": {
                    "id": True,
                },
            },
            js=[
                "wagtailvideos/js/video-chooser-modal.js",
            ],
        ),
    )

    # define how to convert between contentstate's representation of videos and
    # the database representation
    features.register_converter_rule(
        "contentstate", "video", ContentstateVideoConversionRule
    )

    # add 'video' to the set of on-by-default rich text features
    features.default_features.append("video")


@hooks.register("register_video_operations")
def register_video_operations():
    return [
        ("original", video_operations.DoNothingOperation),
        ("fill", video_operations.FillOperation),
        ("min", video_operations.MinMaxOperation),
        ("max", video_operations.MinMaxOperation),
        ("width", video_operations.WidthHeightOperation),
        ("height", video_operations.WidthHeightOperation),
        ("scale", video_operations.ScaleOperation),
        ("jpegquality", video_operations.JPEGQualityOperation),
        ("webpquality", video_operations.WebPQualityOperation),
        ("format", video_operations.FormatOperation),
        ("bgcolor", video_operations.BackgroundColorOperation),
    ]


class VideosSummaryItem(SummaryItem):
    order = 200
    template_name = "wagtailvideos/homepage/site_summary_videos.html"

    def get_context_data(self, parent_context):
        site_name = get_site_for_user(self.request.user)["site_name"]

        return {
            "total_videos": get_video_model().objects.count(),
            "site_name": site_name,
        }

    def is_shown(self):
        return permission_policy.user_has_any_permission(
            self.request.user, ["add", "change", "delete"]
        )


@hooks.register("construct_homepage_summary_items")
def add_videos_summary_item(request, items):
    items.append(VideosSummaryItem(request))


class VideosSearchArea(SearchArea):
    def is_shown(self, request):
        return permission_policy.user_has_any_permission(
            request.user, ["add", "change", "delete"]
        )


@hooks.register("register_admin_search_area")
def register_videos_search_area():
    return VideosSearchArea(
        _("Videos"),
        reverse("wagtailvideos:index"),
        name="videos",
        icon_name="video",
        order=200,
    )


@hooks.register("register_group_permission_panel")
def register_video_permissions_panel():
    return GroupVideoPermissionFormSet


@hooks.register("describe_collection_contents")
def describe_collection_docs(collection):
    videos_count = get_video_model().objects.filter(collection=collection).count()
    if videos_count:
        url = reverse("wagtailvideos:index") + ("?collection_id=%d" % collection.id)
        return {
            "count": videos_count,
            "count_text": ngettext("%(count)s video", "%(count)s videos", videos_count)
            % {"count": videos_count},
            "url": url,
        }


class VideoAdminURLFinder(ModelAdminURLFinder):
    edit_url_name = "wagtailvideos:edit"
    permission_policy = permission_policy


register_admin_url_finder(get_video_model(), VideoAdminURLFinder)


for action_class in [AddTagsBulkAction, AddToCollectionBulkAction, DeleteBulkAction]:
    hooks.register("register_bulk_action", action_class)
