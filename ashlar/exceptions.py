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
