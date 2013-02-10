import unittest
from xmlparser import XMLParser

class TestXMLParser(unittest.TestCase):

    # parse_simulation
    def test_parse_simulation_legal(self):
        xml_parser = XMLParser("../testfiles/settings.xml")
        objects = xml_parser.parse_simulation()

        assert objects[0] == \
            ('robot', 
             'khepera3.K3Supervisor', 
             (1.0, 1.0, 1.5708))
        assert objects[1] == \
            ('obstacle', 
             (1.0, 1.2, 0.0), 
             [(0.0, 0.0), (0.3, 0.0), (0.3, 0.3), (0.0, 0.3)])
        assert objects[2] == \
            ('obstacle', 
             (-0.5, 0.0, 0.7854), 
             [(0.0, 0.0), (0.3, 0.0), (0.3, 0.3), (0.0, 0.3)])
        assert objects[3] == \
            ('obstacle', 
             (0.65, 0.0, 0.7854), 
             [(0.0, 0.0), (0.3, 0.0), (0.3, 0.3), (0.0, 0.3)])
        assert objects[4] == \
            ('obstacle', 
             (0.2, 0.8, 0.0), 
             [(0.0, 0.0), (0.3, 0.0), (0.3, 0.3), (0.0, 0.3)])
        assert objects[5] == \
            ('obstacle', 
             (-1.0, -1.0, 0.0), 
             [(0.0, 0.0), (1.5, 0.0), (1.5, 0.3), (0.0, 0.3)]) 
        assert objects[6] == \
            ('obstacle', 
             (-1.6, -1.5, 0.0), 
             [(0.0, 0.0), (3.0, 0.0), (3.0, 0.1), (0.0, 0.1)])
        assert objects[7] == \
            ('obstacle', 
             (-1.5, -1.4, 1.5708), 
             [(0.0, 0.0), (3.0, 0.0), (3.0, 0.1), (0.0, 0.1)])
        assert objects[8] == \
            ('obstacle', 
             (1.5, -1.5, 1.5708), 
             [(0.0, 0.0), (3.0, 0.0), (3.0, 0.1), (0.0, 0.1)])
        assert objects[9] == \
            ('obstacle', 
             (-1.5, 1.5, 0.0), 
             [(0.0, 0.0), (3.0, 0.0), (3.0, 0.1), (0.0, 0.1)])
            
    def test_parse_simulation_bad_filename(self):
        self.assertRaises(Exception, XMLParser, "pysimiam_rules")
        
    def test_parse_simulation_no_robot_supervisor(self):
        xml_parser = XMLParser("../testfiles/no_robot_supervisor.xml")
        self.assertRaises(Exception, xml_parser.parse_simulation)
    
    def test_parse_simulation_no_robot_pose(self):
        xml_parser = XMLParser("../testfiles/no_robot_pose.xml")
        self.assertRaises(Exception, xml_parser.parse_simulation)

    def test_parse_simulation_bad_robot_coordinate(self):
        xml_parser = XMLParser("../testfiles/bad_robot_coord.xml")
        self.assertRaises(Exception, xml_parser.parse_simulation)
                
    def test_parse_simulation_no_obstacle_pose(self):
        xml_parser = XMLParser("../testfiles/no_obstacle_pose.xml")
        self.assertRaises(Exception, xml_parser.parse_simulation)
        
    def test_parse_simulation_no_obstacle_geometry(self):
        xml_parser = XMLParser("../testfiles/no_obstacle_geometry.xml")
        self.assertRaises(Exception, xml_parser.parse_simulation)
        
    def test_parse_simulation_bad_obstacle_coordinate(self):
        xml_parser = XMLParser("../testfiles/bad_obstacle_coord.xml")
        self.assertRaises(Exception, xml_parser.parse_simulation)    
        
    def test_parse_simulation_missing_obstacle_coordinate(self):
        xml_parser = XMLParser("../testfiles/missing_obstacle_coord.xml")
        self.assertRaises(Exception, xml_parser.parse_simulation)
        
    def test_parse_simulation_too_few_obstacle_points(self):
        xml_parser = XMLParser("../testfiles/too_few_points.xml")
        self.assertRaises(Exception, xml_parser.parse_simulation)


    # parse_parameters
    def test_parse_parameters_legal(self):
        xml_parser = XMLParser("../testfiles/parameters.xml")
        parameters = xml_parser.parse_parameters()
        print parameters[0]    
        assert(parameters[0] == ('pid', 0.7854, 0.1, [5, 0.1, 0.01]))
 
    def test_parse_parameters_no_theta(self):
        xml_parser = XMLParser("../testfiles/no_theta.xml")
        self.assertRaises(Exception, xml_parser.parse_parameters)

    def test_parse_parameters_no_v(self):
        xml_parser = XMLParser("../testfiles/no_v.xml")
        self.assertRaises(Exception, xml_parser.parse_parameters)
    
    def test_parse_parameters_no_gains(self):
        xml_parser = XMLParser("../testfiles/no_gains.xml")
        self.assertRaises(Exception, xml_parser.parse_parameters)
 
if __name__ == "__main__":
    unittest.main()
