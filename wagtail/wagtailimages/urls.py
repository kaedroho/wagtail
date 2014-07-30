from django.conf.urls import url

from wagtail.wagtailimages.views import frontend


urlpatterns = [
    url(r'^(.*)/(\d*)/(.*)/$', frontend.serve, name='wagtailimages_serve'),
]


from django.core.urlresolvers import reverse, Resolver404
from django.core.exceptions import ImproperlyConfigured

def check_url_patterns(urlconf=None):
    # Make sure that wagtailimages.urls wasn't imported into '/admin/images/' by mistake.
    # wagtailimages.urls was previously used for admin URLs so an old project may still
    # be using it for the admin.
    try:
        url = reverse('wagtailimages_serve', args=('foo', 123, 'bar'), urlconf=urlconf)

        if url.startswith('/admin/'):
            raise ImproperlyConfigured("Error with URL configuration: 'wagtailimages.urls' is being imported under '/admin/'. Use \"url(r'^images/', include(wagtailimages_urls))\" instead.")
    except Resolver404:
        pass

