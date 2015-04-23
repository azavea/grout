import django_filters

from rest_framework_gis.filterset import GeoFilterSet

from ashlar.models import Boundary, Record


class RecordFilter(GeoFilterSet):

    class Meta:
        model = Record


class BoundaryFilter(GeoFilterSet):

    STATUS_SET = {status[0] for status in Boundary.StatusTypes.CHOICES}

    status = django_filters.MethodFilter(name='status', action='multi_filter_status')

    def multi_filter_status(self, queryset, value):
        """ Method filter for multiple choice query on status

        e.g. /api/boundary/?status=ERROR,WARNING

        """
        statuses = value.split(',')
        statuses = set(statuses) & self.STATUS_SET
        return queryset.filter(status__in=statuses)

    class Meta:
        model = Boundary
        fields = ['status']
