from __future__ import absolute_import

from flask import Blueprint
from flask_restful import Api

from ashlar import app
from api.resources import (RecordSchemaView,
                           RecordSchemaListView,
                           ItemSchemaView,
                           ItemSchemaListView)


API_CONFIG = app.config['ASHLAR_API']

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)

api.add_resource(RecordSchemaListView, API_CONFIG['PREFIX'] + '/schema/record')
api.add_resource(RecordSchemaView, API_CONFIG['PREFIX'] + '/schema/record/<int:id>')

api.add_resource(ItemSchemaListView, API_CONFIG['PREFIX'] + '/schema/item')
api.add_resource(ItemSchemaView, API_CONFIG['PREFIX'] + '/schema/item/<int:id>')
