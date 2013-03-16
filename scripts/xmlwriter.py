from xmlobject import XMLObject
import xml.etree.ElementTree as ET
import xml.dom.minidom as dom

class XMLWriter(XMLObject):
    """
    A class to handle saving XML files for the simulator and parameters
    entered via the UI.
    """

    _file = None
    _root = None
    _tree = None
    
    def __init__(self, file_, template, tree):
        """ 
        Construct a new XMLWriter instance

        Scope:
            Public
        Parameters:
            file ------> path to the file to which XML should be saved
            template ---> 'simulator' or 'parameters'
        Return:
            A new XMLWriter instance  
        """

        super(XMLWriter, self).__init__(file_, template)

        self._tree = tree

    def _write_parameters(self):
        """ 
        Write out the parameters to the XML file.

        Scope:
            Private
        Parameters:
            None
        Return:
            void
        """

        def write_subtree(root, tree):
            for key, value in tree:
                # Parameter key must be either a string or a tuple                
                # Parameter value is either a list or a number/string:
                if isinstance(value, list):
                    if isinstance(key, basestring):
                        tag = ET.SubElement(root, key)
                    elif isinstance(key, tuple):
                        tag = ET.SubElement(root, str(key[0]))
                        tag.set("id",str(key[1]))
                    else:
                        raise Exception('[XMLWriter._write_parameters] Invalid key: {}'.format(key))
                    write_subtree(tag, value)
                else:
                    if isinstance(key, basestring):
                        root.set(key, str(value))
                    else:
                        raise Exception('[XMLWriter._write_parameters] Invalid key: {}'.format(key))

        xml = ET.ElementTree(ET.Element('parameters'))
        xml_root = xml.getroot()
 
        write_subtree(xml_root, self._tree)
        
        with open(self._file, 'w') as f: 
            dom.parseString(ET.tostring(xml_root)).writexml(f,'','    ','\n')

    def _write_simulation(self):
        """ 
        Write out the simulation to the XML file.

        Scope:
            Private
        Parameters:
            None
        Return:
            void
        """

        # TODO
        pass

    def write(self):
        """
        Write out the *tree* as XML representing the specified *template* to the given *file_*. 

|        *Paramaters:* 
|         None
|        *Return:* 
|         void
        """
        
        if self._tree == None:
            raise Exception(
                '[XMLWriter._write_simulation] No tree specified to write!')

        if self._template == "parameters":
            return self._write_parameters()
        elif self._template == "simulation":
            return self._write_simulation()
        else:
            raise Exception(
                '[XMLReader.write] Unknown template!') 
