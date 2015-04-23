import os

from django.core.urlresolvers import reverse

from rest_framework import status

from ashlar.models import Boundary
from api.tests.api_test_case import AshlarAPITestCase


class BoundaryViewTestCase(AshlarAPITestCase):

    def setUp(self):
        super(BoundaryViewTestCase, self).setUp()

        self.boundary1 = Boundary.objects.create(label='foo', source_file='foo.zip',
                                            status=Boundary.StatusTypes.ERROR)
        self.boundary2 = Boundary.objects.create(label='fooOK', source_file='foo.zip',
                                            status=Boundary.StatusTypes.COMPLETE)

    def test_list_no_geom_field(self):
        """ Ensure geom not in boundary list view """
        url = reverse('boundary-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        boundary = response.data['results'][0]
        self.assertNotIn('geom', boundary.keys())

    def test_get_geom_field(self):
        """ Ensure geom field in boundary detail view """
        url = reverse('boundary-detail', args=[self.boundary1.uuid])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('geom', response.data.keys())

    def test_status_get_filter(self):
        url = '{}?status={}'.format(reverse('boundary-list'), Boundary.StatusTypes.COMPLETE)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only one of the boundaries has status = COMPLETE
        self.assertEqual(len(response.data['results']), 1)
        boundary = response.data['results'][0]
        self.assertEqual(boundary['status'], Boundary.StatusTypes.COMPLETE)

    def test_create_adds_geom_from_valid_shapefile(self):
        zipfile = open(os.path.join(self.files_dir, 'philly.zip'), 'rb')
        data = {
            'errors': '',
            'label': 'foobar',
            'source_file': zipfile
        }
        url = reverse('boundary-list')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('geom', response.data.keys())
        self.assertIsNotNone(response.data['geom'])

    def test_create_from_macosx_shapefile(self):
        """ Ensure __MACOSX files in archive don't wreck the upload """
        zipfile = open(os.path.join(self.files_dir, 'bayarea_macosx.zip'), 'rb')
        data = {
            'errors': '',
            'label': 'foobar',
            'source_file': zipfile
        }
        url = reverse('boundary-list')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('geom', response.data.keys())
        self.assertIsNotNone(response.data['geom'])