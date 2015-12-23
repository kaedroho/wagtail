from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as __

from wagtail.wagtailcore.models import Site
from wagtail.wagtailcore.permissions import site_permission_policy
from wagtail.wagtailsites.forms import SiteForm
from wagtail.wagtailadmin.views import generic
from wagtail.wagtailadmin.viewsets.model import ModelViewSet


class IndexView(generic.IndexView):
    template_name = 'wagtailsites/index.html'
    page_title = __("Sites")
    add_item_label = __("Add a site")


class CreateView(generic.CreateView):
    page_title = __("Add site")
    success_message = __("Site '{0}' created.")
    template_name = 'wagtailsites/create.html'


class EditView(generic.EditView):
    success_message = __("Site '{0}' updated.")
    error_message = __("The site could not be saved due to errors.")
    context_object_name = 'site'
    template_name = 'wagtailsites/edit.html'


class DeleteView(generic.DeleteView):
    success_message = __("Site '{0}' deleted.")
    page_title = __("Delete site")
    confirmation_message = __("Are you sure you want to delete this site?")


class SiteViewSet(ModelViewSet):
    icon = 'site'
    model = Site
    permission_policy = site_permission_policy

    index_view_class = IndexView
    add_view_class = CreateView
    edit_view_class = EditView
    delete_view_class = DeleteView

    def get_form_class(self, for_update=False):
        return SiteForm
