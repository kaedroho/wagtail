from __future__ import absolute_import, unicode_literals

from .views import SiteViewSet


urlpatterns = SiteViewSet('wagtailsites').get_urlpatterns()
