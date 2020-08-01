from collections import defaultdict

from django.utils.translation import gettext_lazy as _

from wagtail.core import hooks


class LogActionRegistry:
    """
    A central store for log actions.
    The expected format for registered log actions: Namespaced action, Action label, Action message (or callable)
    """
    def __init__(self, hook_name):
        self.hook_name = hook_name

        # Has the hook been run for this registry?
        self.has_scanned_for_actions = False

        # Holds the actions.
        self.actions = {}

        # Holds a list of action, action label tuples for use in filters
        self.choices = []

        # Holds the action messsages, keyed by action
        self.messages = {}

        # Holds a mapping of actions to their parents, if the action has specified one.
        self.parents = {}

        # Like parents, but includes all ancestors for efficient lookup
        self.ancestors = defaultdict(set)

    def scan_for_actions(self):
        if not self.has_scanned_for_actions:
            for fn in hooks.get_hooks(self.hook_name):
                fn(self)

            self.has_scanned_for_actions = True

        return self.actions

    def get_actions(self):
        return self.scan_for_actions()

    def get_all_variants(self, action):
        """
        Returns all variants of an action, following the value passed in to the `parent` parameter on `register_action`.

        For example, say we have the following actions:

            register_action('wagtail.create')
            # wagtail.copy also counts as a wagtail.create
            register_action('wagtail.copy', parent='wagtail.create')
            register_action('wagtail.edit')

        When you call .get_all_variants on 'wagtail.create' you will recieve a list containing both 'wagtail.create' and
        'wagtail.copy'.

        This is useful for finding all logs that created a page, which should include creations, copies, and imports.
        """
        return [
            variant for variant in self.actions if action in self.ancestors[variant]
        ]

    def tree(self, action=None):
        """
        Returns a full tree of all the actions base, following the value passed in to the `parent` parameter on `register_action`.

        For example, say we have the following actions:

            register_action('wagtail.create')
            # wagtail.copy also counts as a wagtail.create
            register_action('wagtail.copy', parent='wagtail.create')
            register_action('wagtail.edit')

        This returns the following:

            [
                {
                    'action': 'wagtail.create',
                    'children': [
                        {
                            'action': 'wagtail.copy',
                            'children': []
                        }
                    ]
                },
                {
                    'action': 'wagtail.edit',
                    'children': []
                },
            ]
        """
        if action:
            return {
                'action': action,
                'children': [
                    self.tree(variant) for variant in self.actions if self.parents.get(variant) == action
                ]
            }
        else:
            # Return actions without parents
            return [
                self.tree(action) for action in self.actions if action not in self.parents
            ]

    def register_action(self, action, label, message, parent=None):
        self.actions[action] = (label, message)
        self.messages[action] = message
        self.choices.append((action, label))

        if parent is not None:
            self.parents[action] = parent
            self.ancestors[action].add(parent)
            if self.ancestors[parent]:
                self.ancestors[action].update(self.ancestors[parent])

    def get_choices(self):
        self.scan_for_actions()
        return self.choices

    def get_messages(self):
        self.scan_for_actions()
        return self.messages

    def format_message(self, log_entry):
        message = self.get_messages().get(log_entry.action, _('Unknown {action}').format(action=log_entry.action))
        if callable(message):
            message = message(log_entry.data)

        return message

    def get_action_label(self, action):
        return self.get_actions()[action][0]


# For historical reasons, pages use the 'register_log_actions' hook
page_log_action_registry = LogActionRegistry('register_log_actions')
