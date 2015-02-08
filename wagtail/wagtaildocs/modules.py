from django.conf.urls import url

from wagtail.wagtaildocs.views import documents, chooser
from wagtail.wagtailadmin.modules.base import Module


class DocumentModelModule(Module):
    app_name = 'wagtaildocs'

    def get_urls(self):
        index_view = documents.index
        create_view = documents.add
        update_view = documents.edit
        delete_view = documents.delete
        usage_view = documents.usage

        chooser_view = chooser.chooser
        chooser_chosen_view = chooser.document_chosen
        chooser_upload_view = chooser.chooser_upload

        return (
            url(r'^$', index_view, name='index'),
            url(r'^add/$', create_view, name='create'),
            url(r'^(\d+)/$', update_view, name='update'),
            url(r'^(\d+)/delete/$', delete_view, name='delete'),
            url(r'^usage/(\d+)/$', usage_view, name='usage'),

            url(r'^chooser/$', chooser_view, name='chooser'),
            url(r'^chooser/(\d+)/$', chooser_chosen_view, name='chooser_chosen'),
            url(r'^chooser/upload/$', chooser_upload_view, name='chooser_upload'),
        )

