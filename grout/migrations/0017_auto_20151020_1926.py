# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0016_auto_20151016_1951'),
    ]

    operations = [
        migrations.RenameField(
            model_name='record',
            old_name='nominatim',
            new_name='location_text',
        ),
    ]
