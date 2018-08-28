import json

import mock
from dateutil.parser import parse
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.http import HttpRequest

from rest_framework.test import APIRequestFactory, force_authenticate

from grout import models
from grout.views import RecordViewSet
from grout.exceptions import (QueryParameterException,
                              DATETIME_FORMAT_ERROR,
                              MIN_DATE_RANGE_FILTER_ERROR,
                              MAX_DATE_RANGE_FILTER_ERROR)


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

        self.schema = models.RecordSchema.objects.create(
            record_type=self.item_type,
            version=1,
            schema={}
        )

        # Define five chronological points in time in order to test range filtering.
        self.min_date = parse('2015-01-01T00:00:00+00:00')
        self.lower_quartile_date = parse('2015-01-15T00:00:00+00:00')
        self.mid_date = parse('2015-02-22T00:00:00+00:00')
        self.upper_quartile_date = parse('2018-07-30T00:00:00+00:00')
        self.max_date = parse('2018-08-01T00:00:00+00:00')

        # The first Record spans the first and second points in time.
        self.min_to_mid_date_record = models.Record.objects.create(
            occurred_from=self.min_date,
            occurred_to=self.mid_date,
            geom='POINT (0 0)',
            schema=self.schema,
            data={}
        )
        # The second Record spans the second and third points in time.
        self.mid_to_max_date_record = models.Record.objects.create(
            occurred_from=self.mid_date,
            occurred_to=self.max_date,
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
        # Define a set of filters along with the records that they should match.
        tests = [
            {
                'filters': {'occurred_min': 'min_date'},
                'matches': ['min_to_mid_date_record', 'mid_to_max_date_record']
            },
            {
                'filters': {'occurred_min': 'upper_quartile_date'},
                'matches': ['mid_to_max_date_record']
            },
            {
                'filters': {'occurred_max': 'min_date'},
                'matches': ['min_to_mid_date_record']
            },
            {
                'filters': {'occurred_max': 'mid_date'},
                'matches': ['min_to_mid_date_record', 'mid_to_max_date_record']
            },
            {
                'filters': {
                    'occurred_min': 'min_date',
                    'occurred_max': 'lower_quartile_date'
                },
                'matches': ['min_to_mid_date_record']
            },
            {
                'filters': {
                    'occurred_min': 'upper_quartile_date',
                    'occurred_max': 'max_date'
                },
                'matches': ['mid_to_max_date_record']
            },
            {
                'filters': {
                    'occurred_min': 'lower_quartile_date',
                    'occurred_max': 'upper_quartile_date'
                },
                'matches': ['min_to_mid_date_record', 'mid_to_max_date_record']
            },
            {
                'filters': {
                    'occurred_min': 'min_date',
                    'occurred_max': 'max_date'
                },
                'matches': ['min_to_mid_date_record', 'mid_to_max_date_record']
            },
        ]

        # For each filters/matches pair, test to make sure that the date filters
        # performs correctly.
        for test in tests:
            filters = {key: getattr(self, val) for key, val in test['filters'].items()}
            req = self.factory.get('/foo/', filters)
            expected_count = len(test['matches'])
            force_authenticate(req, self.user)
            res = self.view(req).render()
            self.assertEqual(json.loads(res.content.decode('utf-8')).get('count'),
                             expected_count,
                             test)

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

        # Both values have to be strings in order for the exception to fit
        # the equality test.
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

    def test_invalid_range(self):
        """
        Test that min > max raises an error when both ends of the date range
        filter are provided.
        """
        min_gt_max = {
            'occurred_min': self.max_date,
            'occurred_max': self.min_date
        }
        min_gt_max_req = self.factory.get('/foo/', min_gt_max)
        force_authenticate(min_gt_max_req, self.user)
        min_gt_max_res = self.view(min_gt_max_req).render()
        self.assertEqual(str(json.loads(min_gt_max_res.content.decode('utf-8')).get('occurred_min')),
                         MIN_DATE_RANGE_FILTER_ERROR,
                         min_gt_max_res.content)
        self.assertEqual(str(json.loads(min_gt_max_res.content.decode('utf-8')).get('occurred_max')),
                         MAX_DATE_RANGE_FILTER_ERROR,
                         min_gt_max_res.content)
