# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0006_add_verbose_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='file_sha',
            field=models.CharField(max_length=40, editable=False, default=''),
        ),
    ]
