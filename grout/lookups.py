# -*- coding: utf-8 -*-
import json
import re
import shlex

from django.db.models import Lookup
from django.contrib.postgres.fields import JSONField


class FilterTree(object):
    """
    This class exposes methods for parsing a JSONB query from the Django ORM
    and building a corresponding SQL query.

    Manual filtering by way of Django's ORM might look like:
    Something.objects.filter(<jsonb_field>__jsonb=<filter_specification>)

    Check out the jsonb_field_testing test module for some real examples.
    """
    def __init__(self, tree, field):
        self.field = field  # The JSONField to filter on.
        self.tree = tree  # The nested dictionary representing the query.

        # Map the available filter types to their corresponding classmethod.
        self.sql_generators = {
            "intrange": self.intrange_filter,
            "containment": self.containment_filter,
            "containment_multiple": self.multiple_containment_filter
        }

        self.rules = self.get_rules(self.tree)  # Parse and save the query directive.

    def is_rule(self, obj):
        """
        Check to see if a dictionary is formatted as a query "rule". This method
        is useful for checking to see whether the recursion has bottomed
        out in `get_rules`.

        Args:
            obj (dict): The dictionary that should be checked for ruleness.

        Returns:
            bool: True if the dict is a rule, False otherwise.
        """
        if '_rule_type' in obj and obj['_rule_type'] in self.sql_generators:
            return True
        return False

    def get_rules(self, obj, current_path=[]):
        """
        Recursively crawl a dictionary to look for filtering rules.

        Args:
            obj (dict): The dictionary to be crawled.
            current_path (list): The branch of the tree leading up to this point.

        Returns:
            list: A list of two-tuples representing query rules. The first element
                  will be the path to the value in question, while the second
                  element will be the rule to apply for the filter.
        """
        # If node isn't a rule or dictionary
        if type(obj) != dict:
            return []

        # If node is a rule return its location and its details
        if self.is_rule(obj):
            return [([self.field] + current_path, obj)]

        rules = []
        for path, val in obj.items():
            rules = rules + self.get_rules(val, current_path + [path])
        return rules

    def sql(self):
        """
        Produce output that can be compiled into SQL by Django and psycopg2.

        Returns:
            A tuple of a (template) string followed by a list
            of parameters for compiling that template. (This is the output that
            Django expects for compiling a SQL query.)
        """
        rule_specs = []

        patterns = {}
        pattern_specs = []

        # It's safe to unpack `self.get_rules` because it can only
        # return A) an empty list or B) a list of two-tuples with two elements in
        # them (the path and the rule for each query directive).
        for path, rule in self.rules:
            # Don't parse if this is not a properly registered rule type.
            if not self.is_rule(rule):
                pass
            rule_type = rule['_rule_type']
            sql_tuple = self.sql_generators[rule_type](path, rule)
            if sql_tuple is not None:
                rule_specs.append(sql_tuple)

            # The check on 'pattern' here allows us to apply a pattern filter on top of others
            if 'pattern' in rule:
                # Don't filter as an exact match on the text entered; match per word.
                for pattern in shlex.split(rule['pattern']):
                    if rule['_rule_type'] == 'containment_multiple':
                        sql_tuple = FilterTree.text_similarity_filter(path, pattern, True)
                    else:
                        sql_tuple = FilterTree.text_similarity_filter(path, pattern, False)
                    # add to the list of rules generated for this pattern (one per field)
                    patterns.setdefault(pattern, []).append(sql_tuple)

        rule_string = ' AND '.join([rule[0] for rule in rule_specs])

        pattern_rules = patterns.values()
        pattern_strings = []

        # check if any of the fields for this string pattern match
        for rule_list in pattern_rules:
            pattern_strings.append(' OR '.join([rule[0] for rule in rule_list]))
            pattern_specs += rule_list

        # check that record has a match for all of the string patterns in some field
        pattern_string = '(' + ') AND ('.join(pattern_strings) + ')' if pattern_strings else ''

        if rule_string != '' and pattern_string != '':
            filter_string = '(' + (' AND ('.join([rule_string, pattern_string])) + ')' + ')'
        elif rule_string != '' or pattern_string != '':
            filter_string = '(' + ''.join([rule_string, pattern_string]) + ')'
        else:
            filter_string = ''

        # flatten the rule_paths
        rule_paths_first = ([rule[1] for rule in rule_specs] +
                            [rule[1] for rule in pattern_specs])
        rule_paths = [item for sublist in rule_paths_first
                      for item in sublist]

        outcome = (filter_string, tuple(rule_paths))
        return outcome

    # Filters
    @classmethod
    def containment_filter(cls, path, rule):
        """
        Filter for objects that match the `rule` at some location `path` in
        a Record object.

        Registered on the 'contains' rule type.

        Args:
            path (list): A list of keys representing the path to the field in question,
                         with keys stored from deepest to shallowest.
            rule (dict): A dictionary representing the rule to apply.

        Returns:
            tuple: Information for building a SQL query from this filter rule,
                   with the containment query in the first position and the
                   parameters in the second.
        """
        # The `path` dict stores the full branch that leads to the value in
        # question, from leaf to root.
        leaf, branch = path[0], path[1:]

        template = reconstruct_object(branch)
        has_containment = 'contains' in rule
        abstract_contains_str = leaf + " @> %s"

        if has_containment:
            all_contained = rule.get('contains')
        else:
            return None

        contains_params = []
        json_path = [json.dumps(x) for x in branch]
        for contained in all_contained:
            interpolants = tuple(json_path + [json.dumps(contained)])
            contains_params.append(template % interpolants)

        contains_str = ' OR '.join([abstract_contains_str] * len(all_contained))

        if contains_str != '':
            return ('(' + contains_str + ')', contains_params)
        else:
            return None

    @classmethod
    def multiple_containment_filter(cls, path, rule):
        """
        Filter for objects that match the specified `rule` in any of the objects in a
        given list.

        Registered on the 'containment_multiple' rule type.

        Args:
            path (list): A list of keys representing the path to the field in question,
                         with keys stored from deepest to shallowest.
            rule (dict): A dictionary representing the rule to apply.

        Returns:
            tuple: Information for building a SQL query from this filter rule,
                   with the containment query in the first position and the
                   parameters in the second.
        """
        # The `path` dict stores the full branch that leads to the value in
        # question, from leaf to root.
        leaf, branch = path[0], path[1:]

        template = reconstruct_object_multiple(branch)
        has_containment = 'contains' in rule
        abstract_contains_str = leaf + " @> %s"

        if has_containment:
            all_contained = rule.get('contains')
        else:
            return None

        contains_params = []
        json_path = [json.dumps(x) for x in branch]
        for contained in all_contained:
            interpolants = tuple(json_path + [json.dumps(contained)])
            contains_params.append(template % interpolants)

        contains_str = ' OR '.join([abstract_contains_str] * len(all_contained))

        if contains_str != '':
            return ('(' + contains_str + ')', contains_params)
        else:
            return None

    @classmethod
    def intrange_filter(cls, path, rule):
        """
        Filter for numbers that match boundaries provided by a rule.

        Registered on the 'intrange' rule type.

        Args:
            path (list): A list of keys representing the path to the field in question,
                         with keys stored from deepest to shallowest.
            rule (dict): A dictionary representing the rule to apply.

        Returns:
            tuple: Information for building a SQL query from this filter rule,
                   with the containment query in the first position and the
                   parameters in the second.
        """
        traversed_int = "(" + extract_value_at_path(path) + ")::int"
        has_min = 'min' in rule and rule['min'] is not None
        has_max = 'max' in rule and rule['max'] is not None

        if has_min:
            minimum = rule['min']
            more_than = ("{traversal_int} >= %s"
                         .format(traversal_int=traversed_int))
        if has_max:
            maximum = rule['max']
            less_than = ("{traversal_int} <= %s"
                         .format(traversal_int=traversed_int))

        # The `path` dict stores the full branch that leads to the value in
        # question, from leaf to root.
        branch = path[1:]

        if has_min and not has_max:
            sql_template = '(' + more_than + ')'
            return (sql_template, branch + [minimum])
        elif has_max and not has_min:
            sql_template = '(' + less_than + ')'
            return (sql_template, branch + [maximum])
        elif has_max and has_min:
            sql_template = '(' + less_than + ' AND ' + more_than + ')'
            return (sql_template, branch + [maximum] + branch + [minimum])
        else:
            return None

    @classmethod
    def text_similarity_filter(cls, path, pattern, path_multiple=False):
        """
        Filter for objects that contain members (at the specified addresses)
        which match against a provided pattern.

        Args:
            path (list): A list of keys representing the path to the field in question,
                         with keys stored from deepest to shallowest.
            pattern (str): A regex pattern to use for the filter.
            path_multiple (bool):  If true, this function generates a regular expression to parse
                                   the json array of objects. This regular expression works by
                                   finding the key and attempting to match a string against that
                                   key's associated value. This unfortunate use of regex is
                                   necessitated by Postgres' inability to iterate in a WHERE clause
                                   and the requirement that we deal with records that have multiple
                                   related objects.

        Returns:
            tuple: Information for building a SQL query from this filter rule,
                   with the containment query in the first position and the
                   parameters in the second.
        """
        has_similarity = pattern is not None
        if not has_similarity:
            return None

        if path_multiple:
            traversed_text = "(" + extract_value_at_path(path[:-1]) + ")"
        else:
            traversed_text = "(" + extract_value_at_path(path) + ")"

        sql_template = ("{traversed_text}::text ~* %s"
                        .format(traversed_text=traversed_text))

        if path_multiple:
            return (sql_template, path[1:-1] + ['{key}": "([^"]*?{val}.*?)"'
                                                .format(key=re.escape(path[-1]),
                                                        val=re.escape(pattern))])
        else:
            return (sql_template, path[1:] + [re.escape(pattern)])


