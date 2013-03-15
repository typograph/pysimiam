#!/usr/bin/python2
import xml.etree.ElementTree as ET
import xml.dom.minidom as dom

import sys
import re
from math import sin,cos,atan2,pi,sqrt

"""
This tool converts svg files to world files

It only supports a subset of svg, notably all the groups
except the top one are ignored.

The rectangles in the file will be converted to obstacles.
The paths with more than 2 points are converted to markers.
A path with 1 or 2 points is interpreted as a robot,
with the position of the robot determined by the first point,
and the direction by the second one.

The color of obstacles, markers and robots is taken directly
from the fill color. The stroke color is ignored.

"""

# Change those to get other robots
robot_class = "Khepera3"
robot_supervisor = "K3BlendingSupervisor"

color_re = re.compile('fill:(#[0-9a-fA-F]{6})')
ns_re = re.compile('^(\{[^\}]*\})?(.*)$')
trans_re = re.compile('([^(]*)\(([\-0-9\.,]*)\)')

path_subc = re.compile('[MmZzLlHhVvCcSsQqTtAa]\s*(?:,?\s*[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[1-9][0-9]*)?)*')
path_num  = re.compile('[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[1-9][0-9]*)?')

"""
This class will discard namespace information from the xml
The SVG files tend to have it, but we don't want it
"""
class TreeBuilder_NS(ET.TreeBuilder):
    def start(self,tag,attrs):
        m = ns_re.match(tag)
        if m is not None and m.group(1):
            tag = m.group(2)
            
        attrib = {}
        for key, value in attrs.items():
            m = ns_re.match(key)
            if m is not None and m.group(1):
                attrib[m.group(2)] = value
            else:
                attrib[key] = value

        return ET.TreeBuilder.start(self,tag,attrib)
        
    def end(self,tag):
        m = ns_re.match(tag)
        if m is not None and m.group(1):
            tag = m.group(2)

        return ET.TreeBuilder.end(self,tag)

def ntuples(l,n):
    i = 0
    while i < len(l):
        yield (l[i+k] for k in range(n))
        i += n

def parse_path(pstr):
    points = []
    
    x0, y0 = 0, 0
    last_point_not_saved = True
    
    subcs = path_subc.findall(pstr)
    for subc in subcs:
        command = subc[0]
        numbers = [float(nstr) for nstr in path_num.findall(subc)]

        # Close path
        if command == 'z' or command == 'Z':
            return points
        
        # Relative move
        if command == 'm':
            x0 += numbers[0]
            y0 += numbers[1]
            if len(numbers) == 2: # moveto
                last_point_not_saved = True
            else:
                last_point_not_saved = False
                points.append((x0,y0))
                for x,y in ntuples(numbers[2:],2):
                    x0 += x
                    y0 += y
                    points.append((x0,y0))
            continue
        
        # Absolute move
        if command == 'M':
            x0, y0 = numbers[:2]
            if len(numbers) == 2: # moveto
                last_point_not_saved = True
            else:
                last_point_not_saved = False
                for x,y in ntuples(numbers,2):
                    x0 = x
                    y0 = y
                    points.append((x0,y0))
            continue
        
        # The command is not a move
        if last_point_not_saved:
            points.append((x0,y0))
            last_point_not_saved = False
        
        # Relative lineto or quadratic bezier
        if command == 'l' or command == 't':
            for x,y in ntuples(numbers,2):
                x0 += x
                y0 += y
                points.append((x0,y0))
            continue

        # Absolute lineto or quadratic bezier
        if command == 'L' or command == 'T':
            for x,y in ntuples(numbers,2):
                x0, y0 = x, y
                points.append((x0,y0))
            continue

        # Relative horizontal lineto
        if command == 'h':
            for x in numbers:
                x0 += x
                points.append((x0,y0))
            continue

        # Absolute horizontal lineto
        if command == 'H':
            for x in numbers:
                x0 = x
                points.append((x0,y0))
            continue

        # Relative vertical lineto
        if command == 'v':
            for y in numbers:
                y0 += y
                points.append((x0,y0))
            continue

        # Absolute vertical lineto
        if command == 'V':
            for y in numbers:
                y0 = y
                points.append((x0,y0))
            continue
            
        # Relative bezier curve or ellipse
        if command == 'c' or command == 'a':
            for x1,y1,x2,y2,x,y in ntuples(numbers,6):
                x0 += x
                y0 += y
                points.append((x0,y0))
            continue

        # Absolute bezier curve
        if command == 'C' or command == 'A':
            for x1,y1,x2,y2,x,y in ntuples(numbers,6):
                x0 = x
                y0 = y
                points.append((x0,y0))
            continue
            
        # Relative bezier shorthand or quadratic bezie
        if command == 's' or command == 'q':
            for x2,y2,x,y in ntuples(numbers,4):
                x0 += x
                y0 += y
                points.append((x0,y0))
            continue

        # Absolute bezier shorthand
        if command == 'S' or command == 'Q':
            for x2,y2,x,y in ntuples(numbers,4):
                x0 = x
                y0 = y
                points.append((x0,y0))
            continue
            
    return points

