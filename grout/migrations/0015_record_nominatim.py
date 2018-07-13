# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0014_auto_20150910_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='nominatim',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
