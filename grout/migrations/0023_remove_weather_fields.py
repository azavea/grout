# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0022_record_archived'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='record',
            name='light',
        ),
        migrations.RemoveField(
            model_name='record',
            name='weather',
        ),
    ]
