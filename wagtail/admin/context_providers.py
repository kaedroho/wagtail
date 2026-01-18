from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from wagtail.admin.menu import admin_menu
from wagtail.admin.search import admin_search_areas
from wagtail.admin.ui import sidebar


def sidebar_props(request):
    search_areas = admin_search_areas.search_items_for_request(request)
    if search_areas:
        search_area = search_areas[0]
    else:
        search_area = None

    account_menu = [
        sidebar.LinkMenuItem(
            "account", _("Account"), reverse("wagtailadmin_account"), icon_name="user"
        ),
        sidebar.ActionMenuItem(
            "logout", _("Log out"), reverse("wagtailadmin_logout"), icon_name="logout"
        ),
    ]

    modules = [
        sidebar.WagtailBrandingModule(),
        sidebar.SearchModule(search_area) if search_area else None,
        sidebar.MainMenuModule(
            admin_menu.render_component(request), account_menu, request.user
        ),
    ]
    return {
        "collapsed": not (request.COOKIES.get("wagtail_sidebar_collapsed", "0") == "0"),
        "modules": [module for module in modules if module is not None],
    }
