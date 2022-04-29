from dataclasses import dataclass

from wagtail.admin.forms.search import SearchForm

from .components import Component


class Header(Component):
    @dataclass
    class Button:
        text: str
        url: str
        icon_name: str = "plus"

    @dataclass
    class Search:
        action: str
        form: SearchForm

    title = ""
    subtitle = ""
    icon_name = ""
    search = None
    buttons = []

    template_name = "wagtailadmin/headers/header.html"

    def __init__(self, **kwargs):
        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_context_data(self, parent_context):
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "icon_name": self.icon_name,
            "search": self.search,
            "buttons": self.buttons,
        }
