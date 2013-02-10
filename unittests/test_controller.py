import unittest
from controller import Controller

class TestController(unittest.TestCase):
    def test_pid_controller(self):
        pid_controller = Controller()
        pid_parameters = pid_controller.read_config("../testfiles/parameters.xml")
        assert pid_parameters[0] == ('pid', 0.7854, 0.1, [5, 0.1, 0.01])
