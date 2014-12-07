from core import ui
from core.helpers import Struct

import unittest


class testParamDescr(unittest.TestCase):
    """ui.ParamDescr can be constructed"""

    def test_simple_construction_int(self):
        """ui.Int can be constructed with name & value"""
        pint = ui.Int('Thing', 3)
        self.assertEqual(pint.name, 'thing')
        self.assertEqual(pint.value, 3)
        self.assertEqual(pint.min_value, -100)
        self.assertEqual(pint.max_value, 100)
        self.assertEqual(pint.label, 'Thing')

    def test_full_construction_int(self):
        """ui.Int can be constructed with full set of parameters"""
        pint = ui.Int('thing', 3, 0, 3, 'One more')
        self.assertEqual(pint.name, 'thing')
        self.assertEqual(pint.value, 3)
        self.assertEqual(pint.min_value, 0)
        self.assertEqual(pint.max_value, 3)
        self.assertEqual(pint.label, 'One more')

    def test_faulty_construction_int(self):
        """ui.Int can only be constructed with an int value"""
        self.assertRaises(ValueError,
                          lambda: ui.Int('combo', "five"))
        self.assertRaises(ValueError,
                          lambda: ui.Int('combo', 1.3))
        self.assertRaises(ValueError,
                          lambda: ui.Int('combo', True))

    def test_equality_int(self):
        """ui.Int can be tested for equality"""
        pint = ui.Int('int', 3)
        self.assertNotEqual(pint, 3)
        self.assertEqual(pint, ui.Int('int', 3))
        self.assertNotEqual(pint, ui.Int('int', 4))
        self.assertNotEqual(pint, ui.Int('int2', 3))
        self.assertEqual(pint, ui.Int('int', 3, label='Int'))
        self.assertNotEqual(pint, ui.Int('int', 3, label='Integer'))
        self.assertEqual(pint, ui.Int('int', 3, -100, 100, 'Int'))
        self.assertNotEqual(pint, ui.Int('int', 3, -101, 100, 'Int'))
        self.assertNotEqual(pint, ui.Int('int', 3, -100, 101, 'Int'))

    def test_simple_construction_float(self):
        """ui.Float can be constructed with name & value"""
        pflt = ui.Float('paRAmeter', 3.5)
        self.assertEqual(pflt.name, 'parameter')
        self.assertEqual(pflt.value, 3.5)
        self.assertEqual(pflt.step, 1.0)
        self.assertEqual(pflt.min_value, -1000.0)
        self.assertEqual(pflt.max_value, 1000.0)
        self.assertEqual(pflt.label, 'Parameter')

    def test_full_construction_float(self):
        """ui.Float can be constructed with full set of parameters"""
        pflt = ui.Float('float', 3.5, 0.1, 0, 3, 'Labbell')
        self.assertEqual(pflt.name, 'float')
        self.assertEqual(pflt.value, 3.5)
        self.assertEqual(pflt.step, 0.1)
        self.assertEqual(pflt.min_value, 0)
        self.assertEqual(pflt.max_value, 3)
        self.assertEqual(pflt.label, 'Labbell')

    def test_faulty_construction_float(self):
        """ui.Float can only be constructed with an int or a float value"""
        pflt = ui.Float('combo', 5)
        self.assertIsInstance(pflt.value, float)
        self.assertEqual(pflt.value, 5.0)
        self.assertRaises(ValueError,
                          lambda: ui.Float('combo', "five"))
        self.assertRaises(ValueError,
                          lambda: ui.Float('combo', []))
        self.assertRaises(ValueError,
                          lambda: ui.Float('combo', True))

    def test_equality_float(self):
        """ui.Float can be tested for equality"""
        pflt = ui.Float('float', 3.0)
        self.assertNotEqual(pflt, 3.0)
        self.assertEqual(pflt, ui.Float('float', 3.0))
        self.assertEqual(pflt, ui.Float('float', 3))
        self.assertNotEqual(pflt, ui.Float('float', 4.5))
        self.assertNotEqual(pflt, ui.Float('float2', 3.0))
        self.assertEqual(pflt, ui.Float('float', 3, label='Float'))
        self.assertNotEqual(pflt, ui.Float('float', 3, label='Floating'))
        self.assertEqual(pflt,
                         ui.Float('float', 3, 1.0, -1000, 1000, 'Float'))
        self.assertNotEqual(pflt,
                            ui.Float('float', 3, 0.1, -1000, 1000, 'Float'))
        self.assertNotEqual(pflt,
                            ui.Float('float', 3, 1.0, -100, 1000, 'Float'))
        self.assertNotEqual(pflt,
                            ui.Float('float', 3, 1.0, -1000, 100, 'Float'))

    def test_construction_bool(self):
        """ui.Bool can be constructed with & without label"""
        pboo = ui.Bool('truth', False, '2beOR!2be')
        self.assertEqual(pboo.name, 'truth')
        self.assertEqual(pboo.value, False)
        self.assertEqual(pboo.label, '2beOR!2be')
        pboo = ui.Bool('Bool', True)
        self.assertEqual(pboo.name, 'bool')
        self.assertEqual(pboo.value, True)
        self.assertEqual(pboo.label, 'Bool')

    def test_faulty_construction_bool(self):
        """ui.Bool cannot be constructed with non-boolean value"""
        self.assertRaises(ValueError,
                          lambda: ui.Bool('combo', []))
        self.assertRaises(ValueError,
                          lambda: ui.Bool('combo', 1))
        self.assertRaises(ValueError,
                          lambda: ui.Bool('combo', 'true'))

    def test_equality_bool(self):
        """ui.Bool can be tested for equality"""
        pboo = ui.Bool('bool', True)
        self.assertNotEqual(pboo, True)
        self.assertEqual(pboo, ui.Bool('bool', True))
        self.assertEqual(pboo, ui.Bool('bool', True, 'Bool'))
        self.assertNotEqual(pboo, ui.Bool('bool', False))
        self.assertNotEqual(pboo, ui.Bool('float', True))
        self.assertNotEqual(pboo, ui.Bool('bool', True, label='Boolean'))

    def test_full_construction_select(self):
        """ui.Select can be constructed with & without label"""
        psel = ui.Select('combo', 'One', ['One', 'Two'], 'Select one')
        self.assertEqual(psel.name, 'combo')
        self.assertEqual(psel.value, 'One')
        self.assertEqual(psel.value_list, ['One', 'Two'])
        self.assertEqual(psel.label, 'Select one')
        psel = ui.Select('coMBo', 'One', ['One', 'Two'])
        self.assertEqual(psel.name, 'combo')
        self.assertEqual(psel.value, 'One')
        self.assertEqual(psel.value_list, ['One', 'Two'])
        self.assertEqual(psel.label, 'Combo')

    def test_faulty1_construction_select(self):
        """ui.Select cannot be constructed with value not in list"""
        self.assertRaises(ValueError,
                          lambda: ui.Select('combo', 'Three', ['One', 'Two']))

    def test_faulty2_construction_select(self):
        """ui.Select cannot be constructed with non-string values"""
        self.assertRaises(ValueError,
                          lambda: ui.Select('combo', 3, [1, 2, 3]))
        self.assertRaises(ValueError,
                          lambda: ui.Select('combo', 3, ['1', '2', 3]))
        self.assertRaises(ValueError,
                          lambda: ui.Select('combo', True, [True, False]))
        self.assertRaises(ValueError,
                          lambda: ui.Select('combo', [], [[], ()]))

    def test_equality_select(self):
        """ui.Select can be tested for equality"""
        psel = ui.Select('combo', 'One', ['One', 'Two'], 'Select one')
        self.assertNotEqual(psel, [])
        self.assertEqual(psel, ui.Select('combo',
                                         'One', ['One', 'Two'],
                                         'Select one'))
        self.assertNotEqual(psel, ui.Select('combo2',
                                            'One', ['One', 'Two'],
                                            'Select one'))
        self.assertNotEqual(psel, ui.Select('combo',
                                            'One', ['One', 'Two']))
        self.assertNotEqual(psel, ui.Select('combo',
                                            'One', ['One', 'Three'],
                                            'Select one'))
        self.assertNotEqual(psel, ui.Select('combo',
                                            'One', ['One', 'Two', 'Three'],
                                            'Select one'))
        self.assertNotEqual(psel, ui.Select('combo',
                                            'Two', ['One', 'Two'],
                                            'Select one'))
        self.assertNotEqual(psel, ui.Select('combo',
                                            'One', ['Two', 'One'],
                                            'Select one'))

    def test_param_construction_group(self):
        """ui.Group can be constructed with a list of ui.Parameter"""
        pgrp = ui.Group('testGroup', [ui.Int('testInt', 1),
                                      ui.Float('testFloat', 2.0),
                                      ui.Bool('testBool', False),
                                      ui.Select('testSelect', '1', ['1', '2']),
                                      ui.Int('testInt2', 3, label="One more")],
                        'A test group')
        self.assertEqual(pgrp.name, 'testgroup')
        self.assertEqual(pgrp.label, 'A test group')
        self.assertEqual(len(pgrp.contents), 5)
        self.assertEqual(pgrp.contents[0], ui.Int('testInt', 1))
        self.assertEqual(pgrp.contents[1], ui.Float('testFloat', 2.0))
        self.assertEqual(pgrp.contents[2], ui.Bool('testBool', False))
        self.assertEqual(pgrp.contents[3],
                         ui.Select('testSelect', '1', ['1', '2']))
        self.assertEqual(pgrp.contents[4],
                         ui.Int('testInt2', 3, label="One more"))

    def test_quick_construction_group(self):
        """ui.Group can be constructed with a list of tuples"""
        pgrp = ui.Group('testGroup', [('testBoolTpl', True),
                                      ui.Int('testInt', 1),
                                      ('testIntTpl', 2),
                                      ('testFloatTpl', 'labeled', 4.5),
                                      ('testSelectTpl', ('1', ['1', '2'])),
                                      ('testGroupTpl', [('i', 1)])])
        self.assertEqual(pgrp.name, 'testgroup')
        self.assertEqual(pgrp.label, 'Testgroup')
        self.assertEqual(len(pgrp.contents), 6)
        self.assertEqual(pgrp.contents[0], ui.Bool('testBoolTpl', True))
        self.assertEqual(pgrp.contents[1], ui.Int('testInt', 1))
        self.assertEqual(pgrp.contents[2], ui.Int('testIntTpl', 2))
        self.assertEqual(pgrp.contents[3],
                         ui.Float('testFloatTpl', 4.5, label='labeled'))
        self.assertEqual(pgrp.contents[4],
                         ui.Select('testSelectTpl', '1', ['1', '2']))
        self.assertEqual(pgrp.contents[5],
                         ui.Group('testGroupTpl', [ui.Int('i', 1)]))

    def test_tree_construction_group(self):
        """ui.Group can be constructed with groups inside"""
        pgrp = ui.Group('testGroup',
                        [ui.Group('first', [ui.Int('testInt', 1),
                                            ui.Float('testFloat', 2.0)]),
                         ui.Bool('testBool', False),
                         ui.Group('second', (
                             ui.Group('thrd', ()),
                             ('flt', 3.5))),
                         ('xyz', 4)])
        self.assertEqual(pgrp.name, 'testgroup')
        self.assertEqual(len(pgrp.contents), 4)
        self.assertEqual(len(pgrp.contents[0].contents), 2)
        self.assertEqual(pgrp.contents[0].contents[0],
                         ui.Int('testInt', 1))
        self.assertEqual(pgrp.contents[0].contents[1],
                         ui.Float('testFloat', 2.0))
        self.assertEqual(pgrp.contents[1], ui.Bool('testBool', False))
        self.assertEqual(len(pgrp.contents[2].contents), 2)
        self.assertEqual(len(pgrp.contents[2].contents[0].contents), 0)
        self.assertEqual(pgrp.contents[2].contents[0],
                         ui.Group('thrd', ()))
        self.assertEqual(pgrp.contents[2].contents[1],
                         ui.Float('flt', 3.5))
        self.assertEqual(pgrp.contents[3],
                         ui.Int('xyz', 4))

    def test_same_elements_group(self):
        """ui.Group does not allow elements with the same name
           on the same level
        """
        with self.assertRaises(ValueError):
            ui.Group('grp', [('i', 3), ('i', 3.4)])
        with self.assertRaises(ValueError):
            ui.Group('grp', [ui.Bool('i', False), ui.Group('i', [])])
        ui.Group('grp', [('i', 3), ui.Group('g2', [('i', 4)])])

    def test_equality_group(self):
        """ui.Group can be tested for equality"""
        grp1 = ui.Group('testGroup',
                        [ui.Group('first', [ui.Int('testInt', 1),
                                            ui.Float('testFloat', 2.0)]),
                         ui.Bool('testBool', False),
                         ui.Group('second', (
                             ui.Group('thrd', ()),
                             ('flt', 3.5))),
                         ('xyz', 4)])
        grp2 = ui.Group('testGroup',
                        [('first', [('testInt', 1), ('testFloat', 2.0)]),
                         ('testBool', False),
                         ('second', [('thrd', []), ui.Float('flt', 3.5)]),
                         ui.Int('xyz', 4)])
        self.assertEqual(grp1, grp2)

        grp1 = ui.Group('testGroup', [ui.Int('int', 6), ui.Float('f', 5.5)])
        self.assertNotEqual(grp1, [])
        self.assertEqual(grp1,
                         ui.Group('testGroup', [ui.Int('int', 6),
                                                ui.Float('f', 5.5)]))
        self.assertEqual(grp1,
                         ui.Group('testGroup', [ui.Int('int', 6),
                                                ui.Float('f', 5.5)],
                                  label="Testgroup"))
        self.assertNotEqual(grp1,
                            ui.Group('testGroup2', [ui.Int('int', 6),
                                                    ui.Float('f', 5.5)],
                                     label="Testgroup"))
        self.assertNotEqual(grp1,
                            ui.Group('testGroup', [ui.Int('int', 7),
                                                   ui.Float('f', 5.5)]))
        self.assertNotEqual(grp1,
                            ui.Group('testGroup', [ui.Int('int', 6),
                                                   ui.Float('f', 6.5)]))
        self.assertNotEqual(grp1,
                            ui.Group('testGroup', [ui.Float('f', 5.5),
                                                   ui.Int('int', 6)],
                                     label="Testgroup"))

    def test_struct_export(self):
        """ui.ParamDescr exports to Struct"""
        pgrp = ui.ParamDescr(ui.Group('first', [ui.Int('testint', 1),
                                                ui.Float('testfloat', 2.0)]),
                             ui.Bool('testbool', False),
                             ui.Group('second', (
                                 ui.Group('thrd', ()),
                                 ('flt', 3.5),
                                 ('slct', ('3', ['1', '2', '3'])))),
                             ('xyz', 4))
        sgrp = Struct({'first': {'testint': 1, 'testfloat': 2.0},
                       'testbool': False,
                       'second': {'thrd': {}, 'flt': 3.5, 'slct': '3'},
                       'xyz': 4})
        self.assertEqual(pgrp.asStruct(), sgrp)

    def test_struct_import(self):
        """ui.ParamDescr imports values from Struct"""
        pgrp = ui.ParamDescr(ui.Group('first', [ui.Int('testint', 1),
                                                ui.Float('testfloat', 2.0)]),
                             ui.Bool('testbool', False),
                             ui.Group('second', (
                                 ui.Group('thrd', ()),
                                 ui.Float('flt', 3.5),
                                 ui.Select('slct', '3', ['1', '2', '3']))),
                             ui.Int('xyz', 4))
        sgrp = Struct({'first': {'testint': 1, 'testfloat': 3.0},
                       'testbool': True,
                       'second': {'thrd': {}, 'flt': 1.5, 'slct': '2'},
                       'xyz': 4})
        agrp = ui.ParamDescr(ui.Group('first', [ui.Int('testint', 1),
                                                ui.Float('testfloat', 3.0)]),
                             ui.Bool('testbool', True),
                             ui.Group('second', (
                                 ui.Group('thrd', ()),
                                 ui.Float('flt', 1.5),
                                 ui.Select('slct', '2', ['1', '2', '3']))),
                             ui.Int('xyz', 4))
        pgrp.loadStruct(sgrp)
        self.assertEqual(pgrp, agrp, msg="Exact structure failed")

        sgrp = Struct({'testbool': True,
                       'second': {'flt': 1.5, 'slct': '1'},
                       'xyz': 66})
        agrp = ui.ParamDescr(ui.Group('first', [ui.Int('testint', 1),
                                                ui.Float('testfloat', 3.0)]),
                             ui.Bool('testbool', True),
                             ui.Group('second', (
                                 ui.Group('thrd', ()),
                                 ui.Float('flt', 1.5),
                                 ui.Select('slct', '1', ['1', '2', '3']))),
                             ui.Int('xyz', 66))
        pgrp.loadStruct(sgrp)
        self.assertEqual(pgrp, agrp, msg="Substructure failed")

        sgrp = Struct({'testbool': True,
                       'second': {'thrd': {}, 'flt': 2.5, 'slct': '1', 'x': 2},
                       'xyz': 77,
                       'ztr': '45'})
        agrp = ui.ParamDescr(ui.Group('first', [ui.Int('testint', 1),
                                                ui.Float('testfloat', 3.0)]),
                             ui.Bool('testbool', True),
                             ui.Group('second', (
                                 ui.Group('thrd', ()),
                                 ui.Float('flt', 2.5),
                                 ui.Select('slct', '1', ['1', '2', '3']))),
                             ui.Int('xyz', 77))
        pgrp.loadStruct(sgrp)
        self.assertEqual(pgrp, agrp, msg="Superstructure failed")

        sgrp = Struct({'first': {'testint': 1, 'testfloat': 3.0},
                       'testbool': True,
                       'second': {'thrd': {}, 'flt': 1.5, 'slct': '4'},
                       'xyz': 4})
                       
        with self.assertRaises(ValueError,
                               msg="Out-of-range values accepted in Select"):
            pgrp.loadStruct(sgrp, lazy=False)

    def test_xml_export(self):
        """ui.ParamDescr exports correct XML"""
        try:
            from StringIO import StringIO
        except ImportError:
            from io import StringIO

        pgrp = ui.ParamDescr(ui.Group('first', [ui.Int('testint', 1),
                                                ui.Float('testfloat', 2.0)]),
                             ui.Bool('testbool', False),
                             ui.Group('second', (
                                 ui.Group('thrd', ()),
                                 ui.Float('flt', 3.5),
                                 ui.Select('slct', '3', ['1', '2', '3']))),
                             ui.Int('xyz', 4))
        buffer = StringIO()
        pgrp.saveToXML(buffer)
        self.assertMultiLineEqual(buffer.getvalue(), """\
<?xml version="1.0"?>
<parameters testbool="false" xyz="4">
    <first testint="1" testfloat="2.0"/>
    <second flt="3.5" slct="3">
        <thrd/>
    </second>
</parameters>
""")

    def test_xml_import(self):
        """ui.ParamDescr accepts correct XML"""
        from io import BytesIO
        pgrp = ui.ParamDescr(ui.Group('first', [ui.Int('testint', 3),
                                                ui.Float('testfloat', 6.0)]),
                             ui.Bool('testbool', True),
                             ui.Group('second', (
                                 ui.Group('thrd', ()),
                                 ui.Float('flt', 3.55),
                                 ui.Select('slct', 'two',
                                           ['one', 'two', 'three']))),
                             ui.Int('xyz', 43))
        pgrp.loadFromXML(BytesIO(b"""<?xml version="1.0"?>
                                     <parameters testbool="false" xyz="4">
                                         <first testint="1" testfloat="2.0"/>
                                         <second flt="3.5" slct="three">
                                             <thrd/>
                                         </second>
                                     </parameters>
                                     """), lazy=False)
        self.assertEqual(pgrp,
                         ui.ParamDescr(
                             ui.Group('first', [ui.Int('testint', 1),
                                                ui.Float('testfloat', 2.0)]),
                             ui.Bool('testbool', False),
                             ui.Group('second', (
                                 ui.Group('thrd', ()),
                                 ui.Float('flt', 3.5),
                                 ui.Select('slct', 'three',
                                           ['one', 'two', 'three']))),
                             ui.Int('xyz', 4)))
        with self.assertRaises(ui.ParameterXMLFormatError,
                               msg="Tag 'questionable' accepted at 1st level"):
            pgrp.loadFromXML(
                BytesIO(b"""<?xml version="1.0"?>
                            <questionable testbool="false" xyz="4">
                                <first testint="1" testfloat="2.0"/>
                                <second flt="3.5" slct="three">
                                    <thrd/>
                                </second>
                            </questionable>
                            """), lazy=False)
        with self.assertRaises(ui.ParameterXMLFormatError,
                               msg="Extra attributes accepted"):
            pgrp.loadFromXML(
                BytesIO(b"""<?xml version="1.0"?>
                            <parameters testbool="false" xyz="4">
                                <first testint="1" testfloat="2.0"/>
                                <second flt="3.5" slct="three">
                                    <thrd x="3"/>
                                </second>
                            </parameters>
                            """), lazy=False)
        with self.assertRaises(ui.ParameterXMLFormatError,
                               msg="Missing tags accepted"):
            pgrp.loadFromXML(
                BytesIO(b"""<?xml version="1.0"?>
                            <parameters testbool="false" xyz="4">
                                <first testint="1" testfloat="2.0"/>
                                <second flt="3.5" slct="three">
                                </second>
                            </parameters>
                            """), lazy=False)
        with self.assertRaises(ui.ParameterXMLFormatError,
                               msg="Extra tags accepted"):
            pgrp.loadFromXML(
                BytesIO(b"""<?xml version="1.0"?>
                            <parameters testbool="false" xyz="4">
                                <first testint="1" testfloat="2.0"/>
                                <second flt="3.5" slct="three">
                                    <thrd/>
                                </second>
                                <long/>
                            </parameters>
                            """), lazy=False)
        with self.assertRaises(ui.ParameterXMLFormatError,
                               msg="Duplicate tags accepted"):
            pgrp.loadFromXML(
                BytesIO(b"""<?xml version="1.0"?>
                            <parameters testbool="false" xyz="4">
                                <first testint="1" testfloat="2.0"/>
                                <first testint="1" testfloat="2.0"/>
                                <second flt="3.5" slct="three">
                                    <thrd/>
                                </second>
                            </parameters>
                            """), lazy=False)
        with self.assertRaises(ui.ParameterXMLFormatError,
                               msg="Out-of-range values accepted in Select"):
            pgrp.loadFromXML(
                BytesIO(b"""<?xml version="1.0"?>
                            <parameters testbool="false" xyz="4">
                                <first testint="1" testfloat="2.0"/>
                                <second flt="3.5" slct="x">
                                    <thrd/>
                                </second>
                            </parameters>
                            """), lazy=False)
        with self.assertRaises(ui.ParameterXMLFormatError,
                               msg="Out-of-range values accepted in Bool"):
            pgrp.loadFromXML(
                BytesIO(b"""<?xml version="1.0"?>
                            <parameters testbool="33" xyz="4">
                                <first testint="1" testfloat="2.0"/>
                                <second flt="3.5" slct="one">
                                    <thrd/>
                                </second>
                            </parameters>
                            """), lazy=False)

    @unittest.expectedFailure
    def test_xml_import2(self):
        """ui.ParamDescr accepts correct XML"""
        from io import BytesIO
        pgrp = ui.ParamDescr(ui.Group('first', [ui.Int('testint', 3),
                                                ui.Float('testfloat', 6.0)]),
                             ui.Bool('testbool', True),
                             ui.Group('second', (
                                 ui.Group('thrd', ()),
                                 ui.Float('flt', 3.55),
                                 ui.Select('slct', '2', ['1', '2', '3']))),
                             ui.Int('xyz', 43))
        pgrp.loadFromXML(BytesIO(b"""<?xml version="1.0"?>
                                     <parameters testbool="false" xyz="4">
                                         <first testint="1" testfloat="2.0"/>
                                         <second flt="3.5" slct="3">
                                             <thrd/>
                                         </second>
                                     </parameters>
                                     """), lazy=False)
        self.assertEqual(pgrp,
                         ui.ParamDescr(
                             ui.Group('first', [ui.Int('testint', 1),
                                                ui.Float('testfloat', 2.0)]),
                             ui.Bool('testbool', False),
                             ui.Group('second', (
                                 ui.Group('thrd', ()),
                                 ui.Float('flt', 3.5),
                                 ui.Select('slct', '3', ['1', '2', '3']))),
                             ui.Int('xyz', 4)))
        with self.assertRaises(ui.ParameterXMLFormatError,
                               msg="Tag 'questionable' accepted at 1st level"):
            pgrp.loadFromXML(
                BytesIO(b"""<?xml version="1.0"?>
                            <questionable testbool="false" xyz="4">
                                <first testint="1" testfloat="2.0"/>
                                <second flt="3.5" slct="3">
                                    <thrd/>
                                </second>
                            </questionable>
                            """))
        with self.assertRaises(ui.ParameterXMLFormatError,
                               msg="Extra attributes accepted"):
            pgrp.loadFromXML(
                BytesIO(b"""<?xml version="1.0"?>
                            <parameters testbool="false" xyz="4">
                                <first testint="1" testfloat="2.0"/>
                                <second flt="3.5" slct="3">
                                    <thrd x="3"/>
                                </second>
                            </parameters>
                            """))
        with self.assertRaises(ui.ParameterXMLFormatError,
                               msg="Missing tags accepted"):
            pgrp.loadFromXML(
                BytesIO(b"""<?xml version="1.0"?>
                            <parameters testbool="false" xyz="4">
                                <first testint="1" testfloat="2.0"/>
                                <second flt="3.5" slct="3">
                                </second>
                            </parameters>
                            """), lazy=False)
        with self.assertRaises(ui.ParameterXMLFormatError,
                               msg="Extra tags accepted"):
            pgrp.loadFromXML(
                BytesIO(b"""<?xml version="1.0"?>
                            <parameters testbool="false" xyz="4">
                                <first testint="1" testfloat="2.0"/>
                                <second flt="3.5" slct="3">
                                    <thrd/>
                                </second>
                                <long/>
                            </parameters>
                            """), lazy=False)
        with self.assertRaises(ui.ParameterXMLFormatError,
                               msg="Duplicate tags accepted"):
            pgrp.loadFromXML(
                BytesIO(b"""<?xml version="1.0"?>
                            <parameters testbool="false" xyz="4">
                                <first testint="1" testfloat="2.0"/>
                                <first testint="1" testfloat="2.0"/>
                                <second flt="3.5" slct="3">
                                    <thrd/>
                                </second>
                            </parameters>
                            """), lazy=False)
        with self.assertRaises(ui.ParameterXMLFormatError,
                               msg="Out-of-range values accepted in Select"):
            pgrp.loadFromXML(
                BytesIO(b"""<?xml version="1.0"?>
                            <parameters testbool="false" xyz="4">
                                <first testint="1" testfloat="2.0"/>
                                <second flt="3.5" slct="x">
                                    <thrd/>
                                </second>
                            </parameters>
                            """), lazy=False)
        with self.assertRaises(ui.ParameterXMLFormatError,
                               msg="Out-of-range values accepted in Bool"):
            pgrp.loadFromXML(
                BytesIO(b"""<?xml version="1.0"?>
                            <parameters testbool="33" xyz="4">
                                <first testint="1" testfloat="2.0"/>
                                <second flt="3.5" slct="2">
                                    <thrd/>
                                </second>
                            </parameters>
                            """), lazy=False)
