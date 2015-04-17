from __future__ import absolute_import

from flask import Blueprint
from flask.ext.restless import APIManager

from ashlar import app, db
from ashlar.ashlar.exceptions import SchemaException
from ashlar.ashlar.models import Record, RecordSchema, ItemSchema


api_manager = APIManager(app, session=db.session)

## TODO: Figure out how to properly serialize the geo column
# If exclude_columns=['geo'] is removed, the json serializer will throw
# a TypeError('Boolean value...is not defined'). This is because when we get to the json
# serialization, the geo key still contains a geoalchemy2.elements.WKBElement.
#
# Fixes I attempted:
#   - subclassing geoalchemy2.types.Geometry to return ST_AsText in its bind_expression method
#       Did not appear to work, the geom remained a WKBElement in the dict representation of the
#       sqlalchemy instance.
#       http://docs.sqlalchemy.org/en/rel_0_9/core/custom_types.html#applying-sql-level-bind-result-processing
#   - Calling str(on the WKBElement): This gives the binary representation, useless to us
#   - Investigate a way to override flask_restless.helpers.to_dict
#       This is trouble because we need a session to call ST_AsText on the WKBElement and we don't
#       have one in the to_dict method.
# Other potential alternatives:
#   - Since there is only a single point column, forego geoalchemy entirely, and write our own
#       Geometry field with the necessary methods/filters that returns text rather than binary
#       Example:
#           https://github.com/zzzeek/sqlalchemy/blob/c5edbc6fdc611d3c812735d83fe056fbb7d113f5/examples/postgis/postgis.py
#   - Forego flask_restless entirely, and build the get/post/put/delete via some other library, like flask_restful
#       In that case, we would have to write more boilerplate and json serialization ourselves
record_bp = api_manager.create_api_blueprint(Record,
                                             collection_name='record',
                                             exclude_columns=['geo'],
                                             methods=['GET', 'POST', 'PUT', 'DELETE'])

item_schema_bp = api_manager.create_api_blueprint(ItemSchema,
                                                  collection_name='itemschema',
                                                  validation_exceptions=[SchemaException],
                                                  methods=['GET', 'POST'])
record_schema_bp = api_manager.create_api_blueprint(RecordSchema,
                                                    collection_name='recordschema',
                                                    validation_exceptions=[SchemaException],
                                                    methods=['GET', 'POST'])