# Utility functions
def extract_value_at_path(path):
    return operator_at_traversal_path(path, '->>')


# N.B. This only returns useful query snippets if the parent path
# exists. That is, if you try to query "a"->"b"?"c" but your objects don't have a
# "b" key, you will always get zero rows back, whereas if they do have a "b" key, then
# you will get true if it contains "c" and false otherwise.
def contains_key_at_path(path):
    return operator_at_traversal_path(path, '?')


def operator_at_traversal_path(path, op):
    """
    Construct traversal instructions for Postgres from a list of nodes; apply op as last step
    like: '%s->%S->%s->>%s' for path={a: {b: {c: value } } }, op='->>'

    Don't use this unless extract_value_at_path and contains_key_at_path don't work for you.
    """
    fmt_strs = [path[0]] + ['%s' for leaf in path[1:]]
    traversal = '->'.join(fmt_strs[:-1]) + '{op}%s'.format(op=op)
    return traversal


def reconstruct_object(path):
    """
    Reconstruct the object from root to leaf, recursively.
    """
    if len(path) == 0:
        return '%s'
    else:
        # The indexed query on `path` below is the means by which we recurse
        #  Every iteration pushes it closer to a length of 0 and, thus, bottoming out
        return '{{%s: {recons}}}'.format(recons=reconstruct_object(path[1:]))


