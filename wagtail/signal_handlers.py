import logging

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save, pre_delete

from wagtail.admin.mail import (
    GroupApprovalTaskStateSubmissionEmailNotifier, WorkflowStateApprovalEmailNotifier,
    WorkflowStateRejectionEmailNotifier, WorkflowStateSubmissionEmailNotifier)
from wagtail.models import Page, Site, TaskState, WorkflowState
from wagtail.signals import (
    task_submitted, workflow_approved, workflow_rejected, workflow_submitted)


task_submission_email_notifier = GroupApprovalTaskStateSubmissionEmailNotifier()
workflow_submission_email_notifier = WorkflowStateSubmissionEmailNotifier()
workflow_approval_email_notifier = WorkflowStateApprovalEmailNotifier()
workflow_rejection_email_notifier = WorkflowStateRejectionEmailNotifier()


logger = logging.getLogger('wagtail')


# Clear the wagtail_site_root_paths from the cache whenever Site records are updated.
def post_save_site_signal_handler(instance, update_fields=None, **kwargs):
    cache.delete('wagtail_site_root_paths')


def post_delete_site_signal_handler(instance, **kwargs):
    cache.delete('wagtail_site_root_paths')


def pre_delete_page_unpublish(sender, instance, **kwargs):
    # Make sure pages are unpublished before deleting
    if instance.live:
        # Don't bother to save, this page is just about to be deleted!
        instance.unpublish(commit=False, log_action=None)


def post_delete_page_log_deletion(sender, instance, **kwargs):
    logger.info("Page deleted: \"%s\" id=%d", instance.title, instance.id)


def register_signal_handlers():
    post_save.connect(post_save_site_signal_handler, sender=Site)
    post_delete.connect(post_delete_site_signal_handler, sender=Site)

    pre_delete.connect(pre_delete_page_unpublish, sender=Page)
    post_delete.connect(post_delete_page_log_deletion, sender=Page)

    task_submitted.connect(task_submission_email_notifier, sender=TaskState, dispatch_uid='group_approval_task_submitted_email_notification')

    workflow_submitted.connect(workflow_submission_email_notifier, sender=WorkflowState, dispatch_uid='workflow_state_submitted_email_notification')
    workflow_rejected.connect(workflow_rejection_email_notifier, sender=WorkflowState, dispatch_uid='workflow_state_rejected_email_notification')
    workflow_approved.connect(workflow_approval_email_notifier, sender=WorkflowState, dispatch_uid='workflow_state_approved_email_notification')
