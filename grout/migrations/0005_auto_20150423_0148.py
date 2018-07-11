# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0004_boundary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boundary',
            name='status',
            field=models.CharField(default=b'PENDING', max_length=10, choices=[(b'PENDING', b'Pending'), (b'PROCESSING', b'Processing'), (b'WARNING', b'Warning'), (b'ERROR', b'Error'), (b'COMPLETE', b'Complete')]),
        ),
    ]