def reconstruct_object_multiple(path):
    """
    Reconstruct the object from root to leaf, recursively.
    """
    if len(path) == 0:
        return '%s'
    elif len(path) == 2:
        return '{{%s: [{recons}]}}'.format(recons=reconstruct_object_multiple(path[1:]))
    else:
        # The indexed query on `path` below is the means by which we recurse
        #  Every iteration pushes it closer to a length of 0 and, thus, bottoming out
        #  This function differs from the singular reconstruction in that the final object
        #  gets wrapped in a list (when length is 2, there should be a key and a value left)
        return '{{%s: {recons}}}'.format(recons=reconstruct_object_multiple(path[1:]))


@JSONField.register_lookup
class JSONLookup(Lookup):
    """
    A custom lookup using the FilterTree to implement nested queries for JSONFields.
    """
    lookup_name = 'jsonb'

    def as_sql(self, qn, connection):
        """
        Override the Lookup method that creates the SQL query. See Django's
        documentation for information about the parameters:
        https://docs.djangoproject.com/en/dev/howto/custom-lookups/
        """
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)

        field = lhs
        # JSONField formats query values for the database by wrapping them psycopg2's
        # JsonAdapter, but we need the raw Python dict so that we can parse the
        # query tree. Intercept the query parameter (it'll always be the first
        # element in the parameter list, since the custom jsonb filter only accepts one argument)
        # and revert it back to a Python dict for tree parsing.
        tree = rhs_params[0].adapted

        return FilterTree(tree, field).sql()
