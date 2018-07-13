from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from grout.pagination import OptionalLimitOffsetPagination
from grout.models import RecordType

from tests.api_test_case import GroutAPITestCase


class PaginationTestCase(GroutAPITestCase):

    def setUp(self):
        super(PaginationTestCase, self).setUp()
        self.paginator = OptionalLimitOffsetPagination()
        self.queryset = RecordType.objects.all()

    def test_integer_limit(self):
        """Test that the user can specify an integer limit."""
        limit = 20
        request = Request(APIRequestFactory().get('/foo/?limit=%d' % limit))
        self.paginator.paginate_queryset(self.queryset, request)
        self.assertEqual(self.paginator.limit, limit)

    def test_get_all(self):
        """Test that the user can ask for 'all' records."""
        request = Request(APIRequestFactory().get('/foo/?limit=all'))
        self.paginator.paginate_queryset(self.queryset, request)

        # There are no RecordTypes, so the limit should be 0 + 1 = 1
        self.assertEqual(self.paginator.limit, 1)

    def test_missing_limit(self):
        """Test that when no limit is specified, the paginator returns a default limit."""
        request = Request(APIRequestFactory().get('/foo/'))
        limit = self.paginator.get_limit(request)
        self.assertEqual(limit, self.paginator.default_limit)

    def test_malformed_limit(self):
        """Test the case where the user requests a limit that does not parse."""
        request = Request(APIRequestFactory().get('/foo/?limit=foobar'))
        limit = self.paginator.get_limit(request)
        self.assertEqual(limit, self.paginator.default_limit)
