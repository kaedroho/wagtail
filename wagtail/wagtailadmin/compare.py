import itertools
from bs4 import BeautifulSoup
import difflib

from django.utils.safestring import mark_safe
from django.utils.text import capfirst


class FieldComparison:
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


class TextFieldComparison(FieldComparison):
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


class RichTextFieldComparison(TextFieldComparison):
    def values(self):
        values = super().values()
        return BeautifulSoup(values[0]).getText('\n'), BeautifulSoup(values[1]).getText('\n')


class StreamFieldComparison(FieldComparison):
    pass


class InlineComparison(FieldComparison):
    def get_mapping(self, objs_a, objs_b):
        map_forwards = {}
        map_backwards = {}
        new = []
        deleted = []

        # Match child objects on ID
        for a_idx, a_child in enumerate(objs_a):
            for b_idx, b_child in enumerate(objs_b):
                if b_idx in map_backwards:
                    continue

                if a_child.id == b_child.id:
                    map_forwards[a_idx] = b_idx
                    map_backwards[b_idx] = a_idx

        # TODO now try to match them by data

        # Mark unmapped objects as new/deleted
        for a_idx, a_child in enumerate(objs_a):
            if a_idx not in map_forwards:
                deleted.append(a_idx)

        for b_idx, b_child in enumerate(objs_b):
            if b_idx not in map_backwards:
                new.append(b_idx)

        return map_forwards, map_backwards, new, deleted

    def htmldiff(self):
        values = self.values()
        objs_a = list(values[0].all())
        objs_b = list(values[1].all())

        map_forwards, map_backwards, new, deleted = self.get_mapping(objs_a, objs_b)
        objs_a = dict(enumerate(objs_a))
        objs_b = dict(enumerate(objs_b))

        a_changes = []
        b_changes = []

        for a_idx, a_child in objs_a.items():
            if a_idx in deleted:
                a_changes.append(("deletion", self.display_inline_object(a_child, "deleted", {})))
            else:
                differences = compare_objects(a_child, objs_b[map_forwards[a_idx]], exclude_fields=['id', 'page', 'sort_order'])

                if differences:
                    a_changes.append(("change", self.display_inline_object(a_child, "changed", differences)))
                else:
                    a_changes.append(("", self.display_inline_object(a_child, "nochange", {})))

        for b_idx, b_child in objs_b.items():
            if b_idx in new:
                b_changes.append(("addition", self.display_inline_object(b_child, "new", {})))
            else:
                differences = compare_objects(b_child, objs_a[map_backwards[b_idx]], exclude_fields=['id', 'page', 'sort_order'])

                if differences:
                    b_changes.append(("change", self.display_inline_object(b_child, "changed", differences)))
                else:
                    b_changes.append(("", self.display_inline_object(b_child, "nochange", {})))

        return [
            ((a[0], mark_safe(a[1])), (b[0], mark_safe(b[1])))
            for a, b in itertools.zip_longest(a_changes, b_changes, fillvalue=('', ''))
        ]

    def display_inline_object(self, obj, mode, differences):
        model = type(obj)

        if mode == "nochange":
            field_data = []
            for field in model._meta.get_fields():
                if field.name in ['id', 'page', 'sort_order']:
                    continue
                value = field.value_to_string(obj)
                field_data.append((capfirst(field.verbose_name), value))

            return '<br/>'.join([
                "{}: {}".format(name, value)
                for name, value in field_data
            ])
        elif mode == "changed":
            field_data = []
            for field in model._meta.get_fields():
                if field.name in ['id', 'page', 'sort_order']:
                    continue

                value = field.value_to_string(obj)

                if field.name in differences:
                    value = mark_safe("<span>%s</span>" % value)

                field_data.append((capfirst(field.verbose_name), value))

            return '<br/>'.join([
                "{}: {}".format(name, value)
                for name, value in field_data
            ])
        elif mode == "deleted":
            field_data = []
            for field in model._meta.get_fields():
                if field.name in ['id', 'page', 'sort_order']:
                    continue
                value = field.value_to_string(obj)
                field_data.append((capfirst(field.verbose_name), value))

            return '<br/>'.join([
                "{}: {}".format(name, value)
                for name, value in field_data
            ])
        elif mode == "new":
            field_data = []
            for field in model._meta.get_fields():
                if field.name in ['id', 'page', 'sort_order']:
                    continue
                value = field.value_to_string(obj)
                field_data.append((capfirst(field.verbose_name), value))

            return '<br/>'.join([
                "{}: {}".format(name, value)
                for name, value in field_data
            ])
        else:
            return "ERROR"

    def has_changed(self):
        values = self.values()
        objs_a = list(values[0].all())
        objs_b = list(values[1].all())

        map_forwards, map_backwards, new, deleted = self.get_mapping(objs_a, objs_b)

        if new or deleted:
            return True

        for a_idx, b_idx in map_forwards.items():
            if a_idx != b_idx:
                # A child object was reordered
                return True

            if compare_objects(objs_a[a_idx], objs_b[b_idx], exclude_fields=['id', 'page', 'sort_order']):
                return True

        return False


def compare_objects(obj_a, obj_b, include_fields=None, exclude_fields=None):
    assert(type(obj_a) is type(obj_b))
    model = type(obj_a)

    if include_fields:
        fields = include_fields.copy()
    else:
        fields = [f.name for f in model._meta.get_fields()]

    if exclude_fields is not None:
        for excl in exclude_fields:
            fields.remove(excl)

    differences = {}

    for field_name in fields:
        field = model._meta.get_field(field_name)

        val_a = field.value_to_string(obj_a)
        val_b = field.value_to_string(obj_b)

        if val_a != val_b:
            differences[field_name] = (val_a, val_b)

    return differences
