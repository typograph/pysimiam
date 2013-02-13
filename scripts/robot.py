from simobject import SimObject

class Robot(SimObject):
    def move(self,dt):
        """Moves the robot for time dt"""
        raise NotImplementedError("Robot.move")
    
    def get_info(self):
        """Return the information about robot, including sensor readings and
        shape information"""
        raise NotImplementedError("Robot.get_info")

    def set_inputs(self,inputs):
        """Set drive inputs in the format needed by this robot"""
        raise NotImplementedError("Robot.set_inputs")

    def draw_sensors(self,renderer):
        """Draw the sensors that this robot has"""
        pass
    