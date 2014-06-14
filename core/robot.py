#
# (c) PySimiam Team
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#

"""The robot base classes of PySimiam."""

from .simobject import SimObject

class Robot(SimObject):
    """The robot is a :class:`~simobject.SimObject` that implements drawing
    and information functions to interface with supervisor.
    
    This class is not intended to be subclassed in user code. Use one
    of the provided subclasses instead: :class:`~robot.SimBot` for emulated 
    robots or :class:`~robot.RealBot` for physical robots.
    """
    
    def get_info(self):
        """Return the robot information structure, including sensor 
        readings and shape information.
        """
        raise NotImplementedError("Robot.get_info")

    info = property(lambda self: self.get_info(),
                    doc="The information about the physical configuration of this robot")

    def get_state(self):
        """Return the robot information structure, including sensor 
           readings and shape information.
        """
        raise NotImplementedError("Robot.get_state")

    state = property(lambda self: self.get_state(),
                     doc="The information about the current state of this robot")

    def set_inputs(self,inputs):
        """Set drive inputs in the format needed by this robot"""
        pass

    inputs = property(fset=lambda self, i: self.set_inputs(i),
                      doc="The inputs to robot controls")

    def draw_sensors(self,renderer):
        """Draw the sensors that this robot has"""
        pass

class SimBot(Robot):
    """The robot defined by this class is a simulated robot, and implements
    its own motion in :meth:`~robot.SimBot.move`.
    
    To implement a new type of robot, subclass :class:`SimBot` and 
    implement :meth:`~robot.Robot.get_info` and 
    :meth:`~robot.SimBot.get_external_sensors`.
    
    To make your robot move, implement :meth:`~robot.SimBot.move`.
    
    To make you robot controllable, implement :meth:`~robot.Robot.set_inputs`.
    
    If your robot has sensors that can be drawn in the view, implement
    :meth:`~robot.Robot.draw_sensors`.
    """
    
    def move(self,dt):
        """Move the robot for a time interval `dt`."""
        pass
    
    def get_external_sensors(self):
        """Get the external sensors of the robot as a list.
        This function is used to update the sensor readings in proximity
        sensors."""
        raise NotImplementedError("SimBot.get_external_sensors")    

class RealBot(Robot):
    """This type of robots implements communication with a real-world 
    robot. 

    Although this is a SimObject, it doesn't move by itself.
    Use :meth:`~simobject.SimObject.set_pose()` to move the robot.
    """
        
    def update_external_state(self):
        """Initiate communication with the real robot and get state info 
        back.
        """
        raise NotImplementedError("RealBot.update_external_state")
    
    def pause(self):
        """Stops the robot, saving the state"""
        raise NotImplementedError("RealBot.pause")
        
    def resume(self):
        """Restarts the robot from the saved state"""
        raise NotImplementedError("RealBot.resume")
    
