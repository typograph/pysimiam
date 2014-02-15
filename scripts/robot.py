from simobject import SimObject

class Robot(SimObject):
    """The robot is a :class:`~simobject.SimObject` that implements moving,
       drawing, and information functions to interface with supervisor
       and the world environment.
       
       To implement a new type of robot, subclass :class:`Robot` and implement
       :meth:`~robot.Robot.get_info` and :meth:`~robot.Robot.get_external_sensors`.
       
       To make your robot move, implement :meth:`~robot.Robot.move`.
       
       To make you robot controllable, implement :meth:`~robot.Robot.set_inputs`.
       
       If your robot has sensors that can be drawn in the view, implement
       :meth:`~robot.Robot.draw_sensors`.
       """
       
    def move(self,dt):
        """Move the robot for a time interval `dt`."""
        pass
    
    def get_info(self):
        """Return the robot information structure, including sensor readings and
        shape information"""
        raise NotImplementedError("Robot.get_info")

    def set_inputs(self,inputs):
        """Set drive inputs in the format needed by this robot"""
        pass

    def draw_sensors(self,renderer):
        """Draw the sensors that this robot has"""
        pass

    def get_external_sensors(self):
        """Get the external sensors of the robot as a list.
           This function is used to update the sensor readings in proximity
           sensors."""
        raise NotImplementedError("Robot.get_external_sensors")

    def set_logqueue(self,logqueue):
        self.logqueue = logqueue
    
    def log(self, message):
        print("{}: {}".format(self.__class__.__name__,message))
        if self.logqueue is not None:
            self.logqueue.append((self,message))    
