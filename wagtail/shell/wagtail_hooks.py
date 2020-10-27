from django.http import HttpResponse
from django.urls import path

from wagtail.core import hooks


SERVICE_WORKER = r"""
self.addEventListener('install', function(event) {
    console.log("INSTALLED");
});

self.addEventListener('activate', function(event) {
    console.log("ACTIVATED");
});

self.addEventListener('fetch', event => {
    const request = new Request(event.request, {
        headers: {
            ...event.request.headers,
            'X-Requested-With': 'WagtailShell'
        }
    });

    fetch(request).then(console.log);

    event.preventDefault();
    //event.respondWith();
});

"""


def service_worker(request):
    response = HttpResponse(SERVICE_WORKER, content_type='text/javascript')
    response['Service-Worker-Allowed'] = '/admin/'
    return response


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('shell-service-worker.js', service_worker),
    ]
