"""PySimiam
Author: John Alexander
ChangeDate: 8 FEB 2013; 2300EST
Description: This is the Supervisor class for PySimiam.
"""

class Supervisor:
    def __init__(self, robot, cntrl_list, parameters):
        self.attach_robot(robot)
        self.controller_modules = {}
        self.controllers = {}
        for module_name in cntrl_list:
            # We expect a name in the form "file.Class"
            # to load a controller Class from file controllers/file.py
            try:
                filename, class_name = module_name.split(".")
            except ValueError:
                # either too many or too few dots
                # fallback to capitalization
                filename = module_name
                class_name = module_name.capitalize()
            try:
                module = __import__(filename)
                controller_class = module.__dict__[class_name]
                self.controller_modules[module_name] = (module, controller_class)
                self.controllers[filename] = controller_class(parameters)
            except ImportError:
                print "Module {} failed to load".format(filename)
            except KeyError:
                print "No class {} in module {}".format(class_name,filename)

        #self.build_dict()

    def attach_robot(self, robot):
        self.robot = robot
        self.pose_est = self.robot.get_pose #define the starting pose

    def set_current(self, cntrl):
        self.current = self.controllers[cntrl]

    def get_current(self):
        return self.current

    #def build_dict(self,cntrl_list):
        #for m, controller_class in self.:
            #class_name = getattr(self.controller_modules[controller],
                                 #capitalize(controller[0]) + controller[1:])
            #self.controllers[controller] = class_name()

    def execute(self, dt):
        self.eval_criteria() #User-defined algorithm
        output = self.current.execute(self,dt) #execute the current class
        self.apply_outputs(output)
        self.robot.move_to(self.robot.pose_after(dt))
        self.estimate_pose()

    def eval_criteria(self):
        """Evaluate the situation and select the right controller
        
        To be implemented in subclasses"""
        raise NotImplementedError('Supervisor.eval_criteria')
    
    def apply_outputs(self, outputs):
        """Apply controller outputs to the robot
        
        To be implemented in subclasses"""
        raise NotImplementedError('Supervisor.apply_outputs')
    
    def estimate_pose(self):
        """Update self.pose_est
        
        To be implemented in subclasses"""
        raise NotImplementedError('Supervisor.estimate_pose')
