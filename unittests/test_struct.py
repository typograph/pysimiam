# -*- coding: utf-8 -*-
from core.struct import Struct, update_struct

import unittest


class testStruct(unittest.TestCase):
    """Construction and functionality of helpers.Struct"""
    def test_direct_access(self):
        """Struct fields can be accessed as object attributes"""
        p = Struct()
        p.x = 3.5
        self.assertEqual(p.x, 3.5)
        p.s = 'qwerty'
        self.assertEqual(p.s, 'qwerty')
        p.f = [1, 2, 3, 4, 5]
        self.assertEqual(p.f, [1, 2, 3, 4, 5])
        p.f = None
        self.assertIsNone(p.f)

    def test_dict_access(self):
        """Struct fields can be accessed as dict items"""
        p = Struct()
        p["x"] = 3
        self.assertEqual(p.x, 3)
        p.y = 4.5
        self.assertEqual(p["y"], 4.5)
        self.assertFalse("k" in p)
        self.assertFalse(3 in p)
        self.assertTrue("x" in p)

    def test_identifier_names(self):
        """Struct acceps valid Python identifiers as field names"""
        p = Struct()
        p.very_long_identifier = True
        self.assertTrue(p['very_long_identifier'])
        p.another1ofthoSe1230984 = False
        self.assertFalse(p['another1ofthoSe1230984'])
        p['ASD_qwe'] = True
        self.assertTrue(p.ASD_qwe)

        with self.assertRaises(ValueError):
            p["123asd"] = False
        with self.assertRaises(ValueError):
            p["aqs-asdS"] = False
        with self.assertRaises(ValueError):
            p["поле"] = False

    def test_equality(self):
        """Struct can be compared to another Struct"""
        self.assertEqual(Struct({'a': 3, 'b': 4}),
                         Struct({'a': 3, 'b': 4}))
        self.assertNotEqual(Struct({'a': 3, 'b': 4}),
                            Struct({'a': 3, 'c': 4}))
        self.assertNotEqual(Struct({'a': 3, 'b': 4}),
                            Struct({'a': 4, 'b': 4}))
        self.assertNotEqual(Struct({'a': 3, 'b': 4}),
                            Struct({'a': 3, 'b': 4, 'c': 5}))

        self.assertEqual(Struct({'a': {'b': 4, 'c': {'x': None}}}),
                         Struct('{"a": {"b": 4, "c": {"x": null}}}'))
        self.assertNotEqual(Struct({'a': {'b': 4, 'c': {'x': None}}}),
                            Struct('{"a": {"b": 5, "c": {"x": null}}}'))
        self.assertNotEqual(Struct({'a': {'b': 4, 'c': {'x': 3}}}),
                            Struct('{"a": {"b": 4, "c": {"x": null}}}'))
        self.assertNotEqual(Struct({'a': {'b': 4, 'c': {'y': None}}}),
                            Struct('{"a": {"b": 4, "c": {"x": null}}}'))
        self.assertNotEqual(Struct({'a': {'b': 4, 'c': {'x': None}, 'r': ''}}),
                            Struct('{"a": {"b": 4, "c": {"x": null}}}'))

    def test_dict_constructor(self):
        """Struct can be constructed from dict"""
        # Correct construction
        p = Struct({'a': 3, 'b': [1, 2, 3], 'c': {'q': 1}})
        self.assertEqual(p.a, 3)
        self.assertEqual(p.b, [1, 2, 3])
        # Note that the dict is converted to Struct
        self.assertEqual(p.c.q, 1)

        # Faulty construction
        with self.assertRaises(ValueError):
            p = Struct({'123': 3})
        with self.assertRaises(ValueError):
            p = Struct({1: 3})

    def test_json_import(self):
        """Struct can be reconstructed from a valid JSON"""
        # Simple one-level JSON
        p = Struct('{"x":3, "y":"nothing", "z":null}')
        self.assertEqual(p.x, 3)
        self.assertEqual(p.y, "nothing")
        self.assertIsNone(p.z)

        # Multi-level JSON
        p = Struct('{"x":3, "y":{"a":null, "z":{"q":4,"radius":5.5}}}')
        self.assertEqual(p.x, 3)
        self.assertIsNone(p.y.a)
        self.assertEqual(p.y.z.q, 4)
        self.assertEqual(p.y.z.radius, 5.5)

        # Incomplete JSON
        with self.assertRaises(ValueError):
            p = Struct('null')
        with self.assertRaises(ValueError):
            p = Struct('[5, 4, 5]')

        # Invalid JSON
        with self.assertRaises(ValueError):
            p = Struct('{"x":3 "y":null}')
        with self.assertRaises(ValueError):
            p = Struct('{"x":3, "y":{"q":null, radius:4}}')

        # Invalid field names in JSON
        with self.assertRaises(ValueError):
            p = Struct('{"x":3, "1y":4}')
        with self.assertRaises(ValueError):
            p = Struct('{"x-6":3, "y":4}')
        with self.assertRaises(ValueError):
            p = Struct('{"x-%-y":3}')

    def test_json_export(self):
        """Struct repr() is a valid JSON"""
        p = Struct('{"x":3, "y":{"a":[null,3,4], \
                    "z":{"q":"label","radius":5.5}}}')
        self.assertEqual(p, Struct(repr(p)))

    def test_nleaves(self):
        """Structure knows its number of end leaves"""
        p = Struct({'coords': {'x': 3, 'y': 4, 'z': 5},
                    'title': 'navigation',
                    'pid': {'slow': False,
                            'coeff': {'p': 1.3, 'i': 1.6, 'd': 5.5}}})
        self.assertEqual(len(p), 8)
        self.assertEqual(len(p.coords), 3)
        self.assertEqual(len(p.pid), 4)

        p.title = Struct({'main': 'Nabigation', 'sub': 'Way home'})
        self.assertEqual(len(p), 9)
        self.assertEqual(len(p.title), 2)
        self.assertEqual(len(p.coords), 3)
        self.assertEqual(len(p.pid), 4)

        p.pid.coeff.t = Struct('{"nice":0.3, "ugly":4.4}')
        self.assertEqual(len(p), 11)
        self.assertEqual(len(p.title), 2)
        self.assertEqual(len(p.coords), 3)
        self.assertEqual(len(p.pid), 6)

        p.pid = None
        self.assertEqual(len(p), 6)
        self.assertEqual(len(p.title), 2)
        self.assertEqual(len(p.coords), 3)

    def test_update(self):
        """Struct can partially update itself"""
        def subtest(updated, updater, expected, ui):
            updated_cache = Struct(repr(updated))
            a = updated << updater
            self.assertEqual(a, expected)
            self.assertEqual(updated, updated_cache)
            updated <<= updater
            self.assertEqual(updated, expected)
            self.assertEqual(update_struct(updated_cache, updater), ui)
            self.assertEqual(updated_cache, expected)

        p = Struct({'coords': {'x': 3, 'y': 4, 'z': 5},
                    'title': 'navigation',
                    'pid': {'slow': False,
                            'coeff': {'p': 1.3, 'i': 1.6, 'd': 5.5}}})

        # Empty Struct - all not updated
        subtest(p,
                Struct(),
                Struct({'coords': {'x': 3, 'y': 4, 'z': 5},
                        'title': 'navigation',
                        'pid': {'slow': False,
                                'coeff': {'p': 1.3,
                                          'i': 1.6,
                                          'd': 5.5}}}),
                (0, 0))

        # Alien Struct - all not updated, all ignored
        subtest(p,
                Struct({'x': 3, 'y': 4, 'z': 5}),
                Struct({'coords': {'x': 3, 'y': 4, 'z': 5},
                        'title': 'navigation',
                        'pid': {'slow': False,
                                'coeff': {'p': 1.3,
                                          'i': 1.6,
                                          'd': 5.5}}}),
                (0, 3))

        # Partial Struct
        subtest(p,
                Struct({'coords': {'x': 1,
                                   'y': 2,
                                   'z': 3}}),
                Struct({'coords': {'x': 1, 'y': 2, 'z': 3},
                        'title': 'navigation',
                        'pid': {'slow': False,
                                'coeff': {'p': 1.3,
                                          'i': 1.6,
                                          'd': 5.5}}}),
                (3, 0))

        # Partial Struct with same values - still updated
        subtest(p,
                Struct({'coords': {'x': 1,
                                   'y': 2,
                                   'z': 3}}),
                Struct({'coords': {'x': 1, 'y': 2, 'z': 3},
                        'title': 'navigation',
                        'pid': {'slow': False,
                                'coeff': {'p': 1.3,
                                          'i': 1.6,
                                          'd': 5.5}}}),
                (3, 0))

        # Partial Struct one level deeper
        subtest(p,
                Struct({'coords': {'x': 1,
                                   'y': 2,
                                   'z': 3},
                        'title': 'gauze',
                        'pid': {'k': 3}}),
                Struct({'coords': {'x': 1, 'y': 2, 'z': 3},
                        'title': 'gauze',
                        'pid': {'slow': False,
                                'coeff': {'p': 1.3,
                                          'i': 1.6,
                                          'd': 5.5}}}),
                (4, 1))

        # Partial Struct empty subsets
        subtest(p,
                Struct({'coords': {},
                        'title': 'gauze',
                        'pid': {'slow': False,
                                'coeff': {}}}),
                Struct({'coords': {'x': 1, 'y': 2, 'z': 3},
                        'title': 'gauze',
                        'pid': {'slow': False,
                                'coeff': {'p': 1.3,
                                          'i': 1.6,
                                          'd': 5.5}}}),
                (2, 0))

        # Partial Struct type coercion
        subtest(p,
                Struct({'coords': {'x': 3.3,
                                   'y': True,
                                   'z': 4},
                        'title': 'gauze',
                        'pid': {'slow': False,
                                'coeff': None}}),
                Struct({'coords': {'x': 1, 'y': 2, 'z': 4},
                        'title': 'gauze',
                        'pid': {'slow': False,
                                'coeff': {'p': 1.3,
                                          'i': 1.6,
                                          'd': 5.5}}}),
                (3, 0))

        # int->float type coercion
        subtest(p,
                Struct({'coords': {'x': 3.0,
                                   'y': 4.0,
                                   'z': 5.0},
                        'pid': {'coeff': {'p': 1,
                                          'i': 2,
                                          'd': False}}}),
                Struct({'coords': {'x': 1, 'y': 2, 'z': 4},
                        'title': 'gauze',
                        'pid': {'slow': False,
                                'coeff': {'p': 1.0,
                                          'i': 2.0,
                                          'd': 5.5}}}),
                (2, 0))
