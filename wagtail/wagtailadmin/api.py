from wagtail.contrib.api2.router import WagtailAPIRouter
from wagtail.contrib.api2.endpoints import PagesAPIEndpoint, ImagesAPIEndpoint, DocumentsAPIEndpoint


class PagesAdminAPIEndpoint(PagesAPIEndpoint):
    pass


class ImagesAdminAPIEndpoint(ImagesAPIEndpoint):
    pass


class DocumentsAdminAPIEndpoint(DocumentsAPIEndpoint):
    pass


admin_api = WagtailAPIRouter('wagtailadmin_api')
admin_api.register_endpoint('pages', PagesAdminAPIEndpoint)
admin_api.register_endpoint('images', ImagesAdminAPIEndpoint)
admin_api.register_endpoint('documents', DocumentsAdminAPIEndpoint)
