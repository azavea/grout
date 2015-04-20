# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    json_data_forward_sql = 'CREATE INDEX record_json_data_gin ON jsonbtest_record USING gin(json_data)'
    json_data_backward_sql = 'DROP INDEX IF EXISTS record_json_data_gin'

    schema_forward_sql = 'CREATE INDEX recordschema_schema_gin ON jsonbtest_recordschema USING gin(schema)'
    schema_backward_sql = 'DROP INDEX IF EXISTS recordschema_schema_gin'

    operations = [
        migrations.RunSQL(json_data_forward_sql, json_data_backward_sql),
        migrations.RunSQL(schema_forward_sql, schema_backward_sql),
    ]
