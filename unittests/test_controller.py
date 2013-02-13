import unittest
from controller import Controller

class TestController(unittest.TestCase):
    def test_pid_controller_legal(self):
        pid_controller = Controller()
        pid_parameters = pid_controller.read_config(
                             "../testfiles/parameters.xml")
        
        assert pid_parameters == {'pid': {
                                         'goal': {'y': 10.0, 'x': 11.0},
                                         'angle': {'theta': 0.7854},
                                         'velocity': {'v': 0.1},
                                         ('gains', 'soft'): {'ki': 0.1, 'kp': 5.0, 'kd': 0.01},
                                         ('gains', 'hard'): {'ki': 0.1, 'kp': 5.0, 'kd': 0.01}
                                         }
                                 }

if __name__ == "__main__":
    unittest.main()
