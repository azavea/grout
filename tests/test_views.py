import os
import json

import django
from django.contrib.gis.geos import (Point, Polygon, LinearRing, MultiPolygon,
                                    LineString)
from django.utils import timezone

from rest_framework import status

from tests.api_test_case import GroutAPITestCase
from grout.models import (Boundary, BoundaryPolygon,
                          RecordSchema, RecordType, Record)
from grout.views import RecordViewSet
from grout.exceptions import (GEOMETRY_TYPE_ERROR, DATETIME_REQUIRED,
                              DATETIME_NOT_PERMITTED, MIN_DATE_RANGE_ERROR,
                              MAX_DATE_RANGE_ERROR)

if django.VERSION < (2, 0):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse

class RecordSchemaViewTestCase(GroutAPITestCase):

    def setUp(self):
        super(RecordSchemaViewTestCase, self).setUp()
        self.record_type = RecordType.objects.create(label='foo', plural_label='foos')

    def test_list(self):
        """Basic test to make sure test_list returns the right number of results"""
        RecordSchema.objects.create(schema={"type": "object"},
                                    version=1,
                                    record_type=self.record_type)
        url = reverse('recordschema-list')
        response_data = json.loads(self.client.get(url).content.decode('utf-8'))
        self.assertEqual(response_data['count'], 1)

    def test_detail(self):
        """Test that basic fields returned properly"""
        schema = RecordSchema.objects.create(schema={"type": "object"},
                                             version=1,
                                             record_type=self.record_type)
        url = reverse('recordschema-detail', args=(schema.pk,))
        response_data = json.loads(self.client.get(url).content.decode('utf-8'))
        self.assertEqual(str(schema.pk), response_data['uuid'])
        self.assertEqual(schema.schema, response_data['schema'])
        self.assertEqual(str(schema.record_type.uuid), response_data['record_type'])

    def test_create(self):
        """Basic test that schema creation via endpoint works"""
        url = reverse('recordschema-list')
        # Old style formatting so we don't have to escape all the braces
        schema_data = """{"schema": {"type": "object"},
                       "record_type": "%s"}""" % self.record_type.pk
        response = self.client.post(url, schema_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['version'], 1)

    def test_create_new_version(self):
        """Test that creating a new Schema with an existing record_type increments version"""
        schema = RecordSchema.objects.create(schema={"type": "object"},
                                             version=1,
                                             record_type=self.record_type)
        # Old style formatting so we don't have to escape all the braces
        schema_data = """{"schema": {"type": "object"},
                       "record_type": "%s"}""" % self.record_type.pk
        url = reverse('recordschema-list')
        response = self.client.post(url, schema_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['version'], schema.version + 1)
        # Reload schema from db; its next_version should have changed.
        schema = RecordSchema.objects.get(pk=schema.pk)
        self.assertEqual(str(schema.next_version.pk), response_data['uuid'])
        self.assertEqual(RecordSchema.objects.filter(record_type=schema.record_type).count(), 2)

    def test_no_update(self):
        """Test that schemas are immutable"""
        schema = RecordSchema.objects.create(schema={"type": "object"},
                                             version=1,
                                             record_type=self.record_type)
        schema_data = """{"schema": { },
                          "version": 1,
                          "record_type": "foo"}"""
        url = reverse('recordschema-detail', args=(schema.pk,))
        # Attempt to update existing schema
        response = self.client.patch(url, schema_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.content)

    def test_no_delete(self):
        """Test that deletion doesn't work"""
        schema = RecordSchema.objects.create(schema={"type": "object"},
                                             version=1,
                                             record_type=self.record_type)
        url = reverse('recordschema-detail', args=(schema.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.content)


class RecordTypeViewTestCase(GroutAPITestCase):

    def setUp(self):
        super(RecordTypeViewTestCase, self).setUp()

        self.schema = {
            "type": "object",
            "properties": {}
        }

    def test_record_type_has_current_schema(self):
        """ Test current schema exists and updates when we create a new schema """
        record_type = RecordType.objects.create(label='foo', plural_label='foos')
        record_schema = RecordSchema.objects.create(schema=self.schema,
                                                    version=1,
                                                    record_type=record_type)
        url = reverse('recordtype-detail', args=(record_type.pk,))
        response = self.client.get(url)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['current_schema'], str(record_schema.uuid), response_data)

        new_schema = dict(self.schema)
        new_schema['title'] = 'New Schema'
        new_record_schema = RecordSchema.objects.create(schema=new_schema,
                                                        version=2,
                                                        record_type=record_type)

        url = reverse('recordtype-detail', args=(record_type.pk,))
        response = self.client.get(url)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['current_schema'],
                         str(new_record_schema.uuid),
                         response_data)

    def test_record_count(self):
        record_type = RecordType.objects.create(label='foo', plural_label='foos')
        record_schema = RecordSchema.objects.create(schema=self.schema,
                                                    version=1,
                                                    record_type=record_type)
        url = reverse('recordtype-detail', args=(record_type.pk,))
        response = self.client.get(url)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['current_schema'], str(record_schema.uuid), response_data)

        new_schema = dict(self.schema)
        new_schema['title'] = 'New Schema'
        new_record_schema = RecordSchema.objects.create(schema=new_schema,
                                                        version=2,
                                                        record_type=record_type)

        url = reverse('recordtype-detail', args=(record_type.pk,))
        response = self.client.get(url)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['current_schema'], str(new_record_schema.uuid),
                         response_data)

