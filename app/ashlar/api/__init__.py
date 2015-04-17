from __future__ import absolute_import

from flask import Blueprint
from flask.ext.restless import APIManager

from ashlar import app, db

from ashlar.ashlar.exceptions import SchemaException
from ashlar.ashlar.models import Record, RecordSchema, ItemSchema
from ashlar.api.serializers import (geom_preprocessor,
                                    geom_patch_preprocessor,
                                    geom_postprocessor,
                                    geom_many_postprocessor)


api_manager = APIManager(app, session=db.session)

record_bp = api_manager.create_api_blueprint(Record,
                                             collection_name='record',
                                             preprocessors={
                                                'PUT_SINGLE': [geom_patch_preprocessor],
                                                'POST': [geom_preprocessor]
                                             },
                                             postprocessors={
                                                'GET_SINGLE': [geom_postprocessor],
                                                'GET_MANY': [geom_many_postprocessor],
                                                'PUT_SINGLE': [geom_postprocessor],
                                                'POST': [geom_postprocessor]
                                             },
                                             methods=['GET', 'POST', 'PUT', 'DELETE'])

item_schema_bp = api_manager.create_api_blueprint(ItemSchema,
                                                  collection_name='itemschema',
                                                  validation_exceptions=[SchemaException],
                                                  methods=['GET', 'POST'])
record_schema_bp = api_manager.create_api_blueprint(RecordSchema,
                                                    collection_name='recordschema',
                                                    validation_exceptions=[SchemaException],
                                                    methods=['GET', 'POST'])
