import json
import sys

import dateutil.parser
import django
from django.utils import timezone
from django.contrib.gis.geos import Point
from rest_framework import status
if django.VERSION < (2, 0):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse

from grout import models, exceptions
from tests.api_test_case import GroutAPITestCase


class RecordValidationTestCase(GroutAPITestCase):
    """
    Test validation of new Records.
    """
    @classmethod
    def setUpClass(cls):
        super(RecordValidationTestCase, cls).setUpClass()

        # Create dummy data for a Point RecordType.
        cls.record_type = models.RecordType.objects.create(
            label='Point',
            plural_label='Points',
            geometry_type='point',
            temporal=True
        )
        cls.schema = {
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
        cls.record_schema = models.RecordSchema.objects.create(
            record_type=cls.record_type,
            version=1,
            schema=cls.schema
        )
        # The base endpoint for listing records.
        cls.record_endpt = reverse('record-list')

    def test_temporal_record_with_no_datetime_info(self):
        """
        Test that leaving out datetime information for a temporal Record
        raises an error.
        """
        data = {
            'schema': self.record_schema.uuid,
            'geom': 'POINT(0 0)',
            'archived': False,
            'data': {},
        }

        response = self.client.post(self.record_endpt, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

        min_msg = json.loads(response.content.decode('utf-8')).get('occurred_from')
        max_msg = json.loads(response.content.decode('utf-8')).get('occurred_to')
        expected_msg = exceptions.DATETIME_REQUIRED.format(uuid=self.record_type.uuid)

        self.assertEqual(min_msg, expected_msg, response.content)
        self.assertEqual(max_msg, expected_msg, response.content)

    def test_occurred_from_greater_than_occurred_to(self):
        """
        Test that if the value for `occurred_from` is greater than the value
        for `occurred_to` in a temporal Record, the API returns an error.
        """
        data = {
            'schema': self.record_schema.uuid,
            'occurred_from': dateutil.parser.parse('2018-08-01T00:00:00+00:00'),
            'occurred_to': dateutil.parser.parse('2015-01-01T00:00:00+00:00'),
            'geom': 'POINT(0 0)',
            'archived': False,
            'data': {},
        }

        response = self.client.post(self.record_endpt, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

        min_msg = json.loads(response.content.decode('utf-8')).get('occurred_from')
        max_msg = json.loads(response.content.decode('utf-8')).get('occurred_to')

        self.assertEqual(min_msg, exceptions.MIN_DATE_RANGE_ERROR, response.content)
        self.assertEqual(max_msg, exceptions.MAX_DATE_RANGE_ERROR, response.content)

    def test_invalid_schema(self):
        """
        Test that when a Record is created with data that doesn't match its
        schema, the API returns an error.
        """
        data = {
            'schema': self.record_schema.uuid,
            'occurred_from': timezone.now(),
            'occurred_to': timezone.now(),
            'geom': 'POINT(0 0)',
            'archived': False,
            'data': {
                'foo': 'bar',
                'baz': 'qux',
            },
        }

        response = self.client.post(self.record_endpt, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

        msg = json.loads(response.content.decode('utf-8')).get('data')

        if sys.version_info[0] == 3:
            expected_msg = exceptions.SCHEMA_MISMATCH_ERROR.format(
                uuid=self.record_schema.uuid,
                message="'id' is a required property"
            )
        else:
            # In Python 2, jsonschema uses the __repr__ method of the property
            # to embed it in the error string. This causes a slight difference
            # in the erorr message that gets passed along to the API.
            expected_msg = exceptions.SCHEMA_MISMATCH_ERROR.format(
                uuid=self.record_schema.uuid,
                message="u'id' is a required property"
            )

        self.assertEqual(msg, expected_msg, response.content)
