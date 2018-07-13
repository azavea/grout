# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0002_auto_20150421_1724'),
    ]

    operations = [
        migrations.RenameField(
            model_name='record',
            old_name='schema_id',
            new_name='schema',
        ),
    ]
