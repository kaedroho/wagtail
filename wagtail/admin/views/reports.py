from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.list import BaseListView

from wagtail.core.models import Page, UserPagePermissionsProxy


class ReportView(TemplateResponseMixin, BaseListView):
    header_icon = ''
    page_kwarg = 'p'
    template_name = None
    title = ''
    paginate_by = 10

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, object_list=object_list, **kwargs)
        context['title'] = self.title
        context['header_icon'] = self.header_icon
        return context


class LockedPagesView(ReportView):
    template_name = 'wagtailadmin/reports/locked_pages.html'
    title = _('Locked Pages')
    header_icon = 'locked'

    def get_queryset(self):
        return (UserPagePermissionsProxy(self.request.user).editable_pages() | Page.objects.filter(locked_by=self.request.user)).filter(locked=True)