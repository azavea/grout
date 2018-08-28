# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0010_auto_20150505_1940'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecordType',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('label', models.CharField(max_length=64)),
                ('plural_label', models.CharField(max_length=64)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        # NOTE: makemigrations attempted this operation as an AlterField, but text cannot be
        #       converted to fk via AlterField. So, it was replaced with a
        #       RemoveField + AddField operation. Note that we also need to manually remove the
        #       unique constraint on record_type, then re-add it.
        migrations.AlterUniqueTogether(
            name='recordschema',
            unique_together=set([('version',)]),
        ),
        migrations.RemoveField(
            model_name='recordschema',
            name='record_type',
        ),
        migrations.AddField(
            model_name='recordschema',
            name='record_type',
            field=models.ForeignKey(related_name='schemas', to='grout.RecordType', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='recordschema',
            unique_together=set([('record_type', 'version')]),
        ),
    ]
