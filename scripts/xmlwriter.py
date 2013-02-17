from xmlobject import XMLObject

class XMLWriter(XMLObject):
    """
    A class to handle saving XML files for the simulator and parameters
    entered via the UI.

    Public API:
        write(self) --> write the tree as XML to the given file
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

        # Root must be a dictionary       
        if not isinstance(self._tree, dict):
            raise Exception(
                'XMLWriter._write_parameters] Tree must be a dictionary!')
 
        root_tag = self._tree.keys()[0]
        
        result = "<" + str(root_tag) + ">\n"
        parameters = self._tree.itervalues().next()
        for p in parameters.keys():
            # parameter key must be either a string or a tuple
            if isinstance(p, basestring):  
                parameter_string = "<" + str(p) + " "
            elif isinstance(p, tuple):
                parameter_string = "<" + p[0] + " id=\"" + p[1] + "\" "
            else:
                raise Exception(
                    '[XMLWriter._write_parameters] Invalid key: ' + str(p))  
       
            # Value of a parameter must be a dictionary 
            if not isinstance(parameters[p], dict):
                raise Exception(
                    'XMLWriter._write_parameters] Attributes must be stored' 
                    + 'in a dictionary!')

            attribute_strings = []
            for attribute in parameters[p].keys():
                # Attribute must be {str: float} or {str: int}
                if (not isinstance(parameters[p][attribute], float) and \
                   not isinstance(parameters[p][attribute], int)) or \
                   not isinstance(attribute, basestring):
                    raise Exception(
                        '[XMLWriter._write_parameters] Invalid entry: ' + \
                        str(attribute) + ": " + str(parameters[p][attribute]))
  
                attribute_strings.append(
                    str(attribute) + "=\"" 
                    + str(parameters[p][attribute]) 
                    + "\"")
            parameter_string += " ".join(attribute_strings)
            result = result + "    " + parameter_string + " />\n"
 
        result += "</" + str(root_tag) + ">\n"
       
        with open(self._file, 'w') as f: 
            f.write(result)

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
        Write out the tree as XML to the given file

        Scope:
            Public
        Paramaters:
            None
        Return:
            void
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
