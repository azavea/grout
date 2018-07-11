# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0017_auto_20151020_1926'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='boundary',
            options={'ordering': ('display_field',)},
        ),
        migrations.AlterModelOptions(
            name='recordtype',
            options={'ordering': ('plural_label',)},
        ),
    ]
