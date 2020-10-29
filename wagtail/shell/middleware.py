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


class WagtailShellMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

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
            # If the response is not HTML, return a load-it response
            if not is_html:
                return ShellResponseLoadIt()

            return ShellResponseRenderHtml(response.content.decode('utf-8'))

        # The request wasn't made by the shell
        # If the response is HTML, and rendered using Wagtail's base admin template,
        # wrap the response with the shell's bootstrap template
        # so wrap the response with the shell
        # bootstrap code if
        if is_html and getattr(request, 'shell_template_rendered', False):
            return render(request, 'wagtailshell/bootstrap.html', {
                'content': response.content.decode('utf-8'),
            })

        return response
