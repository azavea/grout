# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0013_auto_20150514_1712'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='record',
            options={'ordering': ('-created',)},
        ),
        migrations.RemoveField(
            model_name='record',
            name='label',
        ),
        migrations.RemoveField(
            model_name='record',
            name='slug',
        ),
    ]
