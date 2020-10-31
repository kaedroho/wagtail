from django.http import JsonResponse
from django.shortcuts import render


class ShellResponse(JsonResponse):
    status = None

    def __init__(self, *args, **kwargs):
        data = {
            'status': self.status,
        }
        data.update(self.get_data(*args, **kwargs))
        super().__init__(data)
        self['X-WagtailShellStatus'] = self.status

    def get_data(self):
        return {}


class ShellResponseLoadIt(ShellResponse):
    status = 'load-it'


class ShellResponseRenderHtml(ShellResponse):
    status = 'render-html'

    def get_data(self, html):
        return {
            'html': html,
        }


class ShellResponseRenderClientSideView(ShellResponse):
    status = 'render-client-side-view'

    def get_data(self, view, context):
        return {
            'view': view,
            'context': context,
        }


class ShellResponseNotFound(ShellResponse):
    status = 'not-found'


class ShellResponsePermissionDenied(ShellResponse):
    status = 'permission-denied'


IFRAME_SAFE_VIEWS = [
    ('wagtail.images.views.images', 'edit'),
    ('wagtail.images.views.images', 'delete'),
    ('wagtail.documents.views.documents', 'edit'),
    ('wagtail.documents.views.documents', 'delete'),
    ('wagtail.snippets.views.snippets', 'index'),
    ('wagtail.snippets.views.snippets', 'list'),
    ('wagtail.snippets.views.snippets', 'edit'),
    ('wagtail.snippets.views.snippets', 'delete'),
    ('wagtail.contrib.modeladmin.options', 'index_view'),
    ('wagtail.contrib.modeladmin.options', 'edit_view'),
    ('wagtail.contrib.modeladmin.options', 'delete_view'),
    ('wagtail.contrib.forms.views', 'FormPagesListView'),
    ('wagtail.contrib.forms.views', 'get_submissions_list_view'),
    ('wagtail.admin.views.reports', 'LockedPagesView'),
    ('wagtail.admin.views.reports', 'WorkflowView'),
    ('wagtail.admin.views.reports', 'WorkflowTasksView'),
    ('wagtail.admin.views.reports', 'LogEntriesView'),
    ('wagtail.admin.views.workflows', 'Index'),
    ('wagtail.admin.views.workflows', 'TaskIndex'),
    ('wagtail.users.views.users', 'index'),
    ('wagtail.users.views.groups', 'IndexView'),
    ('wagtail.users.views.groups', 'DeleteView'),
    ('wagtail.sites.views', 'IndexView'),
    ('wagtail.sites.views', 'EditView'),
    ('wagtail.sites.views', 'DeleteView'),
    ('wagtail.locales.views', 'IndexView'),
    ('wagtail.locales.views', 'EditView'),
    ('wagtail.locales.views', 'DeleteView'),
    ('wagtail.admin.views.collections', 'Index'),
    ('wagtail.contrib.redirects.views', 'index'),
    ('wagtail.contrib.search_promotions.views', 'index'),
    ('wagtail.contrib.styleguide.views', 'index'),
]


class WagtailShellMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def is_iframe_safe(self, request, view_func):
        """
        Returns True if the specified request/view is safe to render in
        an iframe.

        We need to know this ahead of time so that we know if we should render the
        legacy menu in "templates/wagtailadmin/base.html".
        """
        # TODO Turn this into a view decorator
        return (view_func.__module__, view_func.__name__) in IFRAME_SAFE_VIEWS

    def process_view(self, request, view_func, view_args, view_kwargs):
        request.shell_iframe_safe = self.is_iframe_safe(request, view_func)

    def __call__(self, request):
        response = self.get_response(request)

        # If the response is already a shell response, return it
        if isinstance(response, ShellResponse):
            return response

        # FIXME: Find a proper mime type parser
        is_html = response['Content-Type'] == 'text/html; charset=utf-8'

        # If the request was made by Wagtail shell, convert the Django
        # response into a shell response
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'WagtailShell':
            # If the response is not HTML, or can't be rendered in an iframe, return a load-it response
            if not is_html or not request.shell_iframe_safe:
                return ShellResponseLoadIt()

            return ShellResponseRenderHtml(response.content.decode('utf-8'))

        # The request wasn't made by the shell
        # If the response is HTML, and rendered using Wagtail's base admin template,
        # wrap the response with the shell's bootstrap template
        # so wrap the response with the shell
        # bootstrap code if
        if is_html and request.shell_iframe_safe and getattr(request, 'shell_template_rendered', False):
            return render(request, 'wagtailshell/bootstrap.html', {
                'content': response.content.decode('utf-8'),
            })

        return response
