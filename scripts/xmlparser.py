import xml.etree.ElementTree as ET

class XMLParser(object):
    """
    A class to handle parsing of XML files for the simulator and parameters
    configuration files.

    Public API:
        parse(self, template) ----> the parsing function
        validate(self, schema) ---> validates the XML    
    """

    _file = None
    _root = None
    
    def __init__(self, file_):
        """ 
        Construct a new XMLParser instance

        Scope:
            Public
        Parameters:
            file_ ---> path to the file containing the XML
        Return:
            A new XMLParser instance  
        """

        _tree = None
        try:
            _tree = ET.parse(file_)
        except IOError:
            raise Exception('[XMLParser.__init__] Could not open ' + file_)

        self._root = _tree.getroot()
        self._file = file_

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

        result = {}
        for sub in self._root:
            sub_dict = {}
            try:
                if not sub.get('id') == None:
                    for attr in sub.items():
                        if not attr[0] == 'id': sub_dict[attr[0]] = float(attr[1])
                    result[(sub.tag, sub.get('id'))] = sub_dict
                else:
                    for attr in sub.items():
                        sub_dict[attr[0]] = float(attr[1])
                    result[sub.tag] = sub_dict
            except:
                raise Exception(
                    '[XMLParser._parse_parameters] Bad value in XML!')

        return {self._root.tag : result} 
 
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
                    '[XMLParser.parse_simulation] No supervisor specified!')

            pose = robot.find('pose')
            if pose == None:
                raise Exception(
                    '[XMLParser.parse_simulation] No pose specified!')

            try:
                x, y, theta = pose.get('x'), pose.get('y'), pose.get('theta')
                if x == None or y == None or theta == None:
                    raise Exception(
                        '[XMLParser.parse_simulation] Invalid pose!')

                simulator_objects.append(('robot',
                                          robot_type,
                                          supervisor.attrib['type'],
                                          (float(x),
                                           float(y),
                                           float(theta))))
            except ValueError:
                raise Exception(
                    '[XMLParser.parse_simulation] Invalid robot (bad value)!') 

        # obstacles
        for obstacle in self._root.findall('obstacle'):
            pose = obstacle.find('pose')
            if pose == None:
                raise Exception(
                    '[XMLParser.parse_simulation] No pose specified!')

            geometry = obstacle.find('geometry')
            if geometry == None:
                raise Exception(
                    '[XMLParser.parse_simulation] No geometry specified!')
            try:
                points = []
                for point in geometry.findall('point'):
                    x, y = point.get('x'), point.get('y')
                    if x == None or y == None:
                        raise Exception(
                            '[XMLParser.parse_simulation] Invalid point!')
                    points.append((float(x), float(y)))

                if len(points) < 3:
                    raise Exception(
                        '[XMLParser.parse_simulation] Too few points!')

                x, y, theta = pose.get('x'), pose.get('y'), pose.get('theta')
                if x == None or y == None or theta == None:
                    raise Exception(
                        '[XMLParser.parse_simulation] Invalid pose!')

                simulator_objects.append(('obstacle',
                                          (float(x),
                                           float(y),
                                           float(theta)),
                                          points))
            except ValueError:
                raise Exception(
                    '[XMLParser.parse_simulation] Invalid obstacle (bad value)!')

        return simulator_objects 
 
    def parse(self, template):
        """ 
        Call the correct parsing function 
       
        Scope:
            Public 
        Parameters:
            template ---> 'simulator' or 'parameters'
        Return:
            The result of parsing the file (type dependent on the template)
        """
 
        if template == "parameters":
            return self._parse_parameters()
        elif template == "simulation":
            return self._parse_simulation()
        else:
            raise Exception(
                '[XMLParser.parse] Unknown template!')

    def validate(self, schema):
        """ 
        Validate the xml against a given schema.

        Scope:
            Public
        Parameters:
            schema ---> path to the schema (.xsd) file
        Return:
            True if schema validates successfully, False otherwise 
        """

        # TODO
        return True

