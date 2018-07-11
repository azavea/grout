# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django.db import models, migrations
from grout.models import RecordSchema, Record


class Migration(migrations.Migration):

    dependencies = [
        ('grout', '0001_initial'),
    ]

    create_gin_index_sql = 'CREATE INDEX {index_name} ON {table} USING gin({column})'
    drop_gin_index_sql = 'DROP INDEX IF EXISTS {index_name}'

    def _get_field_db_column(cls, fieldname):
        """Returns the name of the database column corresponding to a field on a Django Model

        :param cls: Subjclass of django.db.models.Model
        :param fieldname: Name of a field on cls
        :returns: String with database column name corresponding to fieldname
        """
        # Both of these get_* functions return tuples of information; the
        # numbers are just the indexes of the information we want, which is a
        # Field instance and the db column name, respectively.
        if django.VERSION <= (1, 8):
            return cls._meta.get_field_by_name(fieldname)[0].get_attname_column()[1]
        else:
            return cls._meta.get_field(fieldname).get_attname_column()[1]

    operations = [
        # Records
        migrations.RunSQL(create_gin_index_sql.format(index_name='grout_record_data_gin',
                                                      table=Record._meta.db_table,
                                                      column=_get_field_db_column(Record, 'data')),
                          drop_gin_index_sql.format(index_name='grout_record_data_gin')),
        # RecordSchema
        migrations.RunSQL(create_gin_index_sql.format(index_name='grout_recordschema_schema_gin',
                                                      table=RecordSchema._meta.db_table,
                                                      column=_get_field_db_column(RecordSchema, 'schema')),
                          drop_gin_index_sql.format(index_name='grout_recordschema_schema_gin')),
    ]
