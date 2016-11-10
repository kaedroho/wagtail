import itertools
from bs4 import BeautifulSoup
import difflib

from django.utils.safestring import mark_safe


class FieldComparator:
    def __init__(self, model, field_name, obj_a, obj_b):
        self.model = model
        self.field_name = field_name
        self.obj_a = obj_a
        self.obj_b = obj_b

    def field_label(self):
        # TODO
        return self.field_name

    def values(self):
        return getattr(self.obj_a, self.field_name), getattr(self.obj_b, self.field_name)

    def htmldiff(self):
        return self.values()

    def has_changed(self):
        values = self.values()
        return values[0] != values[1]


class TextFieldComparator(FieldComparator):
    def htmldiff(self):
        def highlight(src, highlight):
            out = ""

            is_highlighting = False
            for c, h in itertools.zip_longest(src, highlight):
                do_highlight = h is not None and not h.isspace()

                if do_highlight and not is_highlighting:
                    out += "<span>"
                    is_highlighting = True

                if not do_highlight and is_highlighting:
                    out += "</span>"
                    is_highlighting = False

                if c:
                    out += c

            if is_highlighting:
                out += "</span>"

            return out

        values = self.values()
        a_lines = values[0].splitlines()
        b_lines = values[1].splitlines()
        diff = difflib.ndiff(a_lines, b_lines)

        a_changes = []
        b_changes = []

        iter = diff.__iter__()
        line = next(iter, None)
        while line:
            if line.startswith('- '):
                a_changes.append(("deletion", line[2:]))

                line = next(iter, None)
                if line and line.startswith('? '):
                    a_changes[-1] = (a_changes[-1][0], highlight(a_changes[-1][1], line[2:]))
                    line = next(iter, None)
                else:
                    a_changes[-1] = (a_changes[-1][0], highlight(a_changes[-1][1], '^' * len(a_changes[-1][1])))
                    b_changes.append(("", ""))

            elif line.startswith('+ '):
                b_changes.append(("addition", line[2:]))

                line = next(iter, None)
                if line and line.startswith('? '):
                    b_changes[-1] = (b_changes[-1][0], highlight(b_changes[-1][1], line[2:]))
                    line = next(iter, None)
                else:
                    b_changes[-1] = (b_changes[-1][0], highlight(b_changes[-1][1], '^' * len(b_changes[-1][1])))
                    a_changes.append(("", ""))

            else:
                a_changes.append(("", line))
                b_changes.append(("", line))
                line = next(iter, None)

        return [
            ((a[0], mark_safe(a[1])), (b[0], mark_safe(b[1])))
            for a, b in itertools.zip_longest(a_changes, b_changes, fillvalue=('', ''))
        ]


class RichTextFieldComparator(TextFieldComparator):
    def values(self):
        values = super().values()
        return BeautifulSoup(values[0]).getText('\n'), BeautifulSoup(values[1]).getText('\n')


class StreamFieldComparator(FieldComparator):
    pass


class InlineComparator:
    def __init__(self, model, relation_name, obj_a, obj_b):
        self.model = model
        self.relation_name = relation_name
        self.obj_a = obj_a
        self.obj_b = obj_b

    def has_changed(self):
        return False
