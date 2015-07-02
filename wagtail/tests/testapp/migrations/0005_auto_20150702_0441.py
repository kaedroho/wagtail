# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0004_streammodel_richtext'),
    ]

    operations = [
        migrations.AddField(
            model_name='customimagewithadminformfields',
            name='file_sha',
            field=models.CharField(max_length=40, editable=False, default=''),
        ),
        migrations.AddField(
            model_name='customimagewithoutadminformfields',
            name='file_sha',
            field=models.CharField(max_length=40, editable=False, default=''),
        ),
    ]
