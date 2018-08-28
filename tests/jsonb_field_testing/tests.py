# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import
from django.test import TestCase

from jsonb_field_testing.models import JsonBModel

from grout.lookups import (FilterTree,
                           extract_value_at_path,
                           contains_key_at_path)


class JsonBFilterTests(TestCase):
    def setUp(self):
        self.mock_rule = {'_rule_type': 'sort of a cheat'}
        self.mock_int_rule = {'_rule_type': 'intrange', 'min': 1, 'max': 5}
        self.mock_contains_rule = {'_rule_type': 'containment', 'contains': ['test1', 'a thing']}

        self.two_rules = {'testing': self.mock_int_rule,
                          'alpha': {'beta': {'gamma': {'delta': self.mock_rule},
                                    'distraction': []}}}
        self.two_rule_tree = FilterTree(self.two_rules, 'data')

        self.containment_object = {'a': {'b': {'c': self.mock_contains_rule}}}
        self.containment_tree = FilterTree(self.containment_object, 'data')

        self.distraction = {'alpha': {'beta': {'gamma': {'delta': self.mock_int_rule},
                                               'distraction': []}}}
        self.distraction_tree = FilterTree(self.distraction, 'data')

    def test_value_extraction_generation(self):
        self.assertEqual(extract_value_at_path(['a', 'b', 'c']), u"a->%s->>%s")

    def test_key_containment_generation(self):
        self.assertEqual(contains_key_at_path(['a', 'b', 'c']), u"a->%s?%s")

    def test_intrange_rules(self):
        self.assertEqual(self.two_rule_tree.rules, [(['data', 'testing'], self.mock_int_rule)])
        self.assertEqual(self.distraction_tree.rules,
                         [(['data', 'alpha', 'beta', 'gamma', 'delta'], self.mock_int_rule)])

    def test_containment_rules(self):
        self.assertEqual(self.containment_tree.rules,
                         [(['data', 'a', 'b', 'c'], self.mock_contains_rule)])

    def test_intrange_sql(self):
        self.assertEqual(self.two_rule_tree.sql(),
                         (u'(((data->>%s)::int <= %s AND (data->>%s)::int >= %s))',
                         ('testing', 5, 'testing', 1)))
        self.assertEqual(self.distraction_tree.sql(),
                         ('(((data->%s->%s->%s->>%s)::int <= %s AND (data->%s->%s->%s->>%s)::int >= %s))',
                         ('alpha', 'beta', 'gamma', 'delta', 5, 'alpha', 'beta', 'gamma', 'delta', 1)))

    def test_containment_sql(self):
        self.assertEqual(self.containment_tree.sql(),
                         ("((data @> %s OR data @> %s))",
                         ('{"a": {"b": {"c": "test1"}}}', '{"a": {"b": {"c": "a thing"}}}')))

    def test_containment_output(self):
        self.assertEqual(FilterTree.containment_filter(['a', 'b'], self.mock_contains_rule),
                         ('(a @> %s OR a @> %s)',
                          ['{"b": "test1"}', '{"b": "a thing"}']))

    def test_containment_query(self):
        JsonBModel.objects.create(data={'a': {'b': {'c': 1}}})
        JsonBModel.objects.create(data={'a': {'b': {'c': 2000}}})

        filt = {'a': {'b': {'c': {'_rule_type': 'containment', 'contains': [1, 2, 3]}}}}
        query = JsonBModel.objects.filter(data__jsonb=filt)
        self.assertEqual(query.count(), 1)

        filt2 = {'a': {'b': {'c': {'_rule_type': 'containment', 'contains': [1, 2000, 3]}}}}
        query2 = JsonBModel.objects.filter(data__jsonb=filt2)
        self.assertEqual(query2.count(), 2)

    def test_intrange_query(self):
        JsonBModel.objects.create(data={'a': {'b': {'c': 1}}})
        JsonBModel.objects.create(data={'a': {'b': {'c': 2000}}})

        filt = {'a': {'b': {'c': {'_rule_type': 'intrange', 'min': 1, 'max': 5}}}}
        query = JsonBModel.objects.filter(data__jsonb=filt)
        self.assertEqual(query.count(), 1)

        filt2 = {'a': {'b': {'c': {'_rule_type': 'intrange', 'min': 1, 'max': 2005}}}}
        query2 = JsonBModel.objects.filter(data__jsonb=filt2)
        self.assertEqual(query2.count(), 2)

    def test_multiple_filters(self):
        """This test depends on all of the logic for containment and intrange and uses both in
        the same query
        """
        JsonBModel.objects.create(data={'a': {'b': {'c': 1, 'd': 25}}})
        JsonBModel.objects.create(data={'a': {'b': {'c': 2000, 'd': 9000}}})

        filt1 = {'a': {'b': {'c': {'_rule_type': 'intrange',
                                   'min': 1, 'max': 5},
                             'd': {'_rule_type': 'containment',
                                   'contains': [0, 25, 92, 23, 44, 123, 21, 32,
                                                12, 32, 42, 12, 23123, 213, 23,
                                                421, 123, 12]}}}}
        query1 = JsonBModel.objects.filter(data__jsonb=filt1)
        self.assertEqual(query1.count(), 1)

        filt2 = filt1.copy()
        filt2['a']['b']['d']['contains'].append(9000)
        query2 = JsonBModel.objects.filter(data__jsonb=filt2)
        self.assertEqual(query2.count(), 1)

        filt3 = filt2.copy()
        filt3['a']['b']['c']['max'] = 9000
        query3 = JsonBModel.objects.filter(data__jsonb=filt3)
        self.assertEqual(query3.count(), 2)

    def test_multiple_containment_filters(self):
        JsonBModel.objects.create(data={'a': {'b': {'c': "zog", 'd': "zog"}}})
        JsonBModel.objects.create(data={'a': {'b': {'c': "zog", 'd': 9000}}})

        filt1 = {'a': {'b': {'c': {'_rule_type': 'containment',
                                   'contains': ['zog']},
                             'd': {'_rule_type': 'containment',
                                   'contains': ['zog']}}}}

        query1 = JsonBModel.objects.filter(data__jsonb=filt1)
        self.assertEqual(query1.count(), 1)

        filt2 = filt1.copy()
        del filt2['a']['b']['d']
        query2 = JsonBModel.objects.filter(data__jsonb=filt2)
        self.assertEqual(query2.count(), 2)

    def test_multiple_containment_multiple_filters(self):
        """Test for filters on data which has a list of objects to check"""
        JsonBModel.objects.create(data={'a': {'b': [{'c': "zog"}, {'c': "dog"}]}})
        JsonBModel.objects.create(data={'a': {'b': [{'c': "zog"}, {'c': 9000}]}})

        filt1 = {'a': {'b': {'c': {'_rule_type': 'containment_multiple',
                                   'contains': ['dog']}}}}

        query1 = JsonBModel.objects.filter(data__jsonb=filt1)
        self.assertEqual(query1.count(), 1)

        filt2 = {'a': {'b': {'c': {'_rule_type': 'containment_multiple',
                                   'contains': ['zog', 'dog']}}}}
        query2 = JsonBModel.objects.filter(data__jsonb=filt2)
        self.assertEqual(query2.count(), 2)

    def test_text_similarity_filter(self):
        JsonBModel.objects.create(data={'a': {'b': {'c': "beagels"}}})
        JsonBModel.objects.create(data={'a': {'b': {'c': "beegles"}}})
        filt1 = {'a': {'b': {'c': {'_rule_type': 'containment',
                                   'pattern': 'a'}}}}
        query1 = JsonBModel.objects.filter(data__jsonb=filt1)
        self.assertEqual(query1.count(), 1)

    def test_text_similarity_split_spaces(self):
        """Test that similarity patterns are split on spaces before filtering"""
        JsonBModel.objects.create(data={'a': {'b': {'c': "goose meese moose"}}})
        JsonBModel.objects.create(data={'a': {'b': {'c': "moose geese goose"}}})
        filt1 = {'a': {'b': {'c': {'_rule_type': 'containment',
                                   'pattern': 'moose goose'}}}}
        query1 = JsonBModel.objects.filter(data__jsonb=filt1)
        self.assertEqual(query1.count(), 2)

    def test_text_similarity_multiple(self):
        JsonBModel.objects.create(data={'a': {'b': [{'c': "beegels"}, {'c': "beagels"}]}})
        JsonBModel.objects.create(data={'a': {'b': [{'c': "beegles"}]}})
        filt1 = {'a': {'b': {'c': {'_rule_type': 'containment_multiple',
                                   'pattern': 'a'}}}}
        query1 = JsonBModel.objects.filter(data__jsonb=filt1)
        self.assertEqual(query1.count(), 1)

    def test_tricky_key_similarity_multiple(self):
        JsonBModel.objects.create(data={'a': {'b': [{'beagels': "beegels"}, {'beagels': "beagels"}]}})
        JsonBModel.objects.create(data={'a': {'b': [{'beagels': "beegles", "arg": "zonk"}]}})
        filt1 = {'a': {'b': {'beagels': {'_rule_type': 'containment_multiple',
                                         'pattern': 'a'}}}}
        query1 = JsonBModel.objects.filter(data__jsonb=filt1)
        self.assertEqual(query1.count(), 1)

    def test_containment_use_with_pattern_match(self):
        JsonBModel.objects.create(data={'a': {'b': {'beagels': "beegels"},
                                              'c': {'rhymes': 'seeds'}}})
        JsonBModel.objects.create(data={'a': {'b': {'beagels': "bgels"},
                                              'c': {'rhymes': 'seeds'}}})

        filt = {'a': {'b': {'beagels': {'_rule_type': 'containment',
                                        'pattern': 'gel'}},
                      'c': {'rhymes': {'_rule_type': 'containment',
                                       'contains': ['seeds']}}}}

        query = JsonBModel.objects.filter(data__jsonb=filt)
        self.assertEqual(query.count(), 2)

    def test_things(self):
        JsonBModel.objects.create(data={"Object Details": {"Main cause": "Mistake"}})

        filt = {'Object Details': {'Main cause': {'_rule_type': 'containment',
                                                    'contains': ['Mistake']}}}

        query = JsonBModel.objects.filter(data__jsonb=filt)
        self.assertEqual(query.count(), 1)

    def test_use_of_ANDs_in_containment_pattern_match(self):
        JsonBModel.objects.create(data={'a': {'b': {'beagels': "beegels"},
                                              'c': {'rhymes': 'seeds'}}})
        JsonBModel.objects.create(data={'a': {'b': {'beagels': "bgels"},
                                              'c': {'rhymes': 'steeds'}}})


        filt1 = {'a': {'b': {'beagels': {'_rule_type': 'containment',
                                         'pattern': 'bee'}},
                       'c': {'rhymes': {'_rule_type': 'containment',
                                        'pattern': 'bee'}}}}

        filt2 = {'a': {'b': {'beagels': {'_rule_type': 'containment',
                                         'pattern': 'eeg'}},
                       'c': {'rhymes': {'_rule_type': 'containment',
                                        'pattern': 'eed'}}}}

        # filt3 should be functionally equivalent to filt2;
        # each space-separated term appears in at least one searched field on the same record
        filt3 = {'a': {'b': {'beagels': {'_rule_type': 'containment',
                                         'pattern': 'eeg eed'}},
                       'c': {'rhymes': {'_rule_type': 'containment',
                                        'pattern': 'eeg eed'}}}}

        # filt4 should return nothing, because although each space-separated term has a match,
        # those matches occur on different records
        filt4 = {'a': {'b': {'beagels': {'_rule_type': 'containment',
                                         'pattern': 'bge seeds'}},
                       'c': {'rhymes': {'_rule_type': 'containment',
                                        'pattern': 'bge seeds'}}}}

        # same as filt4, but this will match because the term matches are on the same record
        filt5 = {'a': {'b': {'beagels': {'_rule_type': 'containment',
                                         'pattern': 'bge steeds'}},
                       'c': {'rhymes': {'_rule_type': 'containment',
                                        'pattern': 'bge steeds'}}}}

        # should match on same field
        filt6 = {'a': {'b': {'beagels': {'_rule_type': 'containment',
                                         'pattern': 'ste eeds'}},
                       'c': {'rhymes': {'_rule_type': 'containment',
                                        'pattern': 'ste eeds'}}}}


        query1 = JsonBModel.objects.filter(data__jsonb=filt1)
        query2 = JsonBModel.objects.filter(data__jsonb=filt2)
        query3 = JsonBModel.objects.filter(data__jsonb=filt3)
        query4 = JsonBModel.objects.filter(data__jsonb=filt4)
        query5 = JsonBModel.objects.filter(data__jsonb=filt5)
        query6 = JsonBModel.objects.filter(data__jsonb=filt6)
        self.assertEqual(query1.count(), 1)
        self.assertEqual(query2.count(), 1)
        self.assertEqual(query3.count(), 1)
        self.assertEqual(query4.count(), 0)
        self.assertEqual(query5.count(), 1)
        self.assertEqual(query6.count(), 1)

    def test_use_of_ANDs_in_multiple_containment_pattern_match(self):
        JsonBModel.objects.create(data={'a': {'b': [{'beagels': "beegels"},
                                                    {'beagels': "beagels"}],
                                              'c': [{'favoritefood': 'seeds'},
                                                    {'favoritefood': 'salt'}]}})
        JsonBModel.objects.create(data={'a': {'b': [{'beagels': "bgels"},
                                                    {'beagels': "bgels"}],
                                              'c': [{'favoritefood': 'waffles'},
                                                    {'favoritefood': 'bees'}]}})


        filt1 = {'a': {'b': {'beagels': {'_rule_type': 'containment_multiple',
                                        'pattern': 'bee'}},
                      'c': {'favoritefood': {'_rule_type': 'containment_multiple',
                                             'pattern': 'bee'}}}}

        filt2 = {'a': {'b': {'beagels': {'_rule_type': 'containment_multiple',
                                        'pattern': 'bge'}},
                      'c': {'favoritefood': {'_rule_type': 'containment_multiple',
                                             'pattern': 'waff'}}}}

        # should be functionally equivalent to filt2
        filt3 = {'a': {'b': {'beagels': {'_rule_type': 'containment_multiple',
                                        'pattern': 'bge waff'}},
                      'c': {'favoritefood': {'_rule_type': 'containment_multiple',
                                             'pattern': 'bge waff'}}}}

        # refinement of filt1
        filt4 = {'a': {'b': {'beagels': {'_rule_type': 'containment_multiple',
                                        'pattern': 'bee ffl'}},
                      'c': {'favoritefood': {'_rule_type': 'containment_multiple',
                                             'pattern': 'bee ffl'}}}}

        # returns nothing because term matches are on separate records
        filt5 = {'a': {'b': {'beagels': {'_rule_type': 'containment_multiple',
                                        'pattern': 'bge salt'}},
                      'c': {'favoritefood': {'_rule_type': 'containment_multiple',
                                             'pattern': 'bge salt'}}}}

        # like filt5, but returns a match because terms are found on same record
        filt6 = {'a': {'b': {'beagels': {'_rule_type': 'containment_multiple',
                                        'pattern': 'beeg salt'}},
                      'c': {'favoritefood': {'_rule_type': 'containment_multiple',
                                             'pattern': 'beeg salt'}}}}

        query1 = JsonBModel.objects.filter(data__jsonb=filt1)
        query2 = JsonBModel.objects.filter(data__jsonb=filt2)
        query3 = JsonBModel.objects.filter(data__jsonb=filt3)
        query4 = JsonBModel.objects.filter(data__jsonb=filt4)
        query5 = JsonBModel.objects.filter(data__jsonb=filt5)
        query6 = JsonBModel.objects.filter(data__jsonb=filt6)
        self.assertEqual(query1.count(), 2)
        self.assertEqual(query2.count(), 1)
        self.assertEqual(query3.count(), 1)
        self.assertEqual(query4.count(), 1)
        self.assertEqual(query5.count(), 0)
        self.assertEqual(query6.count(), 1)

    def test_regex_injection_on_similarity_filter(self):
        JsonBModel.objects.create(data={'a': {'b': [{'beagels': ".*"}, {'beagels': "beagels"}]}})
        JsonBModel.objects.create(data={'a': {'b': [{'beagels': """aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                                                                   aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                                                                   aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                                                                   aaaaaaaa""", "arg": "zonk"}]}})
        filt1 = {'a': {'b': {'beagels': {'_rule_type': 'containment_multiple',
                                         'pattern': '.*'}}}}
        bad_filter = {'a': {'b': {'(a+)+': {'_rule_type': 'containment_multiple',
                                            'pattern': '(a+)+'}}}}
        # ReDos here should cause tests to crash if injection works
        query0 = JsonBModel.objects.filter(data__jsonb=bad_filter)
        query1 = JsonBModel.objects.filter(data__jsonb=filt1)
        self.assertEqual(query0.count(), 0)
        self.assertEqual(query1.count(), 1)

    def test_intrange_filter_missing_numbers(self):
        """Test to ensure that missing min and max doesn't add filters"""
        self.assertEqual(FilterTree.intrange_filter(['a', 'b', 'c'],
                         {'_rule_type': 'intrange', 'min': None}),
                         None)
        self.assertEqual(FilterTree.intrange_filter(['a', 'b', 'c'],
                         {'_rule_type': 'intrange', 'min': 1}),
                         (u'((a->%s->>%s)::int >= %s)',
                          [u'b', u'c', 1]))
        self.assertEqual(FilterTree.intrange_filter(['a', 'b', 'c'],
                         {'_rule_type': 'intrange', 'max': 1}),
                         (u'((a->%s->>%s)::int <= %s)',
                          [u'b', u'c', 1]))
        self.assertEqual(FilterTree.intrange_filter(['a', 'b', 'c'],
                         {'_rule_type': 'intrange', 'max': 1, 'min': None}),
                         (u'((a->%s->>%s)::int <= %s)',
                          [u'b', u'c', 1]))

    def test_exclude_null_filters(self):
        """Test that filters which return None are excluded from the query string"""
        int_none_rule = {'_rule_type': 'intrange', 'min': None, 'max': None}
        other_rule = self.mock_contains_rule
        jsonb_query = {'should_be': other_rule, 'should_not_be': int_none_rule}
        ft = FilterTree(jsonb_query, 'data')
        sql_str, sql_params = ft.sql()
        self.assertFalse('AND' in sql_str, 'Found "AND" in query string')  # Should only be one

    def test_empty_filters(self):
        """Test that fully-empty filters work and return all instances"""
        JsonBModel.objects.create(data={'a': {'b': {'c': "zog", 'd': "zog"}}})
        JsonBModel.objects.create(data={'a': {'b': {'c': "zog", 'd': 9000}}})
        JsonBModel.objects.create(data={'a': {'b': [{'c': "zog"}, {'c': "dog"}]}})

        empty_intrange = {'a': {'b': {'c': {'_rule_type': 'intrange', 'min': None, 'max': None}}}}
        empty_containment = {'a': {'b': {'c': {'_rule_type': 'containment', 'contains': []}}}}
        empty_mult_containment = {'a': {'b': {'c': {'_rule_type': 'containment_multiple',
                                                    'contains': []}}}}
        self.assertEqual(JsonBModel.objects.filter(data__jsonb=empty_intrange).count(), 3)
        self.assertEqual(JsonBModel.objects.filter(data__jsonb=empty_containment).count(), 3)
        self.assertEqual(JsonBModel.objects.filter(data__jsonb=empty_mult_containment).count(), 3)

    def test_large_search(self):
        """Test using a large json object and multiple conditions"""
        JsonBModel.objects.create(data={"Person":[{"License number":"","Name":"Rodolfo","Driver error":"Bad turning","Age":"35","Vehicle":"abc-123","Involvment":"Driver","Sex":"Male","Address":"","Injury":"Not injured","Hospital":"","_localId":"936a572d-2504-44f8-88cc-fa3c4afe82d1"},{"License number":"","Name":"Manos","Age":"45","Vehicle":"abc-123","Involvment":"Driver","Seat belt/helmet":"Not worn","Sex":"Male","Address":"","Injury":"Fatal","Hospital":"Santa Elena","_localId":"2f7163f0-af2d-48b1-a8fb-9dc0ba60dfc0"}],"Object Details":{"Description":"","Surface condition":"Dry","Main cause":"Mistake","_localId":"abc-123","Traffic control":"None","Severity":"Fatal","Collision type":"Right angle","Surface type":"Concrete"},"Vehicle":[{"Maneuver":"Reversing","Vehicle type":"Truck (Artic)","Insurance details":"","Chassis number":"","Make":"Fuso","Defect":"None","Damage":"Right","_localId":"923123","Model":"","Plate number":"","Engine number":""},{"Maneuver":"Going ahead","Direction":"North","Vehicle type":"Motorcycle","Insurance details":"","Chassis number":"","Make":"Honda","Defect":"None","Damage":"Multiple","_localId":"10583eea-864d-408d-99ff-8e57f8d687a8","Model":"","Plate number":"","Engine number":""}]})
        JsonBModel.objects.create(data={"Person":[],"Object Details":{"Traffic control":"Centerline","Description":"V1 was running along Kabulawan, Lagonglong and accidentally hit a stockpile placed in the roadway of deep excavation done by SMART contractor having poor devices. As a result, the driver sustained minor injury and damages to said V1.","Num passenger casualties":"0","Surface condition":"Wet","Num driver casualties":"1","Main cause":"Road defect","Num pedestrian casualties":"0","_localId":"092b80d0-a8fa-44db-857c-d36d7159447f","Surface type":"Concrete","Severity":"Injury","Collision type":"Hit object in road","Num vehicles":"1"},"Vehicle":[]})
        JsonBModel.objects.create(data={"Person":[],"Object Details":{"Traffic control":"None","Description":"The motorolla was traversing the road heading north direction towards Aparri with passenger when a tricycle heading the same direction bumped the rear portion of the motorolla causing damages on both vehicles and injury on the motorcycle driver and passen","Num passenger casualties":"1","Surface condition":"Wet","Num driver casualties":"1","Main cause":"Mistake","Num pedestrian casualties":"0","_localId":"5e8e09fb-185b-4433-8952-94ee4f07422d","Surface type":"Concrete","Severity":"Injury","Collision type":"Rear end","Num vehicles":"2"},"Vehicle":[]})

        # With a simple containment check
        filt1 = {"Object Details":{"Main cause":{"_rule_type":"containment","contains":["Mistake"]}}}
        query1 = JsonBModel.objects.filter(data__jsonb=filt1)
        self.assertEqual(query1.count(), 2)

        # With a containment check and a pattern check
        filt2 = {"Object Details":{"Main cause":{"_rule_type":"containment","contains":["Mistake"]},"Severity":{"pattern":"inj","_rule_type":"containment"}}}
        query2 = JsonBModel.objects.filter(data__jsonb=filt2)
        self.assertEqual(query2.count(), 1)

        filt3 = {"Object Details":{"Severity":{"pattern":"fat","_rule_type":"containment"}}}
        query3 = JsonBModel.objects.filter(data__jsonb=filt3)
        self.assertEqual(query3.count(), 1)