def transform_coords(tstr,points):
    if tstr is None:
        return [(x,-y) for x,y in points]
    
    m = trans_re.match(tstr)
    if m is None:
        print "Invalid transform format"
        return [(x,-y) for x,y in points]
    
    tname = m.group(1)
    topts = [float(v) for v in m.group(2).split(',')]
    
    a11, a12, a13, a21, a22, a23 = 1,0,0,0,1,0
    if tname == 'matrix':
        a11, a21, a12, a22, a13, a23  = topts
    elif tname == 'translate':
        a13, a23 = topts
    elif tname == 'rotate':
        angle = topts[0]*pi/180
        a11 = a22 = cos(angle)
        a12 = -sin(angle)
        a21 = sin(angle)
    elif tname == 'scale':
        a11, a22 = topts

    new_points = []
    for x,y in points:        
        x_new = x*a11 + y*a12 + a13
        y_new = x*a21 + y*a22 + a23
        new_points.append((x_new,-y_new))
    
    return new_points    

if len(sys.argv) < 3:
    print 'usage: svg2world.py input.svg output.xml'
    quit()

try:
    svgfile = ET.parse(sys.argv[1],ET.XMLParser(target = TreeBuilder_NS()))
    root = svgfile.getroot().find('g')
    if root is None:
        raise ValueError("No top-level group in this file")
except Exception as e:
    print 'Invalid svg file'
    print e
    quit()
    
world = ET.ElementTree(ET.Element('simulation'))
world_root = world.getroot()

# Robots:
for circle in root.findall('circle'):
    x = float(circle.get('cx'))
    y = -float(circle.get('cy'))

    name = circle.get('id')
        
    style = circle.get('style')
    color = None
    if style is not None:
        color = color_re.search(style)
    if color is not None:
        robot = ET.SubElement(world_root,'robot',{'type':robot_class,'color':color.group(1)})
    else:
        robot = ET.SubElement(world_root,'robot',{'type':robot_class})

    pose = ET.SubElement(robot,'pose',{'x':str(x),'y':str(y),'theta':"0"})
    geom = ET.SubElement(robot,'supervisor',{'type':robot_supervisor})

# Robots and markers
for path in root.findall('path'):

    style = path.get('style')
    color = None
    if style is not None:
        color = color_re.search(style)

    points = parse_path(path.get('d'))
    if not points:
        continue
    points = transform_coords(path.get('transform'),points)
    
    if len(points) < 3: # Robot
        name = path.get('id')
        
        if color is not None:
            robot = ET.SubElement(world_root,'robot',{'type':robot_class,'color':color.group(1)})
        else:
            robot = ET.SubElement(world_root,'robot',{'type':robot_class})

        x, y = points[0]
        theta = 0
        if len(points) > 1:
            x2, y2 = points[1]
            theta = atan2(y2-y,x2-x)
        pose = ET.SubElement(robot,'pose',{'x':str(x),'y':str(y),'theta':str(theta)})
        geom = ET.SubElement(robot,'supervisor',{'type':robot_supervisor})
        
    else: # Marker   
        if color is not None:
            marker = ET.SubElement(world_root,'marker',{'color':color.group(1)})
        else:
            marker = ET.SubElement(world_root,'marker')
            
        x0, y0 = points[0]
            
        pose = ET.SubElement(marker,'pose',{'x':str(x0),'y':str(y0),'theta':"0"})
        geom = ET.SubElement(marker,'geometry')
        for x, y in points:
            ET.SubElement(geom,'point',{'x':str(x-x0),'y':str(y-y0)})

# Obstacles    
for rect in root.findall('rect'):
    x = float(rect.get('x'))
    y = float(rect.get('y'))
    w = float(rect.get('width'))
    h = float(rect.get('height'))

    points = [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
    points = transform_coords(rect.get('transform'),points)
        
    style = rect.get('style')
    color = None
    if style is not None:
        color = color_re.search(style)
    if color is not None:
        obstacle = ET.SubElement(world_root,'obstacle',{'color':color.group(1)})
    else:
        obstacle = ET.SubElement(world_root,'obstacle')

    x0, y0 = points[0]
        
    pose = ET.SubElement(obstacle,'pose',{'x':str(x0),'y':str(y0),'theta':"0"})
    geom = ET.SubElement(obstacle,'geometry')
    for x, y in points:
        ET.SubElement(geom,'point',{'x':str(x-x0),'y':str(y-y0)})
 
#world.write(sys.argv[2])

with open(sys.argv[2],'w') as f:
    dom.parseString(ET.tostring(world.getroot())).writexml(f,'','    ','\n')

