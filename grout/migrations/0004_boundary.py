# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.contrib.postgres.fields import JSONField
import uuid
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0003_auto_20150422_1310'),
    ]

    operations = [
        migrations.CreateModel(
            name='Boundary',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default=b'pen', max_length=10, choices=[(b'pen', b'Pending'), (b'pro', b'Processing'), (b'war', b'Warning'), (b'err', b'Error'), (b'com', b'Complete')])),
                ('label', models.CharField(max_length=64)),
                ('errors', JSONField(null=True, blank=True)),
                ('source_file', models.FileField(upload_to=b'boundaries/%Y/%m/%d')),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
