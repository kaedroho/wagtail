from wagtail.core.models import Page, WorkflowState

from .base import PageRule, PagePermissionRule, register


@register
class SuperusersCanEditEverything(PageRule):
    verb = 'edit'
    action = 'allow'

    def test(self, user, page):
        return user.is_superuser

    def get_queryset(self, user):
        if user.is_superuser:
            return Page.objects.all()
        else:
            return Page.objects.none()


@register
class InactiveUsersCantEditAnything(PageRule):
    verb = 'edit'
    action = 'disallow'

    def test(self, user, page):
        return not user.is_active

    def get_queryset(self, user):
        if user.is_active:
            return Page.objects.none()
        else:
            return Page.objects.all()


@register
class NobodyCanEditRoot(PageRule):
    verb = 'edit'
    action = 'disallow'

    def test(self, user, page):
        return page.is_root()

    def get_queryset(self, user):
        return Page.get_root_nodes()


@register
class OwnersCanEditTheirPages(PagePermissionRule):
    verb = 'edit'
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
    verb = 'edit'
    permission_type = 'edit'
    action = 'allow'


@register
class PagesInWorkflowsCanOnlyBeEditedByReviewers(PageRule):
    verb = 'edit'
    action = 'disallow'

    def test(self, user, page):
        if page.current_workflow_state:
            task = page.current_workflow_state.current_task_state.task
            if (
                page.current_workflow_state.status != WorkflowState.STATUS_NEEDS_CHANGES
                and task.specific.page_locked_for_user(page, user)
            ):
                return True

        return False

    def get_queryset(self, user):
        disallowed_page_ids = []
        for workflow in WorkflowState.objects.active().exclude(status=WorkflowState.STATUS_NEEDS_CHANGES):
            task = workflow.current_task_state.task
            if task.specific.page_locked_for_user(workflow.page, user):
                disallowed_page_ids.append(workflow.page_id)

        if disallowed_page_ids:
            return Page.objects.filter(id__in=disallowed_page_ids)
        else:
            return Page.objects.none()
