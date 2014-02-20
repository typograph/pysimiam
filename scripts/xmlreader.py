import xml.etree.ElementTree as ET
from xmlobject import XMLObject
from helpers import Struct
from pose import Pose

class XMLReader(XMLObject):
    """
    A class to handle reading and parsing of XML files for the simulator and 
    parameters configuration files.
    """

    _file = None
    _root = None

    def __init__(self, file_, template):
        """ 
        Construct a new XMLReader instance

        Scope:
            Public
        Parameters:
            file_ ------> path to the file containing the XML
            template ---> 'simulator' or 'parameters'
        Return:
            A new XMLReader instance  
        """

        super(XMLReader, self).__init__(file_, template)

        _tree = None
        try:
            _tree = ET.parse(file_)
        except IOError:
            raise Exception('[XMLReader.__init__] Could not open ' + str(file_))
        except ET.ParseError:
            raise Exception('[XMLReader.__init__] Could not parse ' + str(file_))
         
        self._root = _tree.getroot()

    def _parse_parameters(self):
        """ 
        Parse a parameters configuration file
     
        Scope:
            Private 
        Parameters:
            None
        Return:
            A dictionary encapsulating the parameters. 
        """

        def parse_tag(rdict, tag):
            """Fill dict with data from tag"""
            for attr, value in tag.items():
                if attr != "id":
                    try:
                        rdict.append((attr,float(value)))
                    except ValueError:
                        rdict.append((attr,value))
                       
            for child in tag:
                sub = []
                id_ = child.get('id',None)
                if id_ is not None:
                    rdict.append(((child.tag, id_),sub))
                else:
                    rdict.append((child.tag,sub))
                parse_tag(sub, child)

        result = []
        parse_tag(result, self._root)

        return result
 
    def _parse_color(self, color):
        """
        Convert a color attribute value to int
        
        None will yield None, '#FFACDD' will yield 0xFFACDD
        
        Scope:
            Private
        Parameters:
            color ----> the color to be converted
        Return:
            An integer value in the (AA)RRGGBB format
        """
        if color is None:
            return color
        if color[0] == "#":
            return int(color[1:],16)
        color = color.lower()
        if color == 'black':
            return 0x000000
        if color == 'red':
            return 0xFF0000
        if color == 'green':
            return 0x00FF00
        if color == 'blue':
            return 0x0000FF        
        raise Exception('[XMLReader._parse_color] Bad color value in XML!')
 
    def _parse_simulation(self):
        """ 
        Parse a simulation configuration file
       
        Scope: 
            Private 
        Parameters:
            None
        Return:
            A list of the objects in the simulation. 
        """

        simulator_objects = []

        # robots
        for robot in self._root.findall('robot'):
            robot_type = robot.get('type')
            supervisor = robot.find('supervisor')
            if supervisor == None:
                raise Exception(
                    '[XMLReader._parse_simulation] No supervisor specified!')

            pose = robot.find('pose')
            if pose == None:
                raise Exception(
                    '[XMLReader._parse_simulation] No pose specified!')

            try:
                x, y, theta = pose.get('x'), pose.get('y'), pose.get('theta')
                if x == None or y == None or theta == None:
                    raise Exception(
                        '[XMLReader._parse_simulation] Invalid pose!')

                robot_color = self._parse_color(robot.get('color'))

                simulator_objects.append(Struct({'type':'robot',
                                                 'robot':{'type':robot_type,
                                                          'pose':Pose(float(x), float(y), float(theta)),
                                                          'color':robot_color,
                                                          'options':robot.get('options',None)},
                                                 'supervisor':{'type':supervisor.attrib['type'],
                                                               'options':supervisor.get('options',None)}}))
            except ValueError:
                raise Exception(
                    '[XMLReader._parse_simulation] Invalid robot (bad value)!') 

        # obstacles
        for obstacle in self._root.findall('obstacle'):
            pose = obstacle.find('pose')
            if pose == None:
                raise Exception(
                    '[XMLReader._parse_simulation] No pose specified!')

            geometry = obstacle.find('geometry')
            if geometry == None:
                raise Exception(
                    '[XMLReader._parse_simulation] No geometry specified!')
            try:
                points = []
                for point in geometry.findall('point'):
                    x, y = point.get('x'), point.get('y')
                    if x == None or y == None:
                        raise Exception(
                            '[XMLReader._parse_simulation] Invalid point!')
                    points.append((float(x), float(y)))

                if len(points) < 3:
                    raise Exception(
                        '[XMLReader._parse_simulation] Too few points!')

                x, y, theta = pose.get('x'), pose.get('y'), pose.get('theta')
                if x == None or y == None or theta == None:
                    raise Exception(
                        '[XMLReader._parse_simulation] Invalid pose!')

                color = self._parse_color(obstacle.get('color'))
                simulator_objects.append(Struct({'type':'obstacle',
                                                 'polygon':{'pose':Pose(float(x),float(y),float(theta)),
                                                            'color':color,
                                                            'points':points}}))
            except ValueError:
                raise Exception(
                    '[XMLReader._parse_simulation] Invalid obstacle (bad value)!')
        
        # background
        for marker in self._root.findall('marker'):
            pose = marker.find('pose')
            if pose == None:
                raise Exception(
                    '[XMLReader._parse_simulation] No pose specified!')
            
            geometry = marker.find('geometry')
            if geometry == None:
                raise Exception(
                    '[XMLReader._parse_simulation] No geometry specified!')
            try:
                points = []
                for point in geometry.findall('point'):
                    x, y = point.get('x'), point.get('y')
                    if x == None or y == None:
                        raise Exception(
                            '[XMLReader._parse_simulation] Invalid point!')
                    points.append((float(x), float(y)))
                    
                if len(points) < 3:
                    raise Exception(
                        '[XMLReader._parse_simulation] Too few points!')
                
                x, y, theta = pose.get('x'), pose.get('y'), pose.get('theta')
                if x == None or y == None or theta == None:
                    raise Exception(
                        '[XMLReader._parse_simulation] Invalid pose!')
                
                color = self._parse_color(marker.get('color'))
                simulator_objects.append(Struct({'type':'marker',
                                                 'polygon':{'pose':Pose(float(x),float(y),float(theta)),
                                                            'color':color,
                                                            'points':points}}))
            except ValueError:
                raise Exception(
                    '[XMLReader._parse_simulation] Invalid marker (bad value)!')
    
        return simulator_objects
 
    def read(self):
        """ 
        Read in and parse the XML given in *file_* representing the specified *template*.

|        *Parameters:* 
|         None
|        *Return:*     
|         The result of reading and parsing the file.  The type of return is dependent on the template, as follows:
|           
|           1) **simulation**: a list of tuples representing robots, obstacles, and markers, as follows:
|                       ('robot', *robot_type*, *supervisor_type*, *pose*, *color*)
|                       ('obstacle', *pose*, [*point1*, *point2*, *point3*, ...], *color*)
|                       ('marker', *pose*, [*point1*, *point2*, *point3*, ...], *color*)
|             
|           2) **parameters**: a dictionary representing the structure of the XML, as follows:
|                       { *root_element*:
|                           { *parameter_name*: {*attribute_name*: *attribute_value*, ... },
|                             ...
|                             (*parameter_name*, *parameter_id*): {*attribute_name*: *attribute_value*, ... },
|                             ...
|                           }
|                       }
        """
 
        if self._template == "parameters":
            return self._parse_parameters()
        elif self._template == "simulation":
            return self._parse_simulation()
        else:
            raise Exception(
                '[XMLReader.read] Unknown template!')

