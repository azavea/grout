# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0015_record_nominatim'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='nominatim',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
