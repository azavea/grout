# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0009_auto_20150429_1627'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='itemschema',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='itemschema',
            name='next_version',
        ),
        migrations.DeleteModel(
            name='ItemSchema',
        ),
    ]
