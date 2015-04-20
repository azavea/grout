# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields
import django.contrib.gis.db.models.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Record',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('label', models.CharField(max_length=64)),
                ('geometry', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('json_data', django_pgjson.fields.JsonBField()),
            ],
        ),
        migrations.CreateModel(
            name='RecordSchema',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('version', models.IntegerField()),
                ('label', models.CharField(max_length=64)),
                ('schema', django_pgjson.fields.JsonBField()),
            ],
        ),
        migrations.AddField(
            model_name='record',
            name='schema',
            field=models.ForeignKey(to='app.RecordSchema'),
        ),
    ]
