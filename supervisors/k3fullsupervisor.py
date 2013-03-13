from khepera3 import K3Supervisor
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2
import numpy

class K3FullSupervisor(K3Supervisor):
    """K3Full supervisor creates four controllers: hold, gotogoal, avoidobstacles and blending."""
    def __init__(self, robot_pose, robot_info):
        """Creates an avoid-obstacle controller and go-to-goal controller"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        self.distmax = robot_info.ir_sensors.rmax + robot_info.wheels.base_length/2

        # Fill in some parameters
        self.ui_params.sensor_poses = robot_info.ir_sensors.poses[:]
        self.ui_params.ir_max = robot_info.ir_sensors.rmax
        self.ui_params.direction = 'left'
        self.ui_params.distance = self.distmax*0.85
        
        self.robot = robot_info
        self.process()
        
        #Add controllers ( go to goal is default)
        self.avoidobstacles = self.get_controller('AvoidObstacles', self.ui_params)
        self.gtg = self.get_controller('GoToGoal', self.ui_params)
        #self.blending = self.get_controller('blending.Blending', self.ui_params)
        self.wall = self.get_controller('FollowWall', self.ui_params)
        self.hold = self.get_controller('Hold', None)
        
        self.add_controller(self.hold,
                            (lambda: not self.at_goal(), self.gtg))
        self.add_controller(self.gtg,
                            (self.at_goal, self.hold),
                            (self.at_wall, self.wall))
        self.add_controller(self.wall,
                            (self.at_goal,self.hold),
                            (self.unsafe, self.avoidobstacles),
                            (self.wall_cleared, self.gtg))
        self.add_controller(self.avoidobstacles,
                            (self.at_goal, self.hold),
                            (self.safe, self.wall))

        self.current = self.gtg

    def set_parameters(self,params):
        K3Supervisor.set_parameters(self,params)
        self.gtg.set_parameters(self.ui_params)
        self.avoidobstacles.set_parameters(self.ui_params)
        self.wall.set_parameters(self.ui_params)

    def at_goal(self):
        return self.distance_from_goal < self.robot.wheels.base_length/2

    def is_at_wall(self):
        return self.distmin < self.distmax*0.8

    def at_wall(self):
        wall_close = self.is_at_wall()
        # Decide which direction to go
        if wall_close:
            
            dmin = self.distmax
            tmin = 0
            for i, d in enumerate(self.ui_params.sensor_distances):
                if d < dmin:
                    dmin = d
                    tmin = self.ui_params.sensor_poses[i].theta
            
            if tmin > 0:
                self.ui_params.direction = 'left'
            else:
                self.ui_params.direction = 'right'
                
            self.wall.set_parameters(self.ui_params)
            
            self.best_distance = self.distance_from_goal
            
        return wall_close

    def wall_cleared(self):
        print self.distmin/self.distmax
        
        if self.distance_from_goal >= self.best_distance:
            return False
        #self.best_distance = self.distance_from_goal

        print self.distance_from_goal, self.best_distance

        if self.is_at_wall():
            return False
            
        h_gtg = self.gtg.get_heading(self.ui_params)
        print "Far enough", numpy.dot(self.wall.to_wall_vector[:2],h_gtg[:2])
        return numpy.dot(self.wall.to_wall_vector[:2],h_gtg[:2]) < 0

    def unsafe(self):
        return self.distmin < self.distmax*0.5
        
    def safe(self):
        wall_far = self.distmin > self.distmax*0.6
        # Check which way to go
        if wall_far:
            self.at_wall()
        return wall_far

    def process(self):
        """Selects the best controller based on ir sensor readings
        Updates ui_params.pose and ui_params.ir_readings"""

        self.ui_params.pose = self.pose_est
        self.distance_from_goal = sqrt((self.pose_est.x - self.ui_params.goal.x)**2 + (self.pose_est.y - self.ui_params.goal.y)**2)
        
        self.ui_params.sensor_distances = self.get_ir_distances()
        vectors = \
            numpy.array(
                [numpy.dot(
                    p.get_transformation(),
                    numpy.array([d,0,1])
                    )
                     for d, p in zip(self.ui_params.sensor_distances, self.ui_params.sensor_poses) \
                     if abs(p.theta) < 2.4] )
        
        self.distmin = min((sqrt(a[0]**2 + a[1]**2) for a in vectors))

        return self.ui_params
    
    def draw(self, renderer):
        K3Supervisor.draw(self,renderer)

        # Make sure to have all headings:
        renderer.set_pose(self.pose_est)
        arrow_length = self.robot_size*5

        if self.current == self.gtg:
            # Draw arrow to goal
            renderer.set_pen(0x00FF00)
            renderer.draw_arrow(0,0,
                arrow_length*cos(self.gtg.heading_angle),
                arrow_length*sin(self.gtg.heading_angle))

        elif self.current == self.avoidobstacles:
            # Draw arrow away from obstacles
            renderer.set_pen(0xFF0000)
            renderer.draw_arrow(0,0,
                arrow_length*cos(self.avoidobstacles.heading_angle),
                arrow_length*sin(self.avoidobstacles.heading_angle))

        elif self.current == self.wall:

            # Draw vector to wall:
            renderer.set_pen(0x0000FF)
            renderer.draw_arrow(0,0,
                self.wall.to_wall_vector[0],
                self.wall.to_wall_vector[1])
            # Draw 
            renderer.set_pen(0xFF00FF)
            renderer.push_state()
            renderer.translate(self.wall.to_wall_vector[0], self.wall.to_wall_vector[1])
            renderer.draw_arrow(0,0,
                self.wall.along_wall_vector[0],
                self.wall.along_wall_vector[1])
            renderer.pop_state()

            # Draw heading (who knows, it might not be along_wall)
            renderer.set_pen(0xFF00FF)
            renderer.draw_arrow(0,0,
                arrow_length*cos(self.wall.heading_angle),
                arrow_length*sin(self.wall.heading_angle))

            # Important sensors
            renderer.set_pen(0)
            for v in self.wall.vectors:
                x,y,z = v
                
                renderer.push_state()
                renderer.translate(x,y)
                renderer.rotate(atan2(y,x))
            
                renderer.draw_line(0.01,0.01,-0.01,-0.01)
                renderer.draw_line(0.01,-0.01,-0.01,0.01)
                
                renderer.pop_state()