# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.contrib.postgres.fields import JSONField
import uuid
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0005_auto_20150423_0148'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoundaryPolygon',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('data', JSONField()),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='boundary',
            name='geom',
        ),
        migrations.AddField(
            model_name='boundary',
            name='color',
            field=models.CharField(default=b'blue', max_length=64),
        ),
        migrations.AddField(
            model_name='boundary',
            name='data_fields',
            field=JSONField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='boundary',
            name='display_field',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='boundarypolygon',
            name='boundary',
            field=models.ForeignKey(related_name='polygons', to='grout.Boundary', null=True, on_delete=models.CASCADE),
        ),
    ]
