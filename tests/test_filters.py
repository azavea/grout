import json

from django.test import TestCase
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.exceptions import ParseError
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from ashlar.filters import JsonBFilterBackend, RecordFilter
from ashlar.models import Record, RecordSchema, RecordType
from ashlar.views import RecordViewSet, RecordSchemaViewSet


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
        filter_data = json.dumps({ 'title': 'Id' })
        request = Request(self.factory.get('/foo/', {'jcontains': filter_data}))
        queryset = self.filter_backend.filter_queryset(request, self.queryset, self.viewset)
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].record_type, self.id_type)

    def test_disallow_invalid_json(self):
        """ Raise parse error on invalid json in jcontains request """
        filter_data = '{"test": }'
        request = Request(self.factory.get('/foo/', {'jcontains': filter_data}))
        with self.assertRaises(ParseError):
            queryset = self.filter_backend.filter_queryset(request, self.queryset, self.viewset)

    def test_ensure_allow_scalar_false_raises_error(self):
        """ A scalar value in jcontains filter should raise ParseError """
        filter_data = 3
        request = Request(self.factory.get('/foo/', {'jcontains': filter_data}))
        with self.assertRaises(ParseError):
            queryset = self.filter_backend.filter_queryset(request, self.queryset, self.viewset)


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
            label='id_record_1 label',
            slug='id_record_1 slug',
            geom='POINT (0 0)',
            schema=self.id_schema,
            data={}
        )
        self.id_record_2 = Record.objects.create(
            occurred_from=timezone.now(),
            occurred_to=timezone.now(),
            label='id_record_2 label',
            slug='id_record_2 slug',
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
            label='item_record_1 label',
            slug='item_record_1 slug',
            geom='POINT (0 0)',
            schema=self.item_schema,
            data={}
        )
        self.item_record_2 = Record.objects.create(
            occurred_from=timezone.now(),
            occurred_to=timezone.now(),
            label='item_record_2 label',
            slug='item_record_2 slug',
            geom='POINT (0 0)',
            schema=self.item_schema,
            data={}
        )


    def test_record_type_filter(self):
        """ Test filtering by record type """
        queryset = self.filter_backend.filter_record_type(self.queryset, self.id_type.uuid)
        self.assertEqual(len(queryset), 2)
        self.assertEqual(queryset[0].schema, self.id_schema)
