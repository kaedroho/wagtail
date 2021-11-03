from wagtail.core.models import Page

from .base import PageRule, PagePermissionRule, register


@register
class SuperusersCanViewEverything(PageRule):
    verb = 'view'
    action = 'allow'

    def test(self, user, page):
        return user.is_superuser

    def get_queryset(self, user):
        if user.is_superuser:
            return Page.objects.all()
        else:
            return Page.objects.none()


@register
class InactiveUsersCantViewAnything(PageRule):
    verb = 'view'
    action = 'disallow'

    def test(self, user, page):
        return not user.is_active

    def get_queryset(self, user):
        if user.is_active:
            return Page.objects.none()
        else:
            return Page.objects.all()


@register
class NobodyCanViewRoot(PageRule):
    verb = 'view'
    action = 'disallow'

    def test(self, user, page):
        return page.is_root()

    def get_queryset(self, user):
        return Page.get_root_nodes()


@register
class OwnersCanViewTheirPages(PagePermissionRule):
    verb = 'view'
    permission_type = 'add'
    action = 'allow'

    def test(self, user, page):
        if not super().test(user, page):
            return False

        return page.owner_id == user.pk

    def get_queryset(self, user):
        pages_with_add_permission = super().get_queryset(user)
        return pages_with_add_permission.filter(owner=user)


@register
class EditPermission(PagePermissionRule):
    verb = 'view'
    permission_type = 'edit'
    action = 'allow'
