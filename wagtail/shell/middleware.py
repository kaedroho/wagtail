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


class WagtailShellMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # If the request was made by Wagtail shell, return the content
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'WagtailShell':
            return ShellResponseRenderHtml(response.content.decode('utf-8'))

        # Also, if the response is not HTML
        # FIXME: Find a proper mime type parser
        if response['Content-Type'] != 'text/html; charset=utf-8':
            return response

        # If the request wasn't for the admin, return the response as-is
        if not getattr(request, 'shell_template_rendered', False):
            return response

        return render(request, 'wagtailshell/template.html', {
            'content': response.content.decode('utf-8'),
        })
