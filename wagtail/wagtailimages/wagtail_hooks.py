from django.conf import settings
from django.conf.urls import include, url
from django.core.exceptions import ImproperlyConfigured
from django.core import urlresolvers
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.menu import MenuItem

from wagtail.wagtailimages import admin_urls


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^images/', include(admin_urls)),
    ]


def check_url_patterns(urlconf=None):
    # Make sure that wagtailimages.urls wasn't imported into '/admin/images/' by mistake.
    # wagtailimages.urls was previously used for admin URLs so an old project may still
    # be using it for the admin.
    try:
        url = urlresolvers.reverse('wagtailimages_serve', args=('foo', 123, 'bar'), urlconf=urlconf)

        if url.startswith('/admin/'):
            raise ImproperlyConfigured("Error with URL configuration: 'wagtailimages.urls' is being imported under '/admin/'. Use \"url(r'^images/', include(wagtailimages_urls))\" instead.")
    except urlresolvers.Resolver404:
        pass


@hooks.register('construct_main_menu')
def construct_main_menu(request, menu_items):
    if request.user.has_perm('wagtailimages.add_image'):
        menu_items.append(
            MenuItem(_('Images'), urlresolvers.reverse('wagtailimages_index'), classnames='icon icon-image', order=300)
        )

    # HACK: Sneak in check_url_pattens check
    # This will cause check_url_patterns to run on every hit to an admin page to make sure the developer gets the message
    check_url_patterns()

@hooks.register('insert_editor_js')
def editor_js():
    js_files = [
        'wagtailimages/js/hallo-plugins/hallo-wagtailimage.js',
        'wagtailimages/js/image-chooser.js',
    ]
    js_includes = format_html_join('\n', '<script src="{0}{1}"></script>',
        ((settings.STATIC_URL, filename) for filename in js_files)
    )
    return js_includes + format_html(
        """
        <script>
            window.chooserUrls.imageChooser = '{0}';
            registerHalloPlugin('hallowagtailimage');
        </script>
        """,
        urlresolvers.reverse('wagtailimages_chooser')
    )
