import unittest
from core.worldparser import StrictParser, XMLFormatError
#from core.worldparser.expat import ExpatError


class testStrictParser(unittest.TestCase):
    """Strict hierarchical parser"""

    def setUp(self):
        self.parser = StrictParser()

    def tearDown(self):
        del self.parser

    def test_NoneParser(self):
        """Outer layer"""

        self.parser._contexts = {
            'global': (None, ['global'])
            }

        self.assertIsNone(self.parser.parse_string("<global/>"))

    def test_TagSoup(self):
        """Basic XML rules"""
        self.parser._contexts = {
            'global': (None, ['a', 'b']),
            'a': (None, ['b']),
            'b': (None, ['a'])
            }

        self.assertRaises(XMLFormatError, self.parser.parse_string,
                          """<a>""")
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                          """</b>""")
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                          """<a><b></a>""")
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                          """<a><b></a></b>""")
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                          """<a/><b/>""")

        self.assertIsNone(self.parser.parse_string("<a/>"))
        self.assertIsNone(self.parser.parse_string("<a><b/></a>"))
        self.assertIsNone(self.parser.parse_string("<b><a/><a><b/></a></b>"))

    def test_attrs(self):
        """Attributes passing"""

        def result(**kwargs):
            return kwargs

        def tst_a(x, y, t, q, z):
            return x, y, t, q, z

        def tst_b(x, y='0'):
            return x, y

        def tst_c(x, e):
            return e

        def tst_d(x, e=None):
            if e is None:
                return x
            else:
                return e

        def tst_e(x=0):
            pass

        self.parser._contexts = {
            'global': (result, ['a', 'b', 'c', 'd']),
            'a': (tst_a, []),
            'b': (tst_b, []),
            'c': (tst_c, ['e']),
            'd': (tst_d, ['e']),
            'e': (tst_e, [])
            }

        # All are supplied
        self.assertEqual(('3', '4', '6', '7', '8'), self.parser.parse_string(
                         "<a x='3' y='4' t='6' q='7' z='8'/>")['a'][0])
        # Order doesn't matter
        self.assertEqual(('3', '4', '6', '7', '8'), self.parser.parse_string(
                         "<a q='7' x='3' z='8' y='4' t='6'/>")['a'][0])

        # Extra attrs
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                          """<a x='3' y='4' t='6' q='7' z='8' s='99'/>""")

        # Insufficient attrs
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                          """<a x='3' t='6'/>""")

        # Default values used
        self.assertEqual(('3', '4'),
                         self.parser.parse_string("<b x='3' y='4'/>")['b'][0])
        self.assertEqual(('3', '0'),
                         self.parser.parse_string("<b x='3'/>")['b'][0])

        # Collected subtags
        self.assertEqual([None, None], self.parser.parse_string(
                         "<c x='3'><e/><e/></c>")['c'][0])
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                          """<c x='3'/>""")

        # Collected subtags with default
        self.assertEqual([None, None], self.parser.parse_string(
                         "<d x='3'><e/><e/></d>")['d'][0])
        self.assertEqual('3', self.parser.parse_string("<d x='3'/>")['d'][0])

    def test_Suffix(self):
        """Attribute suffix"""
        def result(**kwargs):
            return kwargs

        def tst_a(b_list):
            return b_list

        self.parser._contexts = {
            'global': (result, ['a']),
            'a': (tst_a, ['b']),
            'b': (lambda: None, [])
            }

        self.parser._subtag_suffix = "_list"

        self.assertEqual([None, None], self.parser.parse_string(
                         "<a><b/><b/></a>")['a_list'][0])
