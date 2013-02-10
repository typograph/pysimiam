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
        parameters = []
        if self._root.tag == 'pid':
            try:
                angle = self._root.find('angle')
                if angle == None:
                    raise Exception(
                        '[XMLParser.parse_parameters] No angle specified!')
                theta = angle.get('theta')
                if theta == None:
                    raise Exception(
                        '[XMLParser.parse_parameters] No theta specified!')
 
                velocity = self._root.find('velocity')
                if velocity == None:
                    raise Exception(
                        '[XMLParser.parse_parameters] No velocity specified!')
                v = velocity.get('v')
                if v == None:
                    raise Exception(
                        '[XMLParser.parse_parameters] No v specified!')

                gains = self._root.find('gains')
                if gains == None:
                    raise Exception(
                        '[XMLParser.parse_parameters] No gains specified!')
                kp, ki, kd = gains.get('kp'), gains.get('ki'), gains.get('kd')
                if kp == None or ki == None or kd == None:
                    raise Exception(
                        '[XMLParser.parse_parameters] Must specify all gains!')

                parameters.append(
                    ('pid', 
                     float(theta), 
                     float(v), 
                     [float(kp), float(ki), float(kd)]))
            except ValueError:
                raise Exception(
                    '[XMLParser.parse_parameters] Invalid pid (bad value)!')
        else:
            # Add other parameter types here (only PID exists currently,
            # but others will certainly follow
            raise Exception('[XMLParser.parse_parameters] Invalid type!')

        return parameters
     
    def parse_simulation(self):
        simulator_objects = []
    
        # robots
        for robot in self._root.findall('robot'):
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
