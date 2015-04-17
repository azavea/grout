from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Column, create_engine, inspect
from sqlalchemy.types import Integer, String, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import func, UniqueConstraint
from sqlalchemy.schema import Index
from sqlalchemy.orm import validates

from geoalchemy2.types import Geometry

import jsonschema
from jsonschema.exceptions import SchemaError, ValidationError

#from geometries import Point
from exceptions import SchemaException


BaseModel = declarative_base()


class AshlarModel(BaseModel):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created = Column(DateTime(timezone=True), nullable=False, default=func.now())
    modified = Column(DateTime(timezone=True), nullable=False, server_onupdate=func.now(), default=func.now())


class SchemaModel(AshlarModel):
    __abstract__ = True

    version = Column(Integer, nullable=False)
    schema = Column(JSONB)

    def validate_json(self, json_dict):
        """Validates a JSON-like dictionary against this object's schema

        :param json_dict: Python dict representing json to be validated against self.schema
        :return: None if validation succeeds; jsonschema.exceptions.ValidationError if failure
                 (or jsonschema.exceptions.SchemaError if the schema is invalid)
        """
        return jsonschema.validate(json_dict, self.schema)

    @validates('schema')
    def validate_schema(self, key, schema):
        """Validates that this object's schema is a valid JSON-Schema schema
        :param key: Name of the field being validated
        :param schema: Python dict representing json schema that should be checked
        :return: None if schema validates; raises jsonschema.exceptions.SchemaError
            if schema is invalid
        """
        try:
            jsonschema.Draft4Validator.check_schema(schema)
        except (SchemaError, ValidationError) as error:
            raise SchemaException(error.message)
        return schema


class Record(AshlarModel):
    __tablename__ = 'records'

    occurred_from = Column(DateTime(timezone=True), nullable=False, default=func.now())
    occurred_to = Column(DateTime(timezone=True), nullable=False, default=func.now())
    label = Column(String(50), nullable=False)
    slug = Column(String(50), nullable=False)
    geo = Column(Geometry(geometry_type='POINT', srid=4326))
    schema_id = Column(Integer, ForeignKey('record_schemas.id'))
    json_data = Column(JSONB)

    __table_args__ = (Index('json_data_idx', 'json_data', postgresql_using='gin'),)


class RecordSchema(SchemaModel):
    __tablename__ = 'record_schemas'

    record_type = Column(String(50), nullable=False)

    __table_args__ = (Index('record_schema_idx', 'schema', postgresql_using='gin'),
                      UniqueConstraint('record_type', 'version', name='_record_version_uc'),)


class ItemSchema(SchemaModel):
    __tablename__ = 'object_schemas'

    label = Column(String(50), nullable=False)
    slug = Column(String(50), nullable=False, unique=True)

    __table_args__ = (Index('item_schema_idx', 'schema', postgresql_using='gin'),
                      UniqueConstraint('label', 'version', name='_item_version_uc'),)
