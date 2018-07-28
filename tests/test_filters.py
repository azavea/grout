import json

import mock

from django.test import TestCase
from django.utils import timezone
from django.contrib.gis.geos import Polygon, MultiPolygon
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.exceptions import ParseError

from grout import models
from grout.filters import (BoundaryPolygonFilter, JsonBFilterBackend, RecordFilter,
                           RecordTypeFilter)
from grout.models import Boundary, BoundaryPolygon, Record, RecordSchema, RecordType
from grout.views import BoundaryPolygonViewSet, RecordViewSet


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
        try:
            self.user = User.objects.get(username='admin')
        except ObjectDoesNotExist:
            self.user = User.objects.create_user('admin',
                                                 'grout@azavea.com',
                                                 '123')

        self.filter_backend = RecordFilter(queryset=Record.objects.all())
        self.viewset = RecordViewSet()
        self.view = RecordViewSet.as_view({'get': 'list'})
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

        # Create a non-geospatial Record.
        self.nongeospatial_type = RecordType.objects.create(
            label='nongeospatial',
            plural_label='nongeospatials'
        )
        self.nongeospatial_schema = RecordSchema.objects.create(
            record_type=self.nongeospatial_type,
            version=1,
            schema={}
        )
        self.nongeospatial_record = models.TemporalFlexibleRecord.objects.create(
            occurred_from=timezone.now(),
            occurred_to=timezone.now(),
            schema=self.nongeospatial_schema,
            data={}
        )

        # Create a Record with a Polygon geometry.
        self.polygon_type = RecordType.objects.create(
            label='polygon',
            plural_label='polygons'
        )
        self.polygon_schema = RecordSchema.objects.create(
            record_type=self.polygon_type,
            version=1,
            schema={}
        )
        self.polygon_record = models.TemporalPolygonRecord.objects.create(
            occurred_from=timezone.now(),
            occurred_to=timezone.now(),
            geom=Polygon(((-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1))),
            schema=self.polygon_schema,
            data={}
        )

        # Group the records by geometry type.
        self.point_records = (self.id_record_1, self.id_record_2,
                              self.item_record_1, self.item_record_2)

        self.boundary = Boundary.objects.create(label='Parent for polygons')

    def test_record_type_filter(self):
        """ Test filtering by record type """
        queryset = self.filter_backend.filter_record_type(self.queryset, 'schema', self.id_type.uuid)
        self.assertEqual(len(queryset), 2)
        self.assertEqual(queryset[0].schema, self.id_schema)

    def test_type_for_record_filter(self):
        """Test retrieving a RecordType from a Record."""
        filter_backend = RecordTypeFilter()
        record_types = RecordType.objects.all()

        queryset = filter_backend.type_for_record(record_types, 'pk', self.id_record_1.uuid)

        self.assertEqual(queryset.count(), 1)

    def test_polygon_id_filter(self):
        """Test filtering by a polygon ID"""
        contains0_0 = BoundaryPolygon.objects.create(
            boundary=self.boundary,
            data={},
            geom=MultiPolygon(Polygon(((-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1))))
        )
        no_contains0_0 = BoundaryPolygon.objects.create(
            boundary=self.boundary,
            data={},
            geom=MultiPolygon(Polygon(((1, 1), (2, 1), (2, 2), (1, 2), (1, 1))))
        )
        # Test a geometry that contains the records
        contained_record_count = len([self.id_record_1, self.id_record_2,
                                      self.item_record_1, self.item_record_2,
                                      self.polygon_record])
        queryset = self.filter_backend.filter_polygon_id(self.queryset, 'geom', contains0_0.pk)
        self.assertEqual(queryset.count(), contained_record_count)

        # Test a geometry that does not contain any of the records
        queryset = self.filter_backend.filter_polygon_id(self.queryset, 'geom', no_contains0_0.pk)
        self.assertEqual(queryset.count(), 0)

        # Test leaving out an ID
        full_record_count = len([self.id_record_1, self.id_record_2,
                                 self.item_record_1, self.item_record_2,
                                 self.polygon_record,
                                 self.nongeospatial_record])
        queryset = self.filter_backend.filter_polygon_id(self.queryset, 'geom', None)
        self.assertEqual(queryset.count(), full_record_count)

    def test_valid_polygon_fiter(self):
        """Test filtering by an arbitrary valid GeoJSON polygon."""
        # Test a geometry that contains the records (all of which have coordinates (0, 0)).
        contains0_0 = json.dumps({
            'type': 'Polygon',
            'coordinates': [[[-1, -1], [-1, 1], [1, 1], [1, -1], [-1, -1]]]
        })
        queryset = self.filter_backend.filter_polygon(self.queryset, 'geom', contains0_0)
        self.assertEqual(queryset.count(), 4)

        # Test a geometry that does not contain the records.
        no_contains0_0 = json.dumps({
            'type': 'Polygon',
            'coordinates': [[[1, 1], [1, 2], [2, 2], [2, 1], [1, 1]]]
        })
        queryset = self.filter_backend.filter_polygon(self.queryset, 'geom', no_contains0_0)
        self.assertEqual(queryset.count(), 0)

    def test_polygon_filter_parse_error(self):
        """Test that filtering by a malformed GeoJSON polygon raises an error."""
        invalid_geojson = json.dumps({
            'type': 'Foo',
            'coordinates': [[[]]]
        })

        with self.assertRaises(ParseError):
            queryset = self.filter_backend.filter_polygon(self.queryset, 'geom', invalid_geojson)

    def test_invalid_polygon_filter(self):
        """Test that filtering by an invalid GeoJSON polygon raises an error."""
        class MockGeometry(mock.MagicMock):
            @property
            def valid(self):
                return False

            @property
            def valid_reason(self):
                return ''

        # Patch GEOSGeometry so that the geometry is always invalid.
        with mock.patch('grout.filters.GEOSGeometry', new_callable=MockGeometry):
            geojson = json.dumps({
                'type': 'Polygon',
                'coordinates': [[[1, 1], [1, 2], [2, 2], [2, 1], [1, 1]]]
            })

            with self.assertRaises(ParseError) as e:
                queryset = self.filter_backend.filter_polygon(self.queryset, 'geom', geojson)

    def test_geometry_type_point_filter(self):
        """Test filtering for PointRecords."""
        point_record_count = len([self.id_record_1, self.id_record_2,
                                  self.item_record_1, self.item_record_2])
        point_req = self.factory.get('/foo/', {'geometry_type': 'point'})
        force_authenticate(point_req, self.user)
        point_res = self.view(point_req).render()
        self.assertEqual(json.loads(point_res.content.decode('utf-8'))['count'],
                         point_record_count)

    def test_geometry_type_polygon_filter(self):
        """Test filtering for PolygonRecords."""
        polygon_record_count = len([self.polygon_record])
        polygon_req = self.factory.get('/foo/', {'geometry_type': 'polygon'})
        force_authenticate(polygon_req, self.user)
        polygon_res = self.view(polygon_req).render()
        self.assertEqual(json.loads(polygon_res.content.decode('utf-8'))['count'],
                         polygon_record_count)

    def test_geometry_type_none_filter(self):
        """Test filtering for FlexibleRecords."""
        nongeospatial_record_count = len([self.nongeospatial_record])
        nongeospatial_req = self.factory.get('/foo/', {'geometry_type': 'none'})
        force_authenticate(nongeospatial_req, self.user)
        nongeospatial_res = self.view(nongeospatial_req).render()
        self.assertEqual(json.loads(nongeospatial_res.content.decode('utf-8'))['count'],
                         nongeospatial_record_count)

    def test_geometry_type_unregistered_filter(self):
        """Ensure that an error gets thrown when the user sends in an unexpected geometry_type."""
        bad_req = self.factory.get('/foo/', {'geometry_type': 'foobarbaz'})
        force_authenticate(bad_req, self.user)
        bad_res = self.view(bad_req).render()
        self.assertEqual(bad_res.status_code, 400)
        self.assertEqual(json.loads(bad_res.content.decode('utf-8'))['detail'],
                         RecordViewSet.GEOTYPE_NOT_VALID)

    def test_geometry_type_and_polygon_filters_are_mutually_exclusive(self):
        """Test that the user cannot filter on `geometry_type:none` and `polygon`."""
        # Test that the `polygon` parameter raises an error.
        geojson = json.dumps({
            'type': 'Polygon',
            'coordinates': [[[1, 1], [1, 2], [2, 2], [2, 1], [1, 1]]]
        })
        bad_polygon_req = self.factory.get('/foo/', {'geometry': 'none', 'polygon': geojson})
        force_authenticate(bad_polygon_req, self.user)
        bad_polygon_res = self.view(bad_polygon_req).render()

        self.assertEqual(bad_polygon_res.status_code, 400)
        self.assertEqual(json.loads(bad_polygon_res.content.decode('utf-8'))['detail'],
                         'Replace with the correct error message.')

        # Test that the `polygon_id` parameter raises an error.
        polygon_id = BoundaryPolygon.objects.create(
            boundary=self.boundary,
            data={},
            geom=MultiPolygon(Polygon(((-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1))))
        )
        bad_polygon_id_req = self.factory.get('/foo/', {'geometry': 'none', 'polygon_id': polygon_id})
        force_authenticate(bad_polygon_id_req, self.user)
        bad_polygon_id_res = self.view(bad_polygon_id_req).render()

        self.assertEqual(bad_polygon_id_res.status_code, 400)
        self.assertEqual(json.loads(bad_polygon_id_res.content.decode('utf-8'))['detail'],
                         'Replace with the correct error message.')


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
        queryset = self.filter_backend.filter_boundary(self.queryset, 'status', self.boundary_1.uuid)
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].boundary, self.boundary_1)
