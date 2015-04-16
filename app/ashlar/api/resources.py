from flask_restful import Resource

from ashlar import db
from ashlar.ashlar.models import ItemSchema, RecordSchema

from api import status

class RecordSchemaView(Resource):

    def get(self, id):
        return { 'id': id }, status.HTTP_200_OK


class RecordSchemaListView(Resource):

    def get(self):
        return [], status.HTTP_200_OK


class ItemSchemaView(Resource):

    def get(self, id):
        return { 'id': id }, status.HTTP_200_OK


class ItemSchemaListView(Resource):

    def get(self):
        return [], status.HTTP_200_OK

