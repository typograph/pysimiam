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
        
    def parse(self):
        simulator_objects = []
    
        # robots
        for robot in self._root.findall('robot'):
            supervisor = robot.find('supervisor')
            if supervisor == None:
                raise Exception('[XMLParser.parse] No supervisor specified!')
            
            pose = robot.find('pose')
            if pose == None:
                raise Exception('[XMLParser.parse] No pose specified!')
            
            try:
                x, y, theta = pose.get('x'), pose.get('y'), pose.get('theta')
                if x == None or y == None or theta == None:
                    raise Exception('[XMLParser.parse] Invalid pose!')
                
                simulator_objects.append(('robot', 
                                          supervisor.attrib['type'], 
                                          (float(x), 
                                           float(y), 
                                           float(theta))))
            except ValueError:
                raise Exception(
                    '[XMLParser.parse] Invalid robot (likely bad coordinates)!')
        
        # obstacles
        for obstacle in self._root.findall('obstacle'):
            pose = obstacle.find('pose')
            if pose == None:
                raise Exception('[XMLParser.parse] No pose specified!')
            
            geometry = obstacle.find('geometry')
            if geometry == None:
                raise Exception('[XMLParser.parse] No geometry specified!')
            try:
                points = []
                for point in geometry.findall('point'):
                    x, y = point.get('x'), point.get('y')
                    if x == None or y == None:
                        raise Exception('[XMLParser.parse] Invalid point!')
                    points.append((float(x), float(y)))
                    
                if len(points) < 3:
                    raise Exception('[XMLParser.parse] Too few points in geometry!')
                
                x, y, theta = pose.get('x'), pose.get('y'), pose.get('theta')
                if x == None or y == None or theta == None:
                    raise Exception('[XMLParser.parse] Invalid pose!')
                
                simulator_objects.append(('obstacle',
                                          (float(x),
                                           float(y),
                                           float(theta)),
                                          points))
            except ValueError:
                raise Exception(
                    '[XMLParser.parse] Invalid obstacle (likely bad coordinates)!')
    
        return simulator_objects
