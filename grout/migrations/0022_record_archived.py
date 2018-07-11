# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0021_add_weather_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
