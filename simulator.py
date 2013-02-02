"""Simulator Thread

"""
import threading
from time import sleep

PAUSE = 0
RUN = 1

class Simulator(threading.Thread):

    def __init__(self, targetwin, id):
        super(Simulator, self).__init__()
        
        #Attributes
        self.id = id
        self.targetwin = targetwin
        self.stop = False
        self.state = PAUSE

    def run(self):
        print 'starting simulator thread'
        while not self.stop:
            if self.state == RUN:
                #Test Mutex and post event
                pass    
            
            sleep(0.1) # 100 milliseconds


    # Stops the thread
    def Stop(self):
        print 'stopping simulator thread'
        self.stop = True

    def startSimulation(self):
        self.state = RUN

    def pauseSimulation(self):
        self.state = PAUSE

    def resetSimulation(self):
        pass

        
#end class Simulator
