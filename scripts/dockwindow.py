from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSlot
from helpers import Struct

# Constructing UI from parameters:
# 
# template:
# The template is a tree. Each node of the tree is either a dictionary
# or a floating-point number. The root is always a dictionary.
# The keys of the dictionary are either strings or string tuples.
# The values of the dictionary are tree nodes.
#
# UI:
# Each value node is a spinbox. The key from the parent (either second
# entry in key, or the capitalized key) is the label in front of the box.
# A dictionary node which contains dictionary nodes is a groupbox,
# if it has at least one of such nodes inside

class Entry():
    def __init__(self,label_key,value):
        if isinstance(label_key,str):
            self.field = label_key
            self.label = label_key.capitalize()
        elif isinstance(label_key,tuple):
            self.field = label_key[0]
            self.label = label_key[1]
            if len(label_key) > 2:
                raise ValueError("Too many entries in key")            
        else:
            raise ValueError("Invalid tree key")
        self.value = value
    
    def create_widgets(self,parent,layout):
        """Create a label and a spinbox in layout"""
        self.control = QtGui.QDoubleSpinBox(parent)
        self.control.setMinimum(-1000.0)
        self.control.setMaximum(1000.0)
        self.control.setValue(self.value)
        layout.addRow(self.label,self.control)
    
    def fill_struct(self,p):
        self.value = self.control.value()
        p.__dict__[self.field] = self.value
        
    #def set_parameters(self,p):
        #pass
    
class Group():
    def __init__(self,label_key,parameters):
        if not isinstance(parameters,dict):
            raise ValueError("Invalid tree format in parameters")
        self.field_id = None
        if isinstance(label_key,str):
            self.field = label_key
            self.label = label_key.capitalize()
        elif isinstance(label_key,tuple):
            self.field = label_key[0]
            self.label = label_key[1]
            if len(label_key) > 2:
                self.field_id = label_key[2]
        else:
            raise ValueError("Invalid tree key")
        self.leafs = []
        self.n_entries = 0
        self.n_groups = 0
        for key in parameters:
            v = parameters[key]
            if isinstance(v,float):
                self.leafs.append(Entry(key,v))
                self.n_entries += 1
            else:
                self.leafs.append(Group(key,v))
                self.n_groups += 1
        
    def create_widgets(self, parent, layout):
        self.box = QtGui.QGroupBox(self.label,parent)
        form_layout = QtGui.QFormLayout(self.box)
        for leaf in self.leafs:
            leaf.create_widgets(self.box,form_layout)
        layout.addRow(self.box)
    
    def fill_struct(self,params):
        p = Struct()
        for leaf in self.leafs:
            leaf.fill_struct(p)
        if self.field_id is None:
            params.__dict__[self.field] = p
        else:
            if self.field not in params.__dict__:
                params.__dict__[self.field] = {}
            params.__dict__[self.field][self.field_id] = p
        

class Contents(Group):
    def __init__(self,parameters):
        Group.__init__(self,'',parameters)
    
    def create_widgets(self, parent, layout):
        form_layout = QtGui.QFormLayout()
        for leaf in self.leafs:
            leaf.create_widgets(parent,form_layout)
        layout.addLayout(form_layout)
    
    def fill_struct(self):
        """This method should not be called on this class"""
        raise NotImplementedError("Contents.fill_struct")
    
    def get_struct(self):
        p = Struct()
        for leaf in self.leafs:
            leaf.fill_struct(p)
        return p

class ParamWidget(QtGui.QWidget):
    def __init__(self, window_id, parameters, callback):
        """Construct a new dockwindow following the parameters dict.
        """
        self.id_ = window_id
        self.apply_callback = callback
        
        QtGui.QWidget.__init__(self)
        
        verticalLayout = QtGui.QVBoxLayout(self)
        
        # Big Label
        #robot_label = QtGui.QLabel(window_name,self)
        #font = QtGui.QFont(self.font())
        #font.setPointSize(13)
        #robot_label.setFont(font)
        #robot_label.setFrameShape(QtGui.QFrame.Panel)
        #robot_label.setFrameShadow(QtGui.QFrame.Sunken)
        #robot_label.setAlignment(QtCore.Qt.AlignCenter)
        #verticalLayout.addWidget(robot_label)
        
        # Contents
        self.contents = Contents(parameters)
        self.contents.create_widgets(self,verticalLayout)
        
        # Three buttons
        horizontalLayout = QtGui.QHBoxLayout()

        self.apply_button = QtGui.QPushButton("Apply",self)
        self.apply_button.clicked.connect(self.apply_click)
        horizontalLayout.addWidget(self.apply_button)
        self.save_button = QtGui.QPushButton("Save",self)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_click)
        horizontalLayout.addWidget(self.save_button)
        self.load_button = QtGui.QPushButton("Load",self)
        self.load_button.setEnabled(False)
        self.load_button.clicked.connect(self.load_click)
        horizontalLayout.addWidget(self.load_button)

        verticalLayout.addLayout(horizontalLayout)
        
        verticalLayout.addStretch()
        
        
    def set_parameters(self,parameters):
        try:
            self.contents.set_parameters(parameters)
        except ValueError as e:
            print "Invalid parameters: {}".format(e)
    
    @pyqtSlot()
    def apply_click(self):
        p = self.contents.get_struct()
        #print p
        self.apply_callback(self.id_,p)
        pass
    
    @pyqtSlot()
    def save_click(self):
        pass

    @pyqtSlot()
    def load_click(self):
        pass

class ParamDock(QtGui.QDockWidget):
    def __init__(self, parent, window_id, window_name, parameters, callback):
        """Construct a new dockwindow following the parameters dict.
        """
        QtGui.QDockWidget.__init__(self, window_name, parent)
        self.setWidget(ParamWidget(window_id, parameters, callback))
    