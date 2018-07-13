# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0020_add_extra_nominatim_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='light',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='record',
            name='weather',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
