from django import get_version
from django.db.models import Lookup

from django_pgjson.fields import JsonBField

class JsonBExistsLookup(Lookup):
    """
    jsonb-specific existence lookup that can be used as follows::
        YourModel.objects.filter(data__jexists='author')
    This will be translated into the following SQL::
        select * from yourmodel where data ? "author"
    Such queries can be accelerated by GiN indices on the jsonb field in
    question.
    :author: Andrew Fink
    """

    # ideally we would call this 'contains'. However, in Django 'contains'
    # lookups are explicitly handled by LIKE queries, and the
    # Field.get_db_prep_lookup will then prepare your data for a DB LIKE query
    # breaking our jsonb containment query. -- cpb
    lookup_name = 'jexists'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return "{0} ? {1}".format(lhs, rhs), params


if get_version() >= '1.7':
    JsonBField.register_lookup(JsonBExistsLookup)