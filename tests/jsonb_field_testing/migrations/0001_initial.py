# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models, migrations
from django.contrib.postgres.fields import JSONField


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JsonBModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('data', JSONField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
