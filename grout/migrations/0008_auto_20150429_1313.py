# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0007_auto_20150427_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemschema',
            name='version',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='recordschema',
            name='version',
            field=models.PositiveIntegerField(),
        ),
    ]
