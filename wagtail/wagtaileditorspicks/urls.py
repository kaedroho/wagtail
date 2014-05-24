from django.conf.urls import url
from wagtail.wagtaileditorspicks.views import editorspicks, queries


urlpatterns = [
    url(r'^$', editorspicks.index, name='wagtaileditorspicks_editorspicks_index'),
    url(r'^_add/$', editorspicks.add, name='wagtaileditorspicks_editorspicks_add'),
    url(r'^([\w\-]+)/$', editorspicks.edit, name='wagtaileditorspicks_editorspicks_edit'),
    url(r'^([\w\-]+)/delete/$', editorspicks.delete, name='wagtaileditorspicks_editorspicks_delete'),

    url(r'^queries/chooser/$', queries.chooser, name='wagtaileditorspicks_queries_chooser'),
    url(r'^queries/chooser/results/$', queries.chooserresults, name='wagtaileditorspicks_queries_chooserresults'),
]

# Register signal handlers
from . import signal_handlers
