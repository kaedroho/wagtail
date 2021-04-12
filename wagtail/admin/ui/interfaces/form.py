from .template import TemplateInterface


class FormInterface(TemplateInterface):
    template_name = 'wagtailadmin/interfaces/form.html'

    def __init__(self, form):
        self.form = form

    def get_context(self, request):
        return {
            'form': form
        }


class EditHandlerInterface(TemplateInterface):
    template_name = 'wagtailadmin/interfaces/edit_handler.html'

    def __init__(self, edit_handler):
        self.edit_handler = edit_handler

    def get_context(self, request):
        return {
            'edit_handler': edit_handler
        }
