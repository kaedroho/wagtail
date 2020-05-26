from django.urls import path

from wagtail.admin.views import workflows


app_name = 'wagtailadmin_workflows'
urlpatterns = [
    path('', workflows.Index.as_view(), name='index'),
    path('add/', workflows.Create.as_view(), name='add'),
    path('enable/<int:pk>/', workflows.enable_workflow, name='enable'),
    path('disable/<int:pk>/', workflows.Disable.as_view(), name='disable'),
    path('edit/<int:pk>/', workflows.Edit.as_view(), name='edit'),
    path('remove/<int:page_pk>/', workflows.remove_workflow, name='remove'),
    path('remove/<int:page_pk>/<int:workflow_pk>/', workflows.remove_workflow, name='remove'),
    path('add_to_page/<int:workflow_pk>/', workflows.add_to_page, name='add_to_page'),
]
