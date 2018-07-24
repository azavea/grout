# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0008_auto_20150429_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemschema',
            name='next_version',
            field=models.OneToOneField(related_name='previous_version', null=True, editable=False, to='grout.ItemSchema', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='recordschema',
            name='next_version',
            field=models.OneToOneField(related_name='previous_version', null=True, editable=False, to='grout.RecordSchema', on_delete=models.CASCADE),
        ),
    ]
