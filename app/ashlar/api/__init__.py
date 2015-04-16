from __future__ import absolute_import

from flask import Blueprint
from flask.ext.restless import APIManager
from flask_restful import Api

from ashlar import app, db
from ashlar.ashlar.models import RecordSchema, ItemSchema


API_CONFIG = app.config['ASHLAR_API']

api_manager = APIManager(app, session=db.session)

item_schema_bp = api_manager.create_api_blueprint(ItemSchema,
                                                  collection_name='itemschema',
                                                  methods=['GET', 'POST'])
record_schema_bp = api_manager.create_api_blueprint(RecordSchema,
                                                    collection_name='recordschema',
                                                    methods=['GET', 'POST'])
