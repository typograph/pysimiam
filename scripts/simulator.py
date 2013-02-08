"""Simulator Thread

"""
import threading
from time import sleep

import khepera3
import pose
import simobject

PAUSE = 0
RUN = 1

#mEVT_VIEWER_EVENT = wx.NewEventType()
#EVT_VIEWER_EVENT = wx.PyEventBinder(mEVT_VIEWER_EVENT, 1)
## Custom Event class for simulator notifications
#class ViewerEvent(wx.PyCommandEvent):
#    def __init__(self, index=0, id=0):
#        """Constructor
#        @param index - int describing index of image
#        in buffer to draw to screen
#        """
#        evttype = mEVT_VIEWER_EVENT
#        wx.PyComman#dEvent.__init__(self, evttype, id)
#        self.index #= None
##
##    def setIndex(self, ind):
#        self.index = ind
#
#    def getIndex(self):
#        return self.index
## end class ViewerEvent

class Simulator(threading.Thread):

    def __init__(self, renderer, update_callback):
        """
        The viewer object supplies:
            a Renderer (viewer.renderer),
            a threading.Lock (viewer.lock) to lock painting
        and a threading.Event (viewer.event) to signal the end of painting
        """
        super(Simulator, self).__init__()

        #Attributes
        self._id = id
        #self._targetwin = targetwin
        self._stop = False
        self._state = PAUSE
        self._renderer = renderer

        #test code
        self._robot = khepera3.Khepera3(pose.Pose(200.0, 250.0, 0.0))
        self._robot.set_wheel_speeds(18,16)
        self._obstacles = [
            simobject.Polygon(pose.Pose(200,200,0),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000),
            simobject.Polygon(pose.Pose(300,100,0.1),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000),
            simobject.Polygon(pose.Pose(100,300,0.4),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000)
            ]
        #end test code

    def read_config(self, config):
        ''' Read in the objects from the XML configuration file '''

        print 'reading initial configuration'
        parser = XMLParser(config)
        world = parser.parse()
        self.robot = None
        self.obstacles = []
        for thing in world:
            thing_type = thing[0]
            if thing_type == 'robot':
                robot_type, robot_pose  = thing[1], thing[2] 
                if robot_type == 'khepera3.K3Supervisor':
                    self.robot = khepera3.Khepera3(pose.Pose(robot_pose))
                else:
                    raise Exception('[Simulator.__init__] Unknown robot type!')
            elif thing_type == 'obstacle':
                obstacle_pose, obstacle_coords = thing[1], thing[2]
                self.obstacles.append(
                    simobject.Polygon(pose.Pose(obstacle_pose),
                                      obstacle_coords,
                                      0xFF0000))
            else:
                raise Exception('[Simulator.__init__] Unknown object: ' 
                                + str(thing_type))
        
        if self.robot == None:
            raise Exception('[Simulator.__init__] No robot specified!')

    def run(self):
        print 'starting simulator thread'
        time_constant = 0.1
        while not self._stop:
            if self._state == RUN:
                pass

            sleep(time_constant) # 100 milliseconds

            self._robot.move_to(self._robot.pose_after(time_constant))

            # Post Redraw Event to UI
            if(self._targetwin):
                # Draw to buffer-bitmap
                self.draw()

                # Create UI Event
                event = ViewerEvent()
                wx.PostEvent(self._targetwin, event)

        time_constant = 0.1  # 100 milliseconds
        
        self.draw() # Draw at least once (Move to open afterwards)
        
        while not self.__stop:
           
            sleep(time_constant)

            if self.state != RUN:
                continue

            self._robot.move_to(self._robot.pose_after(time_constant))
            
            # Draw to buffer-bitmap
            self.draw()

    def draw(self):
       
        #Test code
        self._renderer.clear_screen()
        self._robot.draw(self._renderer)
        for obstacle in self._obstacles:
            obstacle.draw(self._renderer)
        self._renderer.set_screen_center_pose(self._robot.get_pose())
        self._renderer.clear_screen()
        for obstacle in self._obstacles:
            obstacle.draw(self._renderer)
        # Draw the robot and sensors after obstacles
        self._robot.draw(self._renderer)
        for s in self._robot.ir_sensors:
            s.draw(self._renderer)
        #end test code
        
        self.updateView()
        
    # Stops the thread
    def stop(self):
        print 'stopping simulator thread'
        self.__stop = True

    def start_simulation(self):
        self.state = RUN

    def pause_simulation(self):
        self.state = PAUSE

    def reset_simulation(self):
        pass


#end class Simulator
