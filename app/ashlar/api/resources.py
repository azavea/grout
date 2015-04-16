from flask_restful import Resource, inputs, reqparse

from sqlalchemy.exc import SQLAlchemyError

from ashlar import db
from ashlar.ashlar.models import ItemSchema, RecordSchema

from api import status

def post_request_helper(db_object):
    try:
        db.session.add(db_object)
        db.session.commit()
        return db_object.to_dict(), status.HTTP_201_CREATED
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'message': e.message
        }, status.HTTP_400_BADREQUEST


class AshlarView(Resource):

    def __init__(self):
        super(AshlarView, self).__init__()
        self.parser = reqparse.RequestParser()
        #self.parser.add_argument('id', type=int, required=True)


class SchemaView(AshlarView):

    def __init__(self):
        super(SchemaView, self).__init__()
        self.parser.add_argument('version', type=inputs.positive, required=True)
        self.parser.add_argument('schema', type=str, required=True)

class RecordSchemaView(Resource):

    def get(self, id):
        record_schema = db.session.query(RecordSchema).get(id)
        if record_schema:
            return record_schema.to_dict(), status.HTTP_200_OK
        else:
            return {
                'message': 'Object does not exist'
            }, status.HTTP_404_NOTFOUND


class RecordSchemaListView(SchemaView):

    def __init__(self):
        super(RecordSchemaListView, self).__init__()
        self.parser.add_argument('record_type', type=str, required=True)

    def get(self):
        return [], status.HTTP_200_OK

    def post(self):
        args = self.parser.parse_args()
        ## Validate json here, shoudl be able to do it via a custom parser format
        record_schema = RecordSchema(**args)
        return post_request_helper(record_schema)


class ItemSchemaView(Resource):

    def get(self, id):
        item_schema = db.session.query(ItemSchema).get(id)
        if item_schema:
            return item_schema.to_dict(), status.HTTP_200_OK
        else:
            return {
                'message': 'Object does not exist'
            }, status.HTTP_404_NOTFOUND


class ItemSchemaListView(Resource):

    def get(self):
        return [], status.HTTP_200_OK

