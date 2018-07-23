# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
from django.contrib.postgres.fields import JSONField
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ItemSchema',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('version', models.IntegerField()),
                ('schema', JSONField()),
                ('label', models.CharField(max_length=50)),
                ('slug', models.CharField(unique=True, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('occurred_from', models.DateTimeField()),
                ('occurred_to', models.DateTimeField()),
                ('label', models.CharField(max_length=50)),
                ('slug', models.CharField(max_length=50)),
                ('geom', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('data', JSONField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RecordSchema',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('version', models.IntegerField()),
                ('schema', JSONField()),
                ('record_type', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='recordschema',
            unique_together=set([('record_type', 'version')]),
        ),
        migrations.AddField(
            model_name='record',
            name='schema_id',
            field=models.ForeignKey(to='grout.RecordSchema', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='itemschema',
            unique_together=set([('slug', 'version')]),
        ),
    ]
