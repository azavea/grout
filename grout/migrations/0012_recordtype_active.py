# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0011_auto_20150505_1941'),
    ]

    operations = [
        migrations.AddField(
            model_name='recordtype',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
