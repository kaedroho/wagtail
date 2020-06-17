from django import forms
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from wagtail.admin import widgets
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, ObjectList
from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.admin.widgets.workflows import AdminTaskChooser
from wagtail.core.models import Page, Workflow, WorkflowPage


class WorkflowPageForm(forms.ModelForm):
    page = forms.ModelChoiceField(
        queryset=Page.objects.all(),
        widget=widgets.AdminPageChooser(
            target_models=[Page],
            can_choose_root=True
        )
    )

    class Meta:
        model = WorkflowPage
        fields = ['page']

    def clean(self):
        page = self.cleaned_data.get('page')
        try:
            existing_workflow = page.workflowpage.workflow
            if not self.errors and existing_workflow != self.cleaned_data['workflow']:
                # If the form has no errors, Page has an existing Workflow assigned, that Workflow is not
                # the selected Workflow, and overwrite_existing is not True, add a new error. This should be used to
                # trigger the confirmation message in the view. This is why this error is only added if there are no
                # other errors - confirmation should be the final step.
                self.add_error('page', ValidationError(_("This page already has workflow '{0}' assigned.").format(existing_workflow), code='existing_workflow'))
        except AttributeError:
            pass

    def save(self, commit=False):
        page = self.cleaned_data['page']

        if commit:
            WorkflowPage.objects.update_or_create(
                page=page,
                defaults={'workflow': self.cleaned_data['workflow']},
            )


class BaseWorkflowPagesFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for form in self.forms:
            form.fields['DELETE'].widget = forms.HiddenInput()

    @property
    def empty_form(self):
        empty_form = super().empty_form
        empty_form.fields['DELETE'].widget = forms.HiddenInput()
        return empty_form

    def clean(self):
        """Checks that no two forms refer to the same page object"""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        pages = [
            form.cleaned_data['page']
            for form in self.forms
            # need to check for presence of 'page' in cleaned_data,
            # because a completely blank form passes validation
            if form not in self.deleted_forms and 'page' in form.cleaned_data
        ]
        if len(set(pages)) != len(pages):
            # pages list contains duplicates
            raise forms.ValidationError(_("You cannot assign this workflow to the same page multiple times."))


WorkflowPagesFormSet = forms.inlineformset_factory(
    Workflow, WorkflowPage, form=WorkflowPageForm, formset=BaseWorkflowPagesFormSet, extra=1, can_delete=True, fields=['page']
)


class BaseTaskForm(forms.ModelForm):
    pass


def get_task_form_class(task_model, for_edit=False):
    """
    Generates a form class for the given task model.

    If the form is to edit an existing task, set for_edit to True. This applies
    the readonly restrictions on fields defined in admin_form_readonly_on_edit_fields.
    """
    fields = task_model.admin_form_fields

    form_class = forms.modelform_factory(
        task_model,
        form=BaseTaskForm,
        fields=fields,
        widgets=getattr(task_model, 'admin_form_widgets', {})
    )

    if for_edit:
        for field_name in getattr(task_model, 'admin_form_readonly_on_edit_fields', []):
            if field_name not in form_class.base_fields:
                raise ImproperlyConfigured(
                    "`%s.admin_form_readonly_on_edit_fields` contains the field "
                    "'%s' but this field doesn't exist. Have you forgotten to add "
                    "it to `%s.admin_form_fields`?"
                    % (task_model.__name__, field_name, task_model.__name__)
                )

            form_class.base_fields[field_name].disabled = True

    return form_class


def get_workflow_edit_handler():
    """
    Returns an edit handler which provides the "name" and "tasks" fields for workflow.
    """
    # Note. It's a bit of a hack that we use edit handlers here. Ideally, it should be
    # made easier to reuse the inline panel templates for any formset.
    # Since this form is internal, we're OK with this for now. We might want to revisit
    # this decision later if we decide to allow custom fields on Workflows.

    panels = [
        FieldPanel("name", heading=_("Give your workflow a name"), classname="full title"),
        InlinePanel("workflow_tasks", [
            FieldPanel('task', widget=AdminTaskChooser(show_clear_link=False)),
        ], heading=_("Add tasks to your workflow")),
    ]
    edit_handler = ObjectList(panels, base_form_class=WagtailAdminModelForm)
    return edit_handler.bind_to(model=Workflow)
