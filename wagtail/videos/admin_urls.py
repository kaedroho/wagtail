from django.urls import path

from wagtail.videos.views import chooser, videos, multiple

app_name = "wagtailvideos"
urlpatterns = [
    path("", videos.IndexView.as_view(), name="index"),
    path("results/", videos.ListingResultsView.as_view(), name="listing_results"),
    path("<int:video_id>/", videos.edit, name="edit"),
    path("<int:video_id>/delete/", videos.delete, name="delete"),
    path("<int:video_id>/generate_url/", videos.url_generator, name="url_generator"),
    path(
        "<int:video_id>/generate_url/<str:filter_spec>/",
        videos.generate_url,
        name="generate_url",
    ),
    path("<int:video_id>/preview/<str:filter_spec>/", videos.preview, name="preview"),
    path("add/", videos.add, name="add"),
    path("usage/<int:video_id>/", videos.usage, name="video_usage"),
    path("multiple/add/", multiple.AddView.as_view(), name="add_multiple"),
    path("multiple/<int:video_id>/", multiple.EditView.as_view(), name="edit_multiple"),
    path(
        "multiple/create_from_uploaded_video/<int:uploaded_video_id>/",
        multiple.CreateFromUploadedVideoView.as_view(),
        name="create_multiple_from_uploaded_video",
    ),
    path(
        "multiple/<int:video_id>/delete/",
        multiple.DeleteView.as_view(),
        name="delete_multiple",
    ),
    path(
        "multiple/delete_upload/<int:uploaded_video_id>/",
        multiple.DeleteUploadView.as_view(),
        name="delete_upload_multiple",
    ),
    path("chooser/", chooser.ChooseView.as_view(), name="chooser"),
    path(
        "chooser/results/", chooser.ChooseResultsView.as_view(), name="chooser_results"
    ),
    path("chooser/<int:video_id>/", chooser.video_chosen, name="video_chosen"),
    path("chooser/upload/", chooser.chooser_upload, name="chooser_upload"),
    path(
        "chooser/<int:video_id>/select_format/",
        chooser.chooser_select_format,
        name="chooser_select_format",
    ),
]