class PointRecordViewTestCase(GroutAPITestCase):
    """
    Test basic API views involving temporal Records with point geometries.
    """
    @classmethod
    def setUpClass(cls):
        super(PointRecordViewTestCase, cls).setUpClass()

        # Create dummy data for a Point RecordType.
        cls.point_record_type = RecordType.objects.create(label='Point',
                                                          plural_label='Points',
                                                          geometry_type='point',
                                                          temporal=True)
        cls.point_schema = RecordSchema.objects.create(record_type=cls.point_record_type,
                                                       version=1,
                                                       schema={})
        cls.point_record = Record.objects.create(schema=cls.point_schema,
                                                 data='{}',
                                                 occurred_from=timezone.now(),
                                                 occurred_to=timezone.now(),
                                                 geom=Point(0, 0))
        # The base endpoint for listing records.
        cls.record_endpt = reverse('record-list')

    def test_create_point_record(self):
        """
        Test successfully creating a Record with point geometry.
        """
        data = {
            'schema': self.point_schema.uuid,
            'occurred_from': timezone.now(),
            'occurred_to': timezone.now(),
            'geom': 'POINT(0 0)',
            'archived': False,
            'data': {},
        }

        response = self.client.post(self.record_endpt, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        uuid = response.data['uuid']
        new_record = Record.objects.get(uuid=uuid)
        self.assertEqual(new_record.geom.coords, Point(0, 0).coords)

    def test_point_record_wrong_geometry_errors(self):
        """
        Test that uploading the wrong type of geometry to a Record in a
        Point RecordType raises an error.
        """
        coords = ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))
        points = ', '.join('%d %d' % (x, y) for x, y in coords)
        geom = 'POLYGON(({points}))'.format(points=points)
        data = {
            'schema': self.point_schema.uuid,
            'occurred_from': timezone.now(),
            'occurred_to': timezone.now(),
            'geom': geom,  # Use a Polygon instead of a Point.
            'archived': False,
            'data': {},
        }

        response = self.client.post(self.record_endpt, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

        received_msg = json.loads(response.content.decode('utf-8')).get('geom')
        expected_msg = GEOMETRY_TYPE_ERROR.format(incoming='Polygon',
                                                  expected='Point',
                                                  uuid=self.point_record_type.uuid)
        self.assertEqual(received_msg, expected_msg, response.content)

    def test_get_point_record(self):
        """
        Get a Record with point geometry.
        """
        data = {
            'record_type': self.point_record_type.uuid
        }
        response = self.client.get(self.record_endpt, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['count'], 1)

        response_entity = response_data['results'][0]
        self.assertEqual(response_entity['uuid'],
                         str(self.point_record.uuid),
                         response_entity)

        response_geotype = response_entity['geom']['type']
        self.assertEqual(response_geotype, 'Point', response_entity)

        response_coordinates = response_entity['geom']['coordinates']
        # Format the tuples in the expected coordinates as lists to match the response,
        # which comes in as JSON.
        expected_coordinates = json.loads(json.dumps(self.point_record.geom.coords))
        self.assertEqual(response_coordinates, expected_coordinates, response_entity)


class PolygonRecordViewTestCase(GroutAPITestCase):
    """
    Test basic API views involving temporal Records with polygon geometries.
    """
    @classmethod
    def setUpClass(cls):
        super(PolygonRecordViewTestCase, cls).setUpClass()

        # Create dummy data for a Polygon RecordType.
        cls.coords = ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))
        cls.polygon_record_type = RecordType.objects.create(label='Polygon',
                                                            plural_label='Polygons',
                                                            geometry_type='polygon',
                                                            temporal=True)
        cls.polygon_schema = RecordSchema.objects.create(record_type=cls.polygon_record_type,
                                                         version=1,
                                                         schema={})
        cls.polygon_record = Record.objects.create(schema=cls.polygon_schema,
                                                   data='{}',
                                                   occurred_from=timezone.now(),
                                                   occurred_to=timezone.now(),
                                                   geom=Polygon(LinearRing(cls.coords)))
        # The base endpoint for listing records.
        cls.record_endpt = reverse('record-list')

    def test_create_polygon_record(self):
        """
        Test successfully creating a Record with polygon geometry.
        """
        points = ', '.join('%d %d' % (x, y) for x, y in self.coords)
        geom = 'POLYGON(({points}))'.format(points=points)
        data = {
            'schema': self.polygon_schema.uuid,
            'occurred_from': timezone.now(),
            'occurred_to': timezone.now(),
            'geom': geom,
            'archived': False,
            'data': {},
        }

        response = self.client.post(self.record_endpt, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        uuid = response.data['uuid']
        new_record = Record.objects.get(uuid=uuid)
        expected_coords = Polygon(LinearRing(self.coords)).coords
        self.assertEqual(new_record.geom.coords, expected_coords)

    def test_polygon_record_wrong_geometry_errors(self):
        """
        Test that uploading the wrong type of geometry to a Record in a
        Polygon RecordType raises an error.
        """
        data = {
            'schema': self.polygon_schema.uuid,
            'occurred_from': timezone.now(),
            'occurred_to': timezone.now(),
            'geom': 'POINT(0 0)',  # Use a Point instead of a Polygon.
            'archived': False,
            'data': {},
        }

        response = self.client.post(self.record_endpt, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

        received_msg = json.loads(response.content.decode('utf-8')).get('geom')
        expected_msg = GEOMETRY_TYPE_ERROR.format(incoming='Point',
                                                  expected='Polygon',
                                                  uuid=self.polygon_record_type.uuid)
        self.assertEqual(received_msg, expected_msg, response.content)

    def test_get_polygon_record(self):
        """
        Get a Record with polygon geometry.
        """
        data = {
            'record_type': self.polygon_record_type.uuid
        }
        response = self.client.get(self.record_endpt, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['count'], 1)

        response_entity = response_data['results'][0]
        self.assertEqual(response_entity['uuid'],
                         str(self.polygon_record.uuid),
                         response_entity)

        response_geotype = response_entity['geom']['type']
        self.assertEqual(response_geotype, 'Polygon', response_entity)

        response_coordinates = response_entity['geom']['coordinates']
        # Format the tuples in the expected coordinates as lists to match the response,
        # which comes in as JSON.
        expected_coordinates = json.loads(json.dumps(self.polygon_record.geom.coords))
        self.assertEqual(response_coordinates, expected_coordinates, response_entity)


class MultiPolygonRecordViewTestCase(GroutAPITestCase):
    """
    Test basic API views involving temporal Records with MultiPolygon geometries.
    """
    @classmethod
    def setUpClass(cls):
        super(MultiPolygonRecordViewTestCase, cls).setUpClass()

        # Create dummy data for a MultiPolygon Recordtype.
        cls.coords = ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))
        cls.multipolygon_record_type = RecordType.objects.create(label='Multipolygon',
                                                                 plural_label='Multipolygons',
                                                                 geometry_type='multipolygon',
                                                                 temporal=True)
        cls.multipolygon_schema = RecordSchema.objects.create(record_type=cls.multipolygon_record_type,
                                                              version=1,
                                                              schema={})
        cls.multipolygon_record = Record.objects.create(schema=cls.multipolygon_schema,
                                                        data='{}',
                                                        occurred_from=timezone.now(),
                                                        occurred_to=timezone.now(),
                                                        geom=MultiPolygon(Polygon(LinearRing(cls.coords))))

        # The base endpoint for listing records.
        cls.record_endpt = reverse('record-list')

    def test_create_multipolygon_record(self):
        """
        Test successfully creating a Record with multipolygon geometry.
        """
        points = ', '.join('%d %d' % (x, y) for x, y in self.coords)
        geom = 'MULTIPOLYGON((({points})))'.format(points=points)
        data = {
            'schema': self.multipolygon_schema.uuid,
            'occurred_from': timezone.now(),
            'occurred_to': timezone.now(),
            'geom': geom,
            'archived': False,
            'data': {},
        }

        response = self.client.post(self.record_endpt, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        uuid = response.data['uuid']
        new_record = Record.objects.get(uuid=uuid)
        expected_coords = MultiPolygon(Polygon(LinearRing(self.coords))).coords
        self.assertEqual(new_record.geom.coords, expected_coords)

    def test_multipolygon_record_wrong_geometry_errors(self):
        """
        Test that uploading the wrong type of geometry to a Record in a
        Multipolygon RecordType raises an error.
        """
        data = {
            'schema': self.multipolygon_schema.uuid,
            'occurred_from': timezone.now(),
            'occurred_to': timezone.now(),
            'geom': 'POINT(0 0)',  # Use a Point instead of a MultiPolygon.
            'archived': False,
            'data': {},
        }

        response = self.client.post(self.record_endpt, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

        received_msg = json.loads(response.content.decode('utf-8')).get('geom')
        expected_msg = GEOMETRY_TYPE_ERROR.format(incoming='Point',
                                                  expected='MultiPolygon',
                                                  uuid=self.multipolygon_record_type.uuid)
        self.assertEqual(received_msg, expected_msg, response.content)

    def test_get_multipolygon_record(self):
        """
        Get a Record with multipolygon geometry.
        """
        data = {
            'record_type': self.multipolygon_record_type.uuid
        }
        response = self.client.get(self.record_endpt, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['count'], 1)

        response_entity = response_data['results'][0]
        self.assertEqual(response_entity['uuid'],
                         str(self.multipolygon_record.uuid),
                         response_entity)

        response_geotype = response_entity['geom']['type']
        self.assertEqual(response_geotype, 'MultiPolygon', response_entity)

        response_coordinates = response_entity['geom']['coordinates']
        # Format the tuples in the expected coordinates as lists to match the response,
        # which comes in as JSON.
        expected_coordinates = json.loads(json.dumps(self.multipolygon_record.geom.coords))
        self.assertEqual(response_coordinates, expected_coordinates, response_entity)


class LineStringRecordViewTestCase(GroutAPITestCase):
    """
    Test basic API views involving temporal Records with LineString geometries.
    """
    @classmethod
    def setUpClass(cls):
        super(LineStringRecordViewTestCase, cls).setUpClass()

        # Create dummy data for a LineString Recordtype.
        cls.coords = ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))
        cls.linestring_record_type = RecordType.objects.create(label='Linestring',
                                                               plural_label='Linestrings',
                                                               geometry_type='linestring',
                                                               temporal=True)
        cls.linestring_schema = RecordSchema.objects.create(record_type=cls.linestring_record_type,
                                                            version=1,
                                                            schema={})
        cls.linestring_record = Record.objects.create(schema=cls.linestring_schema,
                                                      data='{}',
                                                      occurred_from=timezone.now(),
                                                      occurred_to=timezone.now(),
                                                      geom=LineString(cls.coords))
        # The base endpoint for listing records.
        cls.record_endpt = reverse('record-list')

    def test_create_linestring_record(self):
        """
        Test successfully creating a Record with linestring geometry.
        """
        points = ', '.join('%d %d' % (x, y) for x, y in self.coords)
        geom = 'LINESTRING({points})'.format(points=points)
        data = {
            'schema': self.linestring_schema.uuid,
            'occurred_from': timezone.now(),
            'occurred_to': timezone.now(),
            'geom': geom,
            'archived': False,
            'data': {},
        }

        response = self.client.post(self.record_endpt, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        uuid = response.data['uuid']
        new_record = Record.objects.get(uuid=uuid)
        expected_coords = LineString(self.coords).coords
        self.assertEqual(new_record.geom.coords, expected_coords)

    def test_linestring_record_wrong_geometry_errors(self):
        """
        Test that uploading the wrong type of geometry to a Record in a
        Linestring RecordType raises an error.
        """
        data = {
            'schema': self.linestring_schema.uuid,
            'occurred_from': timezone.now(),
            'occurred_to': timezone.now(),
            'geom': 'POINT(0 0)',  # Use a Point instead of a LineString.
            'archived': False,
            'data': {},
        }

        response = self.client.post(self.record_endpt, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

        received_msg = json.loads(response.content.decode('utf-8')).get('geom')
        expected_msg = GEOMETRY_TYPE_ERROR.format(incoming='Point',
                                                  expected='LineString',
                                                  uuid=self.linestring_record_type.uuid)
        self.assertEqual(received_msg, expected_msg, response.content)

    def test_get_linestring_record(self):
        """
        Get a Record with linestring geometry.
        """
        data = {
            'record_type': self.linestring_record_type.uuid
        }
        response = self.client.get(self.record_endpt, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['count'], 1, response_data)

        response_entity = response_data['results'][0]
        self.assertEqual(response_entity['uuid'], str(self.linestring_record.uuid), response_entity)

        response_geotype = response_entity['geom']['type']
        self.assertEqual(response_geotype, 'LineString', response_entity)

        response_coordinates = response_entity['geom']['coordinates']
        # Format the tuples in the expected coordinates as lists to match the response,
        # which comes in as JSON.
        expected_coordinates = json.loads(json.dumps(self.linestring_record.geom.coords))
        self.assertEqual(response_coordinates, expected_coordinates, response_entity)


class NonGeospatialRecordViewTestCase(GroutAPITestCase):
    """
    Test basic API views involving temporal Records with no geometries.
    """
    @classmethod
    def setUpClass(cls):
        super(NonGeospatialRecordViewTestCase, cls).setUpClass()

        # Create dummy data for a RecordType with no geometry.
        cls.nongeospatial_record_type = RecordType.objects.create(label='Nongeospatial',
                                                                  plural_label='Nongeospatials',
                                                                  geometry_type='none',
                                                                  temporal=True)
        cls.nongeospatial_schema = RecordSchema.objects.create(record_type=cls.nongeospatial_record_type,
                                                               version=1,
                                                               schema={})
        cls.nongeospatial_record = Record.objects.create(schema=cls.nongeospatial_schema,
                                                         data='{}',
                                                         occurred_from=timezone.now(),
                                                         occurred_to=timezone.now())
        # The base endpoint for listing records.
        cls.record_endpt = reverse('record-list')

    def test_create_nongeospatial_record(self):
        """
        Test successfully creating a Record with no geometry.
        """
        data = {
            'schema': self.nongeospatial_schema.uuid,
            'occurred_from': timezone.now(),
            'occurred_to': timezone.now(),
            'archived': False,
            'data': {},
        }

        response = self.client.post(self.record_endpt, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.assertIsNone(response.data.get('geom'))

    def test_nongeospatial_record_wrong_geometry_errors(self):
        """
        Test that uploading a geometry to a Record with a nongeospatial RecordType
        raises an error.
        """
        data = {
            'schema': self.nongeospatial_schema.uuid,
            'occurred_from': timezone.now(),
            'occurred_to': timezone.now(),
            'geom': 'POINT(0 0)',
            'archived': False,
            'data': {},
        }

        response = self.client.post(self.record_endpt, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

        received_msg = json.loads(response.content.decode('utf-8')).get('geom')
        expected_msg = GEOMETRY_TYPE_ERROR.format(incoming='Point',
                                                  expected='None',
                                                  uuid=self.nongeospatial_record_type.uuid)
        self.assertEqual(received_msg, expected_msg, response.content)


class NonTemporalRecordViewTestCase(GroutAPITestCase):
    """
    Test basic API views involving Records with no datetime component.
    """
    @classmethod
    def setUpClass(cls):
        super(NonTemporalRecordViewTestCase, cls).setUpClass()

        # Create dummy data for a RecordType with no datetime information.
        cls.nontemporal_record_type = RecordType.objects.create(label='Nontemporal',
                                                                plural_label='Nontemporals',
                                                                geometry_type='point',
                                                                temporal=False)
        cls.nontemporal_schema = RecordSchema.objects.create(record_type=cls.nontemporal_record_type,
                                                             version=1,
                                                             schema={})
        cls.nontemporal_record = Record.objects.create(schema=cls.nontemporal_schema,
                                                       data='{}',
                                                       geom=Point(0, 0))
        # The base endpoint for listing records.
        cls.record_endpt = reverse('record-list')

    def test_create_nontemporal_record(self):
        """
        Test successfully creating a Record with no datetime information.
        """
        data = {
            'schema': self.nontemporal_schema.uuid,
            'geom': 'POINT(0 0)',
            'archived': False,
            'data': {},
        }

        response = self.client.post(self.record_endpt, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.assertIsNone(response.data.get('occurred_from'), response.data)
        self.assertIsNone(response.data.get('occurred_to'), response.data)

    def test_nontemporal_record_with_datetime_info_errors(self):
        """
        Test that uploading datetime information to a nontemporal Record
        raises an error.
        """
        data = {
            'schema': self.nontemporal_schema.uuid,
            'occurred_from': timezone.now(),
            'occurred_to': timezone.now(),
            'geom': 'POINT(0 0)',
            'archived': False,
            'data': {},
        }

        response = self.client.post(self.record_endpt, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

        min_msg = json.loads(response.content.decode('utf-8')).get('occurred_from')
        max_msg = json.loads(response.content.decode('utf-8')).get('occurred_to')
        expected_msg = DATETIME_NOT_PERMITTED.format(uuid=self.nontemporal_record_type.uuid)

        self.assertEqual(min_msg, expected_msg, response.content)
        self.assertEqual(max_msg, expected_msg, response.content)


class BoundaryViewTestCase(GroutAPITestCase):

    def setUp(self):
        super(BoundaryViewTestCase, self).setUp()

        self.boundary1 = Boundary.objects.create(label='foo', source_file='foo.zip',
                                                 status=Boundary.StatusTypes.ERROR)
        self.boundary2 = Boundary.objects.create(label='fooOK', source_file='foo.zip',
                                                 status=Boundary.StatusTypes.COMPLETE)

    def post_boundary(self, zip_filename):
        """ Helper method to create a new boundary via POST """
        zipfile = open(os.path.join(self.files_dir, zip_filename), 'rb')
        data = {
            'color': 'red',
            'label': 'foobar',
            'source_file': zipfile
        }
        url = reverse('boundary-list')
        return self.client.post(url, data)

    def test_status_get_filter(self):
        url = '{}?status={}'.format(reverse('boundary-list'), Boundary.StatusTypes.COMPLETE)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only one of the boundaries has status = COMPLETE
        self.assertEqual(len(response.data['results']), 1)
        boundary = response.data['results'][0]
        self.assertEqual(boundary['status'], Boundary.StatusTypes.COMPLETE)

    def test_create_adds_geom_from_valid_shapefile(self):
        response = self.post_boundary('philly.zip')

        # Make sure that the upload hasn't errored
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'COMPLETE')

        boundary_uuid = response.data['uuid']
        boundary = Boundary.objects.get(uuid=boundary_uuid)
        self.assertGreater(boundary.polygons.count(), 0)

    def test_create_from_macosx_shapefile(self):
        """ Ensure __MACOSX files in archive don't wreck the upload """
        response = self.post_boundary('bayarea_macosx.zip')

        # Make sure that the upload hasn't errored
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'COMPLETE')

        boundary_uuid = response.data['uuid']
        boundary = Boundary.objects.get(uuid=boundary_uuid)
        self.assertGreater(boundary.polygons.count(), 0)

    def test_boundary_crud(self):
        """ Already tested create, so don't bother, but test other operations """
        response = self.post_boundary('philly.zip')

        # Make sure that the upload hasn't errored
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'COMPLETE')

        boundary_dict = response.data
        uuid = boundary_dict['uuid']

        url = reverse('boundary-detail', args=[uuid])

        # Read back list and ensure same as boundary dict
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, boundary_dict)

        # Update display field to be first in result display_fields
        display_field = boundary_dict['data_fields'][0]
        data = {
            'uuid': uuid,
            'display_field': display_field
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['display_field'], display_field)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_shapefile(self):
        """ This shapefile has points, not polygons """
        """ Already tested create, so don't bother, but test other operations """
        response = self.post_boundary('points.zip')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['errors'])
        self.assertEqual(response.data['status'], Boundary.StatusTypes.ERROR)

    def test_uniqueness_constraint(self):
        """Test that uploading a boundary that already exists will fail."""
        # Upload the shapefile a first time and confirm that it works.
        first_response = self.post_boundary('philly.zip')
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(first_response.data['status'], Boundary.StatusTypes.COMPLETE)

        # Upload the shapefile a second time and confirm that an error is raised.
        error_response = self.post_boundary('philly.zip')
        self.assertEqual(error_response.status_code, status.HTTP_409_CONFLICT)
        self.assertIsNotNone(error_response.data['error'])
        self.assertEqual(error_response.data['error'], 'uniqueness constraint violation')

    def test_geojson_response(self):
        """ Create shape, then test that geojson serializes out properly """
        response = self.post_boundary('bayarea_macosx.zip')
        uuid = response.data['uuid']
        url = '{}geojson/'.format(reverse('boundary-detail', args=[uuid]))

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'FeatureCollection')
        self.assertEqual(len(response.data['features']), 3)


class BoundaryPolygonViewTestCase(GroutAPITestCase):
    def setUp(self):
        boundary = Boundary.objects.create(label='fooOK', source_file='foo.zip',
                                           status=Boundary.StatusTypes.COMPLETE)
        coords = ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))
        self.poly = BoundaryPolygon.objects.create(data={},
                                                   geom=MultiPolygon(Polygon(LinearRing(coords))),
                                                   boundary=boundary)

    def test_no_geom_param(self):
        """Make sure that the nogeom param excludes the geometry and includes a bounding box"""
        super(BoundaryPolygonViewTestCase, self).setUp()
        url = reverse('boundarypolygon-detail', args=[self.poly.uuid])
        response = self.client.get(url, {'nogeom': True})
        self.assertIn('bbox', response.data)
        self.assertNotIn('geom', response.data)
