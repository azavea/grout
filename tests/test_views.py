import os
import json
from datetime import datetime, timedelta

from django.core.urlresolvers import reverse

from rest_framework import status

from tests.api_test_case import AshlarAPITestCase
from ashlar.models import Boundary, RecordSchema, RecordType, Record


class RecordViewTestCase(AshlarAPITestCase):

    def setUp(self):
        super(RecordViewTestCase, self).setUp()
        self.now = datetime.now()
        self.then = self.now - timedelta(days=10)
        self.laterThanThen = self.now - timedelta(days=9)

        self.tod = self.now.hour
        self.dow = self.now.isoweekday() + 1  # 1 added here to handle differences in indexing

        self.record_type = RecordType.objects.create(label='foo', plural_label='foos')
        self.schema = RecordSchema.objects.create(schema={"type": "object"},
                                                  version=1,
                                                  record_type=self.record_type)
        self.record1 = Record.objects.create(occurred_from=self.now,
                                             occurred_to=self.now,
                                             geom='POINT (0 0)',
                                             schema=self.schema)
        self.record2 = Record.objects.create(occurred_from=self.then,
                                             occurred_to=self.now,
                                             geom='POINT (0 0)',
                                             schema=self.schema)

    def test_toddow(self):
        url = '/api/records/toddow/?record_type={}'.format(str(self.record_type.uuid))
        response_data = json.loads(self.client.get(url).content)[1]  # only one record to count

        self.assertEqual(response_data['count'], 1)
        self.assertEqual(response_data['tod'], self.tod)
        self.assertEqual(response_data['dow'], self.dow)

    def test_arbitrary_filters(self):
        base = '/api/records/toddow/?record_type={rt}&&occurred_max={dtmax}Z&occurred_min={dtmin}Z'

        url1 = base.format(rt=self.record_type.uuid,
                           dtmin=self.laterThanThen.isoformat(),  # later than `then`
                           dtmax=self.now.isoformat())
        response_data1 = json.loads(self.client.get(url1).content)
        self.assertEqual(len(response_data1), 1)

        url2 = base.format(rt=self.record_type.uuid,
                           dtmin=self.then.isoformat(),  # `then`
                           dtmax=self.now.isoformat())
        response_data2 = json.loads(self.client.get(url2).content)
        self.assertEqual(len(response_data2), 2)


class RecordSchemaViewTestCase(AshlarAPITestCase):

    def setUp(self):
        super(RecordSchemaViewTestCase, self).setUp()
        self.record_type = RecordType.objects.create(label='foo', plural_label='foos')

    def test_list(self):
        """Basic test to make sure test_list returns the right number of results"""
        RecordSchema.objects.create(schema={"type": "object"},
                                    version=1,
                                    record_type=self.record_type)
        url = reverse('recordschema-list')
        response_data = json.loads(self.client.get(url).content)
        self.assertEqual(response_data['count'], 1)

    def test_detail(self):
        """Test that basic fields returned properly"""
        schema = RecordSchema.objects.create(schema={"type": "object"},
                                             version=1,
                                             record_type=self.record_type)
        url = reverse('recordschema-detail', args=(schema.pk,))
        response_data = json.loads(self.client.get(url).content)
        self.assertEqual(unicode(schema.pk), response_data['uuid'])
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
        response_data = json.loads(response.content)
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
        response_data = json.loads(response.content)
        self.assertEqual(response_data['version'], schema.version + 1)
        # Reload schema from db; its next_version should have changed.
        schema = RecordSchema.objects.get(pk=schema.pk)
        self.assertEqual(unicode(schema.next_version.pk), response_data['uuid'])
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


class RecordTypeViewTestCase(AshlarAPITestCase):

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
        response_data = json.loads(response.content)
        self.assertEqual(response_data['current_schema'], str(record_schema.uuid), response_data)

        new_schema = dict(self.schema)
        new_schema['title'] = 'New Schema'
        new_record_schema = RecordSchema.objects.create(schema=new_schema,
                                                        version=2,
                                                        record_type=record_type)

        url = reverse('recordtype-detail', args=(record_type.pk,))
        response = self.client.get(url)
        response_data = json.loads(response.content)
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
        response_data = json.loads(response.content)
        self.assertEqual(response_data['current_schema'], str(record_schema.uuid), response_data)

        new_schema = dict(self.schema)
        new_schema['title'] = 'New Schema'
        new_record_schema = RecordSchema.objects.create(schema=new_schema,
                                                        version=2,
                                                        record_type=record_type)

        url = reverse('recordtype-detail', args=(record_type.pk,))
        response = self.client.get(url)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['current_schema'], str(new_record_schema.uuid), response_data)


class BoundaryViewTestCase(AshlarAPITestCase):

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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        boundary_uuid = response.data['uuid']
        boundary = Boundary.objects.get(uuid=boundary_uuid)
        self.assertGreater(boundary.polygons.count(), 0)

    def test_create_from_macosx_shapefile(self):
        """ Ensure __MACOSX files in archive don't wreck the upload """
        response = self.post_boundary('bayarea_macosx.zip')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        boundary_uuid = response.data['uuid']
        boundary = Boundary.objects.get(uuid=boundary_uuid)
        self.assertGreater(boundary.polygons.count(), 0)

    def test_boundary_crud(self):
        """ Already tested create, so don't bother, but test other operations """
        response = self.post_boundary('philly.zip')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
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

    def test_geojson_response(self):
        """ Create shape, then test that geojson serializes out properly """
        response = self.post_boundary('bayarea_macosx.zip')
        uuid = response.data['uuid']

        url = '{}geojson/'.format(reverse('boundary-detail', args=[uuid]))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'FeatureCollection')
        self.assertEqual(len(response.data['features']), 3)
