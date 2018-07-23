# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0006_auto_20150424_1857'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemschema',
            name='next_version',
            field=models.OneToOneField(related_name='previous_version', null=True, to='grout.ItemSchema', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='recordschema',
            name='next_version',
            field=models.OneToOneField(related_name='previous_version', null=True, to='grout.RecordSchema', on_delete=models.CASCADE),
        ),
    ]
