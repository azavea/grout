import json

from django.test import TestCase
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.exceptions import ParseError
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from ashlar.filters import BoundaryPolygonFilter, JsonBFilterBackend, RecordFilter
from ashlar.models import Boundary, BoundaryPolygon, Record, RecordSchema, RecordType
from ashlar.views import BoundaryPolygonViewSet, RecordViewSet, RecordSchemaViewSet


class JsonBFilterViewSet(viewsets.ModelViewSet):
    """ Custom viewset to ensure jsonb_filter viewset properties are set correctly """
    queryset = RecordSchema.objects.all()
    jsonb_filter_field = 'schema'
    jsonb_filters = (
        ('jcontains', False),
    )


class JsonBFilterBackendTestCase(TestCase):
    """ Test serializer field for JsonB """

    def setUp(self):
        self.filter_backend = JsonBFilterBackend()
        self.viewset = JsonBFilterViewSet()
        self.factory = APIRequestFactory()
        self.queryset = RecordSchema.objects.all()

        self.id_type = RecordType.objects.create(label='id', plural_label='ids')
        self.item_type = RecordType.objects.create(label='item', plural_label='items')

        item_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "title": "Item",
            "description": "An item",
            "type": "object",
            "properties": {
                "id": {
                    "description": "The unique identifier for a product",
                    "type": "integer"
                },
                "name": {
                    "description": "Name of the product",
                    "type": "string"
                }
            },
            "required": ["id", "name"]
        }
        id_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "title": "Id",
            "description": "An id",
            "type": "object",
            "properties": {
                "id": {
                    "description": "The unique identifier for a product",
                    "type": "integer"
                }
            }
        }

        schema1 = RecordSchema.objects.create(record_type=self.id_type,
                                              version=1,
                                              schema=id_schema)
        schema2 = RecordSchema.objects.create(record_type=self.item_type,
                                              version=1,
                                              schema=item_schema)

    def test_valid_jcontains_filter(self):
        """ Test filtering on jsonb keys """
        request = Request(self.factory.get('/foo/?jsonb={"title": {"_rule_type": "containment", "contains": ["Id"]}}'))
        queryset = self.filter_backend.filter_queryset(request, self.queryset, self.viewset)
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].record_type, self.id_type)


class RecordQueryTestCase(TestCase):
    """ Test Record queries """

    def setUp(self):
        self.filter_backend = RecordFilter()
        self.viewset = RecordViewSet()
        self.factory = APIRequestFactory()
        self.queryset = Record.objects.all()

        self.id_type = RecordType.objects.create(label='id', plural_label='ids')
        self.id_schema = RecordSchema.objects.create(
            record_type=self.id_type,
            version=1,
            schema={}
        )
        self.id_record_1 = Record.objects.create(
            occurred_from=timezone.now(),
            occurred_to=timezone.now(),
            geom='POINT (0 0)',
            schema=self.id_schema,
            data={}
        )
        self.id_record_2 = Record.objects.create(
            occurred_from=timezone.now(),
            occurred_to=timezone.now(),
            geom='POINT (0 0)',
            schema=self.id_schema,
            data={}
        )

        self.item_type = RecordType.objects.create(label='item', plural_label='items')
        self.item_schema = RecordSchema.objects.create(
            record_type=self.item_type,
            version=1,
            schema={}
        )
        self.item_record_1 = Record.objects.create(
            occurred_from=timezone.now(),
            occurred_to=timezone.now(),
            geom='POINT (0 0)',
            schema=self.item_schema,
            data={}
        )
        self.item_record_2 = Record.objects.create(
            occurred_from=timezone.now(),
            occurred_to=timezone.now(),
            geom='POINT (0 0)',
            schema=self.item_schema,
            data={}
        )


    def test_record_type_filter(self):
        """ Test filtering by record type """
        queryset = self.filter_backend.filter_record_type(self.queryset, self.id_type.uuid)
        self.assertEqual(len(queryset), 2)
        self.assertEqual(queryset[0].schema, self.id_schema)


class BoundaryPolygonQueryTestCase(TestCase):
    """ Test BoundaryPolygon queries """

    def setUp(self):
        self.filter_backend = BoundaryPolygonFilter()
        self.viewset = BoundaryPolygonViewSet()
        self.factory = APIRequestFactory()
        self.queryset = BoundaryPolygon.objects.all()

        self.boundary_1 = Boundary.objects.create(label='boundary_1')
        self.boundary_2 = Boundary.objects.create(label='boundary_2')

        self.boundary_polygon_1 = BoundaryPolygon.objects.create(
            geom=('MULTIPOLYGON (((30 20, 45 40, 10 40, 30 20)),'
                  '((15 5, 40 10, 10 20, 5 10, 15 5)))'),
            boundary=self.boundary_1,
            data={}
        )
        self.boundary_polygon_1 = BoundaryPolygon.objects.create(
            geom=('MULTIPOLYGON (((40 40, 20 45, 45 30, 40 40)),'
                  '((20 35, 10 30, 10 10, 30 5, 45 20, 20 35),'
                  '(30 20, 20 15, 20 25, 30 20)))'),
            boundary=self.boundary_2,
            data={}
        )

    def test_boundary_filter(self):
        """ Test filtering by boundary """
        queryset = self.filter_backend.filter_boundary(self.queryset, self.boundary_1.uuid)
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].boundary, self.boundary_1)
