from jsonschema.exceptions import SchemaError


class SchemaException(SchemaError):
    """ Override SchemaError to provide an errors dict for restless error messages

    http://flask-restless.readthedocs.org/en/latest/customizing.html#capturing-validation-errors

    """
    def __init__(self, message):
        """ Create errors dict in constructor """
        super(SchemaException, self).__init__(message)
        self.errors = {
            self.__class__.__name__: self.message
        }
