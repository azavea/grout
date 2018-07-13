# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0012_recordtype_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boundary',
            name='label',
            field=models.CharField(unique=True, max_length=128, validators=[django.core.validators.MinLengthValidator(3)]),
        ),
    ]
