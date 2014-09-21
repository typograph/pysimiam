from core.pose import Pose
from core.helpers import Struct

import unittest
from core.worldparser import WorldParser, XMLFormatError

class testWorldParser(unittest.TestCase):
    
    def setUp(self):
        self.parser = WorldParser()
        
    def tearDown(self):
        del self.parser
        
    def test_empty(self):
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                     """""")
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                     """<simulation/>""")
                
    def test_good_robot(self):
        # Simple
        self.assertEqual(
            self.parser.parse_string("""
            <simulation>
                <robot type="A">
                    <pose x="1" y="2" theta="3"/>
                    <supervisor type="B"/>
                </robot>
            </simulation>"""),
            [Struct({'type':'robot',
                     'robot':{'type':'A',
                              'pose':Pose(1,2,3),
                              'color':None,
                              'options':None},
                     'supervisor':{'type':'B','options':None}})])
        # With color
        self.assertEqual(
            self.parser.parse_string("""
            <simulation>
                <robot type="A" color="#FFFFFF">
                    <pose x="1" y="2" theta="3"/>
                    <supervisor type="B"/>
                </robot>
            </simulation>"""),
            [Struct({'type':'robot',
                     'robot':{'type':'A',
                              'pose':Pose(1,2,3),
                              'color':0xFFFFFF,
                              'options':None},
                     'supervisor':{'type':'B','options':None}})])    
        # With options
        self.assertEqual(
            self.parser.parse_string("""
            <simulation>
                <robot type="A" options='{"t":3,"w":{"x":"nobody"} }'>
                    <pose x="1" y="2" theta="3"/>
                    <supervisor type="B"/>
                </robot>
            </simulation>"""),
            [Struct({'type':'robot',
                     'robot':{'type':'A',
                              'pose':Pose(1,2,3),
                              'color':None,
                              'options':{'t':3,'w':{'x':'nobody'}}},
                     'supervisor':{'type':'B','options':None}})]) 
                     
        # With supervisor options
        self.assertEqual(
            self.parser.parse_string("""
            <simulation>
                <robot type="A" color="#FFFFFF">
                    <pose x="1" y="2" theta="3"/>
                    <supervisor type="B" options='{"t":3,"w":{"x":"nobody"} }'/>
                </robot>
            </simulation>"""),
            [Struct({'type':'robot',
                     'robot':{'type':'A',
                              'pose':Pose(1,2,3),
                              'color':0xFFFFFF,
                              'options':None},
                     'supervisor':{'type':'B','options':{'t':3,'w':{'x':'nobody'}}}})])    
                     
                     
    def test_bad_robot(self):
        # No type
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                     """<simulation>
                            <robot color="#000000">
                                <pose x=3 y=4 theta=5>
                            </robot>
                        </simulation>""")
        # Extra tags
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                     """<simulation>
                            <robot type="C" arm="None">
                                <pose x=3 y=4 theta=5>
                            </robot>
                        </simulation>""")
        
        # No supervisor
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                     """<simulation>
                            <robot type="A">
                                <pose x=3 y=4 theta=5>
                            </robot>
                        </simulation>""")
        # No supervisor type
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                     """<simulation>
                            <robot type="A">
                                <pose x=3 y=4 theta=5>
                                <supervisor options="{}"/>
                            </robot>
                        </simulation>""")
        # Extra supervisor tags
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                     """<simulation>
                            <robot type="A">
                                <pose x=3 y=4 theta=5>
                                <supervisor type="B" options="{}" hat="small"/>
                            </robot>
                        </simulation>""")
        
        # No Pose
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                     """<simulation>
                            <robot type="A">
                                <supervisor type="B">
                            </robot>
                        </simulation>""")
        # Incomplete Pose
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                     """<simulation>
                            <robot type="A">
                                <pose x="4" theta="0.004"/>
                                <supervisor type="B">
                            </robot>
                        </simulation>""")
        # Extra Pose tags
        self.assertRaises(XMLFormatError, self.parser.parse_string,
                     """<simulation>
                            <robot type="A">
                                <pose x="4" y="6" theta="0.004" phi="33"/>
                                <supervisor type="B">
                            </robot>
                        </simulation>""")
        
    def test_good_polygon(self):
        
        def test_polygon(tag):
            # Simple
            self.assertEqual(
                self.parser.parse_string("""
                <simulation>
                    <robot type="A">
                        <pose x="1" y="2" theta="3"/>
                        <supervisor type="B"/>
                    </robot>
                    <{0}>
                        <pose x="2" y="3" theta="4"/>
                        <geometry>
                            <point x="1" y="2"/>
                            <point x="1" y="3"/>
                            <point x="2" y="2"/>
                        </geometry>
                    </{0}>
                </simulation>""".format(tag)),
                [Struct({'type':'robot',
                        'robot':{'type':'A',
                                'pose':Pose(1,2,3),
                                'color':None,
                                'options':None},
                        'supervisor':{'type':'B','options':None}}),
                Struct({'type':tag,
                        'pose':Pose(2,3,4),
                        'color':None,
                        'points':[(1,2),(1,3),(2,2)]})])
            # With color
            self.assertEqual(
                self.parser.parse_string("""
                <simulation>
                    <robot type="A">
                        <pose x="1" y="2" theta="3"/>
                        <supervisor type="B"/>
                    </robot>
                    <{0} color="#FF0000">
                        <pose x="2" y="3" theta="4"/>
                        <geometry>
                            <point x="1" y="2"/>
                            <point x="1" y="3"/>
                            <point x="2" y="2"/>
                        </geometry>
                    </{0}>
                </simulation>""".format(tag)),
                [Struct({'type':'robot',
                        'robot':{'type':'A',
                                'pose':Pose(1,2,3),
                                'color':None,
                                'options':None},
                        'supervisor':{'type':'B','options':None}}),
                Struct({'type':tag,
                        'pose':Pose(2,3,4),
                        'color':0xFF0000,
                        'points':[(1,2),(1,3),(2,2)]})])
            # More points
            self.assertEqual(
                self.parser.parse_string("""
                <simulation>
                    <robot type="A">
                        <pose x="1" y="2" theta="3"/>
                        <supervisor type="B"/>
                    </robot>
                    <{0} color="#FF0000">
                        <pose x="2" y="3" theta="4"/>
                        <geometry>
                            <point x="1" y="2"/>
                            <point x="1" y="3"/>
                            <point x="2" y="2"/>
                            <point x="2.25" y="2.125"/>
                            <point x="23.125" y="22.25"/>
                        </geometry>
                    </{0}>
                </simulation>""".format(tag)),
                [Struct({'type':'robot',
                        'robot':{'type':'A',
                                'pose':Pose(1,2,3),
                                'color':None,
                                'options':None},
                        'supervisor':{'type':'B','options':None}}),
                Struct({'type':tag,
                        'pose':Pose(2,3,4),
                        'color':0xFF0000,
                        'points':[(1,2),(1,3),(2,2),(2.25,2.125),(23.125,22.25)]})])
        
        test_polygon('obstacle')
        test_polygon('marker')
        
    def test_bad_polygon(self):

        def test_polygon(tag):
            # No pose
            self.assertRaises(XMLFormatError, self.parser.parse_string,
                """
                <simulation>
                    <robot type="A">
                        <pose x="1" y="2" theta="3"/>
                        <supervisor type="B"/>
                    </robot>
                    <{0}>
                        <geometry>
                            <point x="1" y="2"/>
                            <point x="1" y="3"/>
                            <point x="2" y="2"/>
                        </geometry>
                    </{0}>
                </simulation>""".format(tag))
            # No pose y
            self.assertRaises(XMLFormatError, self.parser.parse_string,
                """<simulation>
                       <robot type="A">
                           <pose x="1" y="2" theta="3"/>
                           <supervisor type="B"/>
                       </robot>
                       <{0} color="#FF0000">
                           <pose x="2" theta="4"/>
                           <geometry>
                               <point x="1" y="2"/>
                               <point x="1" y="3"/>
                               <point x="2" y="2"/>
                           </geometry>
                       </{0}>
                   </simulation>""".format(tag))
            # Two poses
            self.assertRaises(XMLFormatError, self.parser.parse_string,
                """<simulation>
                       <robot type="A">
                           <pose x="1" y="2" theta="3"/>
                           <supervisor type="B"/>
                       </robot>
                       <{0} color="#FF0000">
                           <pose x="2" y="4" theta="4"/>
                           <pose x="2" y="3" theta="4"/>
                           <geometry>
                               <point x="1" y="2"/>
                               <point x="1" y="3"/>
                               <point x="2" y="2"/>
                           </geometry>
                       </{0}>
                   </simulation>""".format(tag))
            # No point x
            self.assertRaises(XMLFormatError, self.parser.parse_string,
                """<simulation>
                       <robot type="A">
                           <pose x="1" y="2" theta="3"/>
                           <supervisor type="B"/>
                       </robot>
                       <{0} color="#FF0000">
                           <pose x="2" y="3" theta="4"/>
                           <geometry>
                               <point x="1" y="2"/>
                               <point y="3"/>
                               <point x="2" y="2"/>
                           </geometry>
                       </{0}>
                   </simulation>""".format(tag))
            # No point y
            self.assertRaises(XMLFormatError, self.parser.parse_string,
                """<simulation>
                       <robot type="A">
                           <pose x="1" y="2" theta="3"/>
                           <supervisor type="B"/>
                       </robot>
                       <{0} color="#FF0000">
                           <pose x="2" y="3" theta="4"/>
                           <geometry>
                               <point x="1" y="2"/>
                               <point y="3"/>
                               <point x="2" y="2"/>
                           </geometry>
                       </{0}>
                   </simulation>""".format(tag))
            # No geometry
            self.assertRaises(XMLFormatError, self.parser.parse_string,
                """<simulation>
                       <robot type="A">
                           <pose x="1" y="2" theta="3"/>
                           <supervisor type="B"/>
                       </robot>
                       <{0} color="#FF0000">
                           <pose x="2" y="3" theta="4"/>
                       </{0}>
                   </simulation>""".format(tag))
            # Two points
            self.assertRaises(XMLFormatError, self.parser.parse_string,
                """<simulation>
                       <robot type="A">
                           <pose x="1" y="2" theta="3"/>
                           <supervisor type="B"/>
                       </robot>
                       <{0} color="#FF0000">
                           <pose x="2" y="3" theta="4"/>
                           <geometry>
                               <point x="1" y="2"/>
                               <point x="2" y="2"/>
                           </geometry>                           
                       </{0}>
                   </simulation>""".format(tag))
            # One point
            self.assertRaises(XMLFormatError, self.parser.parse_string,
                """<simulation>
                       <robot type="A">
                           <pose x="1" y="2" theta="3"/>
                           <supervisor type="B"/>
                       </robot>
                       <{0} color="#FF0000">
                           <pose x="2" y="3" theta="4"/>
                           <geometry>
                               <point x="1" y="2"/>
                           </geometry>                           
                       </{0}>
                   </simulation>""".format(tag))
            # Zero points
            self.assertRaises(XMLFormatError, self.parser.parse_string,
                """<simulation>
                       <robot type="A">
                           <pose x="1" y="2" theta="3"/>
                           <supervisor type="B"/>
                       </robot>
                       <{0} color="#FF0000">
                           <pose x="2" y="3" theta="4"/>
                           <geometry>
                           </geometry>                           
                       </{0}>
                   </simulation>""".format(tag))
            
            
        test_polygon('obstacle')
        test_polygon('marker')