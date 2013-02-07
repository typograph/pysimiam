import unittest
from simulator import Simulator

class TestSimulator(unittest.TestCase):

    def test_read_config_default_xml_settings(self):
        sim = Simulator(None, None, 0)
        sim.read_config('testfiles/settings.xml')
        
        assert sim.robot.getPose().getPoseList() ==  [1.0, 1.0, 1.5708]
        # TODO --- have Robot return type via getter, check here
        
        assert len(sim.obstacles) == 9
        
        assert sim.obstacles[0].getPose().getPoseList() == [1.0, 1.2, 0.0]
        assert sim.obstacles[0].getEnvelope() == \
            [(0.0,0.0), (0.3,0.0), (0.3,0.3), (0.0,0.3)]
        # TODO --- have Polygon return color, check here
        
        assert sim.obstacles[1].getPose().getPoseList() == [-0.5, 0.0, 0.7854]
        assert sim.obstacles[1].getEnvelope() == \
                    [(0.0, 0.0), (0.3, 0.0), (0.3, 0.3), (0.0, 0.3)]
        # TODO --- have Polygon return color, check here
                    
        assert sim.obstacles[2].getPose().getPoseList() == [0.65, 0.0, 0.7854]
        assert sim.obstacles[2].getEnvelope() == \
                    [(0.0, 0.0), (0.3, 0.0), (0.3, 0.3), (0.0, 0.3)]
        # TODO --- have Polygon return color, check here

        assert sim.obstacles[3].getPose().getPoseList() == [0.2, 0.8, 0.0]
        assert sim.obstacles[3].getEnvelope() == \
                    [(0.0, 0.0), (0.3, 0.0), (0.3, 0.3), (0.0, 0.3)]
        # TODO --- have Polygon return color, check here

        assert sim.obstacles[4].getPose().getPoseList() == [-1.0, -1.0, 0.0]
        assert sim.obstacles[4].getEnvelope() == \
                    [(0.0, 0.0), (1.5, 0.0), (1.5, 0.3), (0.0, 0.3)]
        # TODO --- have Polygon return color, check here

        assert sim.obstacles[5].getPose().getPoseList() == [-1.6, -1.5, 0.0]
        assert sim.obstacles[5].getEnvelope() == \
                    [(0.0, 0.0), (3.0, 0.0), (3.0, 0.1), (0.0, 0.1)]
        # TODO --- have Polygon return color, check here

        assert sim.obstacles[6].getPose().getPoseList() == [-1.5, -1.4, 1.5708]
        assert sim.obstacles[6].getEnvelope() == \
                    [(0.0, 0.0), (3.0, 0.0), (3.0, 0.1), (0.0, 0.1)]
        # TODO --- have Polygon return color, check here

        assert sim.obstacles[7].getPose().getPoseList() == [1.5, -1.5, 1.5708]
        assert sim.obstacles[7].getEnvelope() == \
                    [(0.0, 0.0), (3.0, 0.0), (3.0, 0.1), (0.0, 0.1)]
        # TODO --- have Polygon return color, check here

        assert sim.obstacles[8].getPose().getPoseList() == [-1.5, 1.5, 0.0]
        assert sim.obstacles[8].getEnvelope() == \
                    [(0.0, 0.0), (3.0, 0.0), (3.0, 0.1), (0.0, 0.1)]
        # TODO --- have Polygon return color, check here

if __name__ == "__main__":
    unittest.main()