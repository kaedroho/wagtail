class TemplateInterface:
    def __init__(self, template_name, context):
        self.template_name = template_name
        self.context = context

    def get_context(self, request):
        return self.context

    def render(self, request):
        return render_to_string(self.template_name, self.get_context(request), request=request)


class TemplateInterfaceAdapter(Adapter):
    # A component on the frontend that displays the HTML
    js_constructor = 'wagtail.components.HTML'

    def js_args(self, request, interface):
        return [
            interface.render(request)
        ]


register(TemplateInterfaceAdapter(), TemplateInterface)
