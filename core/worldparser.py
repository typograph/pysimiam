import xml.parsers.expat as expat
from core.struct import Struct
from core.pose import Pose
import re

class XMLFormatError(Exception):
    pass

class StrictParser:
    """:class:StrictParser is based on the expat XML parser.
       It parses an XML-like text file based on a concept of 'contexts',
       where every XML tag defines a context. The XML tags are assumed to
       contain no character data, only nested tags, that define further
       contexts.
       
       xxxxxxxxxxxxxx
       Subclassing
       xxxxxxxxxxxxxx
       
       To use the parser, you need to subclass it, as the base class
       only accepts empty XML.
       
       Subclassing requires redefining `self._contexts` to match the expected
       XML structure.
       `self._contexts` is a dictionary, with XML tags (context names) as keys and
       tuples (parser, subcontexts) as values.
       The `subcontexts` part is a list of strings,
       corresponding to possible contexts nested inside this context.
       If a nested tag is encountered that does not occur in this list,
       a :class:XMLFormatError is raised.
       The `parser` function is called for every occurence of a context.
       It can return a value, that is a result of the parsing.
       
       For example to parse XML corresponding to the following DTD scheme::
       
       !DOCTYPE CATALOG [ 
            <!ELEMENT CATALOG (BOOK|DVD)+>
            <!ELEMENT BOOK (AUTHOR+)>
            <!ELEMENT AUTHOR EMPTY>
            <!ELEMENT DVD EMPTY>
            <!ATTLIST BOOK
                TITLE CDATA #REQUIRED
                YEAR  CDATA #REQUIRED
                PUBLISHER CDATA #IMPLIED
            >
            <!ATTLIST AUTHOR NAME CDATA #REQUIRED>
            <!ATTLIST DVD
                TITLE CDATA #REQUIRED
                YEAR  CDATA #REQUIRED
            >
        ]> 
       
       the following contexts dictionary might be appropriate::
       
       self._contexts = {
        'global': (self.parse_global, ['catalog']),
        'catalog': (self.parse_catalog, ['book','dvd']),
        'book': (self.parse_book, ['author']),
        'author':(self.parse_author, []),
        'dvd':(self.parse_dvd, [])        
       }
       
       This dictionary is enough to ensure that no extra tags appear
       in the file. To follow the DTD closer, the parser functions
       have to be defined accordingly.
       
       xxxxxxxxxxxxxxx
       Parser function
       xxxxxxxxxxxxxxx
       
       The parser function should accept all possible tag attributes
       plus all subcontexts. All those are passed in as keyword parameters.
       For example, if the following piece of XML is parsed::
       
       <outer x="2" y="2">
         <inner t="Hello, beautiful!"/>
       </outer>
       
       then the parser function for 'inner' will be called as follows::
       
       parse_inner(t='Hello, beautiful!')
       
       and supposing this function just returns the value of t, the parser
       function for 'outer' will receive the following parameters::
       
       parse_outer(x="2",y="2",inner=['Hello, beautiful!'])
       
       For the DTD scheme mentioned above, the parser function definions might
       look like this::
       
       def parse_global(self,catalog)       
       def parse_catalog(self, book=[], dvd=[])
       def parse_book(self, title, year, publisher=None, author)
       def parse_author(self, name)
       def parse_dvd(self, title, year)
       
       These definitions ensure e.g. that books with no authors or DVDs without title
       will raise runtime errors. On the other hand, books without publishers will be accepted.
       Note that `book` and `dvd` parameters should have default values to ensure
       catalogs without DVDs or books respectively are parsed correctly.
       Further checking should be done in the function code, e.g. to reject empty catalogs.
       
       xxxxxxxxxxxxxxxx
       Using the parser
       xxxxxxxxxxxxxxxx

       To use the parser, call parse_string or parse_file method.
       The return value of the parser function for context 'global'
       will be returned from that call.
    """

    whitespace = re.compile(r'^\s*$') # To ignore whitespace CDATA
    
    def __init__(self):

        self._subtag_suffix = ''

        self.reset()
        
        # XML tags
        self._contexts = {'global': (None, []) }
        
    def reset(self):
        
        self._context = 'global'

        # Tag stack to check inconsistencies
        self._tags = ['global']

        # Attribute stacks to collect subcontexts
        self._attrs = [0,{}]
        

    def __enter__(self):
        self.reset()

        self._parser = expat.ParserCreate()
        self._parser.StartElementHandler = self.start
        self._parser.EndElementHandler = self.end
        self._parser.CharacterDataHandler = self.data
        
        return self._parser

    def __exit__(self, exc_type, exc_value, traceback):
        del self._parser

    def parse_string(self, data):
        """Parses the string `data` as XML and returns the result
           of a call to the parser of context 'global'.
        """
        try:
            with self as parser:
                parser.Parse(data, True)
                result_parser = self._contexts['global'][0]
                if result_parser is not None:
                    return result_parser(**self._attrs[-1])
        except expat.ExpatError as e:
            raise XMLFormatError("[{}] {}".format(e.code,str(e)))

    def parse_file(self, filename):
        """Parses the XML file 'filename` and returns the result
           of a call to the parser of context 'global'.
        """
        with open(filename,'r') as f:
            try:
                with self as parser:
                    parser.ParseFile(f)
                result_parser = self._contexts['global'][0]
                if result_parser is not None:
                    return result_parser(**self._attrs[-1])
            except expat.ExpatError as e:
                raise XMLFormatError("[{}] {}".format(e.code,str(e)))

    def subtag_attr_name(self,tag):
        """Defines the name of keyword parameter corresponding to nested tags.
           Redefine this or self._subtag_suffix in subclasses to have parameter name you like.
        """
        return tag + self._subtag_suffix

    def start(self, tag, attrs):
        """Start of the tag: pushes current context on stack"""
        
