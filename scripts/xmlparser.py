import xml.etree.ElementTree as ET

class XMLParser(object):
    _tree = None
    _root = None
    
    def __init__(self, file_):
        try:
            self._tree = ET.parse(file_)
            self._root = self._tree.getroot()
        except IOError:
            raise Exception('[XMLParser.__init__] Could not open ' + file_)
       
    def parse_parameters(self):
        goals = []
        for goal in self._root.findall('goal'):
            try:
                points = goal.findall('point')
                if points == None:
                    raise Exception(
                        '[XMLParser.parse_parameters] No goal point specified')
                for point in points:
                    x, y = point.get('x'), point.get('y')
                    if x == None or y == None:
                        raise Exception(
                            '[XMLParser.parse_parameters] Invalid goal point!')
                    goals.append((float(x), float(y))) 
            except ValueError:
                raise Exception(
                    '[XMLParser.parse_parameters] Invalid goal (bad value)!')

        parameters = []
        for parameter in self._root.findall('pid'):
            try:
                identifier = parameter.get('id')
                
                angle = parameter.find('angle')
                if angle == None:
                    raise Exception(
                        '[XMLParser.parse_parameters] No angle specified!')
                theta = angle.get('theta')
                if theta == None:
                    raise Exception(
                        '[XMLParser.parse_parameters] No theta specified!')
 
                velocity = parameter.find('velocity')
                if velocity == None:
                    raise Exception(
                        '[XMLParser.parse_parameters] No velocity specified!')
                v = velocity.get('v')
                if v == None:
                    raise Exception(
                        '[XMLParser.parse_parameters] No v specified!')

                gains = parameter.find('gains')
                if gains == None:
                    raise Exception(
                        '[XMLParser.parse_parameters] No gains specified!')
                kp, ki, kd = gains.get('kp'), gains.get('ki'), gains.get('kd')
                if kp == None or ki == None or kd == None:
                    raise Exception(
                        '[XMLParser.parse_parameters] Must specify all gains!')

                parameters.append(
                    ('pid',
                     identifier, 
                     float(theta), 
                     float(v), 
                     [float(kp), float(ki), float(kd)]))
            except ValueError:
                raise Exception(
                    '[XMLParser.parse_parameters] Invalid pid (bad value)!')

        return (goals, parameters)
     
    def parse_simulation(self):
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
