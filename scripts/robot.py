from simobject import SimObject

class Robot(SimObject):
    """The robot class inherits from the simobject and implements moving, drawing, and information functions to interface with supervisors and the world environment."""
    def move(self,dt):
        """Moves the robot with time dt"""
        raise NotImplementedError("Robot.move")
    
    def get_info(self):
        """Return the robot information structure, including sensor readings and
        shape information"""
        raise NotImplementedError("Robot.get_info")

    def set_inputs(self,inputs):
        """Set drive inputs in the format needed by this robot"""
        raise NotImplementedError("Robot.set_inputs")

    def draw_sensors(self,renderer):
        """Draw the sensors that this robot has"""
        pass

    def update_sensors(self):
        """Update sensor values"""
        pass