#        print('START : {}\nCONTEXT : {}'.format(tag,self._context))
        
        if tag not in self._contexts[self._context][1]:
            raise XMLFormatError('Invalid tag in {} on line {}: {}'.
                                 format(self._context,self._parser.CurrentLineNumber,tag))
        self._tags.append(self._context)
        self._context = tag
        self._attrs.append(self._parser.CurrentLineNumber)
        self._attrs.append(attrs)
        
    def end(self, tag):
        """End of the tag: calls the context parser and pops previous context from stack"""

#        print('END : {}\nCONTEXT : {}'.format(tag,self._context))
        if (self._context != tag):
            raise XMLFormatError('Invalid closing tag on line {}: {}'.
                                 format(self._parser.CurrentLineNumber,tag))
        parser = self._contexts[self._context][0]
        attrs = self._attrs.pop()
        attrline = self._attrs.pop()
        self._context = self._tags.pop()
#        print('CONTEXT : {}'.format(self._context))
        if parser is not None:
            try:
                result = parser(**attrs)
            except Exception as e:
                raise XMLFormatError("Format error on line {}: {}".format(attrline,str(e)))
            attrs = self._attrs[-1]
            tag_attr = self.subtag_attr_name(tag)
            if tag_attr not in attrs:
                attrs[tag_attr] = []
            attrs[tag_attr].append(result)

    def data(self, data):
        """Placeholder for parsing characted data inside tag.
           Currently ignores whitespace and raises XMLFormatError in other cases.
        """
        # There are no character data
        if self.whitespace.match(data) is None:
            raise XMLFormatError("Non-empty tag on line {}".
                                 format(self._parser.CurrentLineNumber))

class WorldParser(StrictParser):
    """This parser would parse a simulation file in XML format
       and return a list of world objects as Struct's.
    """

    def __init__(self):
        
        StrictParser.__init__(self)
                
        # Context : parser(**attrs), subcontexts
        
        self._subtag_suffix = "s"
        
        self._contexts = {
            'global': (self.parse_full, ['simulation']),
            'app': (None,[]),
            'simulation': (self.parse_simulation, ['app','robot','obstacle','marker']),
            'robot': (self.parse_robot, ['pose','supervisor']),
            'obstacle': (self.parse_obstacle,['pose','geometry']),
            'marker': (self.parse_marker,['pose','geometry']),
            'geometry': (self.parse_geometry,['point']),
            'supervisor': (self.parse_supervisor,[]),
            'point': (self.parse_point, []),
            'pose': (self.parse_pose, [])
            }
            
    def parse_full(self,simulations,apps=None):
        if len(simulations) != 1:
            print("\n",simulations[0])
            print(simulations[1])
            raise XMLFormatError('More than one "simulation" tag')
        return simulations[0]
                
    def parse_simulation(self, robots, obstacles=[], markers=[]):
        if len(robots) < 1:
            raise XMLFormatError('No robots found')
        return robots + obstacles + markers

    def parse_robot(self, type, poses, supervisors, color=None, options=None):

        if len(poses) != 1:
            raise XMLFormatError('More than one pose for robot {}'.format(type))
        if len(supervisors) != 1:
            raise XMLFormatError('More than one supervisor for robot {}'.format(type))

        if options is not None:
            options = Struct(options)

        return Struct({'type':'robot',
                       'robot':{'type':type,
                                'pose':poses[0],
                                'color':self._parse_color(color),
                                'options':options},
                       'supervisor':supervisors[0]})
    
    def parse_supervisor(self, type, options=None):
        if options is not None:
            options = Struct(options)
        return Struct({'type':type, 'options':options})

    def parse_pose(self,x,y,theta):
        return Pose(float(x),float(y),float(theta))

    def parse_obstacle(self,poses,geometrys,color=None):
        if len(poses) != 1:
            raise XMLFormatError('More than one pose for obstacle')
        if len(geometrys) != 1:
            raise XMLFormatError('More than one geometry for obstacle')
        return Struct({'type':'obstacle',
                       'pose':poses[0],
                       'color':self._parse_color(color),
                       'points':geometrys[0]})

    def parse_marker(self,poses,geometrys,color=None):
        if len(poses) != 1:
            raise XMLFormatError('More than one pose for marker')
        if len(geometrys) != 1:
            raise XMLFormatError('More than one geometry for marker')
        return Struct({'type':'marker',
                       'pose':poses[0],
                       'color':self._parse_color(color),
                       'points':geometrys[0]})

    def parse_geometry(self,points):
        if len(points) < 3:
            raise XMLFormatError("Too few points for an object: {}".format(len(point)))
        return points

    def parse_point(self,x,y):
        return float(x),float(y)
    
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
        raise XMLFormatError('Bad color value in XML on line {}: {}'.format(self._parser.CurrentLineNumber,color))

