import unittest
from xmlwriter import XMLWriter
from xmlreader import XMLReader
from os import unlink

class TestXMLWriter(unittest.TestCase):

    # write parameters
    def test_write_parameters_legal(self):
        parameters = {'pid': {
                             'goal': {'y': 10.0, 'x': 11.0}, 
                             'angle': {'theta': 0.7854}, 
                             'velocity': {'v': 0.1}, 
                             ('gains', 'soft'): {'ki': 0.1, 'kp': 5.0, 'kd': 0.01}, 
                             ('gains', 'hard'): {'ki': 0.1, 'kp': 5.0, 'kd': 0.01}
                             }
                     }

        file_ = "tmp_removeme.xml"
        try:
            XMLWriter(file_, "parameters", parameters).write()
            result = XMLReader(file_, "parameters").read()
            assert result == parameters
        finally:
            # If the file was created (it exists), delete it
            try:
                with open(file_) as f:
                    f.close()
                    unlink(file_)
            except IOError:
                pass
 
    def test_write_parameters_bad_parameter_string_value(self):
        parameters = {'pid': {
                             'goal': {'y': 'banks', 'x': 11.0}, 
                             'angle': {'theta': 0.7854}, 
                             'velocity': {'v': 0.1}, 
                             ('gains', 'soft'): {'ki': 0.1, 'kp': 5.0, 'kd': 0.01}, 
                             ('gains', 'hard'): {'ki': 0.1, 'kp': 5.0, 'kd': 0.01}
                             }
                     }

        writer = XMLWriter("bad_parameter.xml", "parameters", parameters)
        self.assertRaises(Exception, writer.write)
    
    def test_write_parameters_bad_parameter_float_key(self):
        parameters = {'pid': {
                             'goal': {'13.0': '10.0', 'x': 11.0}, 
                             'angle': {'theta': 0.7854}, 
                             'velocity': {'v': 0.1}, 
                             ('gains', 'soft'): {'ki': 0.1, 'kp': 5.0, 'kd': 0.01}, 
                             ('gains', 'hard'): {'ki': 0.1, 'kp': 5.0, 'kd': 0.01}
                             }
                     }

        writer = XMLWriter("bad_parameter.xml", "parameters", parameters)
        self.assertRaises(Exception, writer.write)

    def test_write_parameters_root_not_dict(self):
        parameters = ('shaun', 'juliet')
        writer = XMLWriter("root_not_dict.xml", "parameters", parameters)
        self.assertRaises(Exception, writer.write)

if __name__ == "__main__":
    unittest.main()
