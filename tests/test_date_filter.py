from dateutil.parser import parse
import json

import mock

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.http import HttpRequest

from rest_framework.test import APIRequestFactory, force_authenticate


from grout import models
from grout.views import RecordViewSet
from grout.exceptions import QueryParameterException, DATETIME_FORMAT_ERROR


class DateFilterBackendTestCase(TestCase):
    """ Test serializer field for dates """

    def setUp(self):
        try:
            self.user = User.objects.get(username='admin')
        except ObjectDoesNotExist:
            self.user = User.objects.create_user('admin',
                                                 'grout@azavea.com',
                                                 '123')

        self.factory = APIRequestFactory()

        self.item_type = models.RecordType.objects.create(label='item', plural_label='items')

        self.item_schema = {
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

        self.schema = models.RecordSchema.objects.create(record_type=self.item_type,
                                                  version=1,
                                                  schema=self.item_schema)

        # Define three chronological points in time in order to test range filtering.
        self.a_date = parse('2015-01-01T00:00:00+00:00')
        self.a_later_date = parse('2015-02-22T00:00:00+00:00')
        self.an_even_later_date = parse('2018-07-30T00:00:00+00:00')

        # The first Record spans the first and second points in time.
        self.early_record = models.Record.objects.create(
            occurred_from=self.a_date,
            occurred_to=self.a_later_date,
            geom='POINT (0 0)',
            schema=self.schema,
            data={}
        )
        # The second Record spans the second and third points in time.
        self.later_record = models.Record.objects.create(
            occurred_from=self.a_later_date,
            occurred_to=self.an_even_later_date,
            geom='POINT (0 0)',
            schema=self.schema,
            data={}
        )

        # Create Records for a nontemporal RecordType.
        self.nontemporal_record_type = models.RecordType.objects.create(
            label='Nontemporal',
            plural_label='Nontemporals',
            temporal=False
        )
        self.nontemporal_schema = models.RecordSchema.objects.create(
            record_type=self.nontemporal_record_type,
            version=1,
            schema={}
        )
        self.nontemporal_record = models.Record.objects.create(
            schema=self.nontemporal_schema,
            geom='POINT (0 0)',
            data={}
        )

        self.view = RecordViewSet.as_view({'get': 'list'})

    def test_valid_datefilter(self):
        """ Test filtering on dates """
        req1 = self.factory.get('/foo/', {'occurred_min': self.a_date})
        force_authenticate(req1, self.user)
        res1 = self.view(req1).render()
        expected_count1 = len([self.early_record, self.later_record])
        self.assertEqual(json.loads(res1.content.decode('utf-8'))['count'], expected_count1)

        req2 = self.factory.get('/foo/', {'occurred_min': self.a_later_date})
        force_authenticate(req2, self.user)
        res2 = self.view(req2).render()
        expected_count2 = len([self.later_record])
        self.assertEqual(json.loads(res2.content.decode('utf-8'))['count'], expected_count2)

        req3 = self.factory.get('/foo/', {'occurred_max': self.a_date})
        force_authenticate(req3, self.user)
        res3 = self.view(req3).render()
        expected_count3 = len([])
        self.assertEqual(json.loads(res3.content.decode('utf-8'))['count'], expected_count3)

        req4 = self.factory.get('/foo/', {'occurred_max': self.a_later_date})
        force_authenticate(req4, self.user)
        res4 = self.view(req4).render()
        expected_count4 = len([self.early_record])
        self.assertEqual(json.loads(res4.content.decode('utf-8'))['count'], expected_count4)

        req5 = self.factory.get('/foo/', {'occurred_min': self.a_date,
                                          'occurred_max': self.a_later_date})
        force_authenticate(req5, self.user)
        res5 = self.view(req5).render()
        expected_count5 = len([self.early_record])
        self.assertEqual(json.loads(res5.content.decode('utf-8'))['count'], 1)

    def test_missing_min_max(self):
        """
        Test that forgetting both `occurred_min` and `occurred_max` returns all records,
        including the nontemporal record.
        """
        missing_range_req = self.factory.get('/foo/')
        force_authenticate(missing_range_req, self.user)
        missing_range_res = self.view(missing_range_req).render()

        self.assertEqual(json.loads(missing_range_res.content.decode('utf-8'))['count'], 3)

    def test_missing_timezone(self):
        """Test that forgetting timezone information raises an error."""
        date_no_time = '2015-01-01'
        missing_tz_req = self.factory.get('/foo/', {'occurred_max': date_no_time})
        force_authenticate(missing_tz_req, self.user)
        missing_tz_res = self.view(missing_tz_req).render()

        self.assertEqual(str(json.loads(missing_tz_res.content.decode('utf-8'))['detail']),
                         str(QueryParameterException('occurred_max', DATETIME_FORMAT_ERROR)))

    def test_range_parse_errors(self):
        """Test that parse errors get thrown when the date range is improperly formatted."""
        # Test a bad `occurred_min` parameter.
        bad_min_req = self.factory.get('/foo/', {'occurred_min': 'foobarbaz'})
        force_authenticate(bad_min_req, self.user)
        bad_min_res = self.view(bad_min_req).render()

        self.assertEqual(str(json.loads(bad_min_res.content.decode('utf-8'))['detail']),
                         str(QueryParameterException('occurred_min', DATETIME_FORMAT_ERROR)))

        # Test a bad `occurred_max` parameter.
        bad_max_req = self.factory.get('/foo/', {'occurred_max': 'foobarbaz'})
        force_authenticate(bad_max_req, self.user)
        bad_max_res = self.view(bad_max_req).render()

        self.assertEqual(str(json.loads(bad_max_res.content.decode('utf-8'))['detail']),
                         str(QueryParameterException('occurred_max', DATETIME_FORMAT_ERROR)))
