from bs4 import BeautifulSoup

from urllib.parse import urlparse

from django.http import HttpRequest, JsonResponse, QueryDict
from django.urls import resolve
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

    def get_data(self, title, content, css, js):
        return {
            'title': title,
            'content': content,
            'css': css,
            'js': js,
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


class ShellRequest(HttpRequest):
    def __init__(self, wsgi_request, path, query_string):
        self.wsgi_request = wsgi_request
        self.path = path
        self.query_string = query_string

        self.method = 'GET'
        self.META = self.wsgi_request.META.copy()

        self.shell_template_rendered = False

    @property
    def GET(self):
        return QueryDict(self.query_string)

    @property
    def POST(self):
        return QueryDict()


def shell(request):
    url = request.GET.get('url')

    if not url:
        return ShellResponseNotFound()

    parsed = urlparse(url)

    match = resolve(parsed.path)

    shell_request = ShellRequest(request, parsed.path, parsed.query)
    shell_request.user = request.user

    response = match.func(shell_request, *match.args, **match.kwargs)
    response.render()

    if isinstance(response, ShellResponse):
        return response

    if shell_request.shell_template_rendered:
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('title').text
        content = soup.find(id='wagtailshell-content').encode_contents().decode('utf-8')
        css = soup.find(id='wagtailshell-css').encode_contents().decode('utf-8')
        js = soup.find(id='wagtailshell-js').encode_contents().decode('utf-8')
        return ShellResponseRenderHtml(title, content, css, js)

    return ShellResponseLoadIt()


def template(request):
    return render(request, 'wagtailshell/template.html')
