# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('wagtailsearch', '0002_add_verbose_names'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='editorspick',
            name='page',
        ),
        migrations.RemoveField(
            model_name='editorspick',
            name='query',
        ),
        migrations.DeleteModel(
            name='EditorsPick',
        ),
    ]
