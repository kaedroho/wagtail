from django.conf.urls import include, url

from wagtail.wagtaildocs.modules import DocumentModelModule

urlpatterns = [
    url(r'documents/', include(DocumentModelModule('wagtaildocs').urls)),
]
