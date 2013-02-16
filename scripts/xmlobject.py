import xml.etree.ElementTree as ET

class XMLObject(object):
    """
    Base class for XML handling.
    
    Public API:
        validate(self, file_, schema) ------> validate XML against a schema
    """

    _file = None
    _template = None

    def __init__(self, file_, template):
        """ 
        Construct a new XMLObject instance

        Scope:
            Public
        Parameters:
            file_ ------> the XML file
            template ---> 'simulation' or 'parameters'
        Return:
            A new XMLObject instance  
        """
        self._file = file_
        self._template = template

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

        try:
            from lxml import etree
            from lxml.etree import XMLSchema
        except ImportError:
            raise Exception(
                '[XMLObject.validate] Need lxml to validate xml!')

        try:
            xmlschema_doc = etree.parse(schema)
            xmlschema = XMLSchema(xmlschema_doc)
            xml_doc = etree.parse(self._file)
        except etree.XMLSyntaxError, e:
            raise Exception(
                '[XMLObject.validate] Cannot validate xml: ' + str(e)) 
        
        return xmlschema.validate(xml_doc)

