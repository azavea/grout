from rest_framework import status
from rest_framework.exceptions import APIException


class QueryParameterException(APIException):
    """Exception raised when a get parameter does not satisfy requirements"""

    def __init__(self, query_parameter, requirement, status_code=status.HTTP_400_BAD_REQUEST):
        """
        :param query_parameter: message provided to user about error
        :param requirement: requirement parameter must satisfy (e.g. 'must be integer')
        :param status_code: http status for error
        """
        self.detail = (u'Invalid value for parameter %s, value must be %s'
                       % (query_parameter, requirement))
        self.status_code = status_code

        def __str__(self):
            return repr(self.detail)


SCHEMA_MISMATCH_ERROR = ("Schema validation failed for RecordSchema {uuid}: " +
                         "{message}")
GEOMETRY_TYPE_ERROR = ("Incoming Record geometry '{incoming}' does not match the " +
                       "expected geometry type '{expected}' of the RecordType {uuid}.")
DATETIME_NOT_PERMITTED = ("This field is not permitted for Records of RecordType {uuid}. " +
                          "Please remove this field, or update the RecordType to set " +
                          "the `temporal` flag to True")
DATETIME_REQUIRED = ("This field is required for all Records of RecordType {uuid}. " +
                     "Please include this field, or update the RecordType to set " +
                     "the `temporal` flag to False.")
DATETIME_FORMAT_ERROR = ('ISO 8601 formatted with timezone information. Please check ' +
                         'that the URL is properly encoded.')
BASE_MIN_DATE_RANGE_ERROR = "Value must be the same or earlier than '{max}'."
BASE_MAX_DATE_RANGE_ERROR = "Value must be the same or later than '{min}'."

# Date range errors for the Record model fields (occurred_from and occurred_to).
MIN_DATE_RANGE_ERROR = BASE_MIN_DATE_RANGE_ERROR.format(max='occurred_to')
MAX_DATE_RANGE_ERROR = BASE_MAX_DATE_RANGE_ERROR.format(min='occurred_from')

# Date range errors for the Record filters (occurred_min and occurred_max).
MIN_DATE_RANGE_FILTER_ERROR = BASE_MIN_DATE_RANGE_ERROR.format(max='occurred_max')
MAX_DATE_RANGE_FILTER_ERROR = BASE_MAX_DATE_RANGE_ERROR.format(min='occurred_min')
