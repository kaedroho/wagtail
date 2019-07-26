import json

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

# The edit_handlers module extends Page with some additional attributes required by
# wagtailadmin (namely, base_form_class and get_edit_handler). Importing this within
# wagtailadmin.models ensures that this happens in advance of running wagtailadmin's
# system checks.
from wagtail.admin import edit_handlers  # NOQA


class PageActionLogEntry(models.Model):
    action_type = models.CharField(max_length=255, blank=True, db_index=True)
    data_json = models.TextField(blank=True)
    time = models.DateTimeField()

    page_title = models.TextField()
    page = models.ForeignKey(
        'wagtailcore.Page',
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        related_name='action_log_entries',
    )

    revision = models.ForeignKey(
        'wagtailcore.PageRevision',
        null=True,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        related_name='+',
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,  # Null if actioned by system
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        related_name='+',
    )

    # These flags provide additional context to the 'action' made
    # by the user (or system).
    created = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    unpublished = models.BooleanField(default=False)
    content_changed = models.BooleanField(default=False, db_index=True)
    deleted = models.BooleanField(default=False)

    @cached_property
    def username(self):
        if self.user_id:
            try:
                return self.user.username
            except (self._meta.get_field('user').related_model.DoesNotExist):
                # User has been deleted
                return _('user {id} (deleted)').format(id=self.user_id)
        else:
            return _('system')

    @cached_property
    def data(self):
        if self.data_json:
            return json.loads(self.data_json)
        else:
            return {}
