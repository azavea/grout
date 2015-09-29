# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ashlar', '0013_auto_20150514_1712'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='record',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterField(
            model_name='boundarypolygon',
            name='geom',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326),
        ),
        migrations.AlterField(
            model_name='record',
            name='geom',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326),
        ),
    ]
