# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0010_change_page_owner_to_null_on_delete'),
        ('wagtailredirects', '0001_initial'),
        ('wagtailforms', '0001_initial'),
        ('wagtailsearch', '0001_initial'),
        ('tests', '0008_registerdecorator'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='routablepagetest',
            name='page_ptr',
        ),
        migrations.DeleteModel(
            name='RoutablePageTest',
        ),
    ]
