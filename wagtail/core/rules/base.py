from wagtail.core.models import Page, GroupPagePermission

class PageRule:
    verb = None
    action = None

    def test(self, user, page):
        """
        Returns True if this rule applies to the given user/page combination.
        """
        return self.get_queryset(user).filter(id=page.id).exists()

    def test_any(self, user, pages):
        """
        Returns True if this rule applies to any pages in the queryset for the given user.
        """
        return (self.get_queryset(user) & pages).exists()

    def get_queryset(self, user):
        """
        Returns a queryset of pages that this rule applies to for the given user.
        """
        return Page.objects.none()


class ClonedPageRule(PageRule):
    verb = None
    cloned_verb = None
    action = 'allow'

    def test(self, user, page):
        return test(self.cloned_verb, user, page)

    def test_any(self, user, pages):
        return test_any(self.cloned_verb, user, pages)

    def get_queryset(self, user):
        return get_queryset(self.cloned_verb, user)


class InheritedPageRule(PageRule):
    def test(self, user, page):
        return self.test_roots(user, page.get_ancestors(inclusive=True))

    def test_any(self, user, pages):
        all_ancestors = Page.objects.none()
        for page in pages:
            all_ancestors |= page.get_ancestors(inclusive=True)

        return self.test_roots(user, all_ancestors)

    def get_queryset(self, user):
        pages = Page.objects.none()

        for root in self.get_root_queryset(user):
            pages |= Page.objects.descendant_of(root, inclusive=True)

        return pages


class PagePermissionRule(InheritedPageRule):
    permission_type = None

    def test_roots(self, user, pages):
        return GroupPagePermission.objects.filter(group__user=user, page__in=pages, permission_type=self.permission_type).exists()

    def get_root_queryset(self, user):
        return Page.objects.filter(
            id__in=GroupPagePermission.objects.filter(group__user=user, permission_type=self.permission_type).values_list('page_id', flat=True)
        )


REGISTERED_RULES = {}

def register(rule_cls):
    if rule_cls.verb not in REGISTERED_RULES:
        REGISTERED_RULES[rule_cls.verb] = []

    REGISTERED_RULES[rule_cls.verb].append(rule_cls)


def test(verb, user, page):
    if not user.is_authenticated:
        return False

    rules = REGISTERED_RULES.get(verb, [])
    allowed = any(rule().test(user, page) for rule  in rules if rule.action == 'allow')
    disallowed = any(rule().test(user, page) for rule in rules if rule.action == 'disallow')

    return allowed and not disallowed


def test_any(verb, user, pages):
    if not user.is_authenticated:
        return False

    # TODO optimise
    return any(test(verb, user, page) for page in pages)


def get_queryset(verb, user):
    if not user.is_authenticated:
        return Page.objects.none()

    rules = REGISTERED_RULES.get(verb, [])

    allowed_pages = Page.objects.none()
    disallowed_pages = Page.objects.none()

    for rule in rules:
        rule_pages = rule().get_queryset(user).order_by()

        if rule.action == 'allow':
            allowed_pages |= rule_pages
        elif rule.action == 'disallow':
            disallowed_pages |= rule_pages

    return allowed_pages.exclude(id__in=disallowed_pages.values_list('id', flat=True))
