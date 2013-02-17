from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSlot, pyqtSignal, Qt, QObject, QEvent
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
            raise ValueError(
                "Invalid tree leaf class {}".format(
                    parameters.__class__.__name__))
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
            elif isinstance(v,int):
                self.leafs.append(Entry(key,float(v)))
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
    apply_request = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')
    
    def __init__(self, parent, window_id, parameters):
        """Construct a new dockwindow following the parameters dict.
        """
        self.id_ = window_id
        
        QtGui.QWidget.__init__(self, parent)

        verticalLayout = QtGui.QVBoxLayout(self)
        verticalLayout.setContentsMargins(10,10,10,10)
        verticalLayout.setSpacing(10)
        
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
        
        #verticalLayout.addStretch()
        
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Maximum)
        
        
    def set_parameters(self,parameters):
        try:
            self.contents.set_parameters(parameters)
        except ValueError as e:
            print "Invalid parameters: {}".format(e)
    
    @pyqtSlot()
    def apply_click(self):
        p = self.contents.get_struct()
        self.apply_request.emit(self.id_,p)
    
    @pyqtSlot()
    def save_click(self):
        pass
    
    @pyqtSlot()
    def load_click(self):
        pass

class ParamDock(QtGui.QDockWidget):
    title_click = pyqtSignal()

    def __init__(self, parent, window_id, window_name, window_color, parameters):
        """Construct a new dockwindow following the parameters dict.
        """
        QtGui.QDockWidget.__init__(self, window_name, parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.__panel = QtGui.QWidget(self)
        self.__panel.hide()
        self.__panel.setFixedHeight(1)

        self.__click = False

        self._widget = None
        self.reset(window_id, window_color, parameters)

    def set_color(self, window_color):
        self.setStyleSheet(
        """ QDockWidget {{
                border: 1px solid #{color:06x};
                }}
           
            QDockWidget::title {{
                background: #{color:06x};
                text-align: left;
                padding-left: 5px;
                }}""".format(color=window_color))

    def reset(self,window_id, window_color, parameters):
        self.set_color(window_color)    
        if self._widget is not None:
            self._widget.hide()
            self._widget.deleteLater()
        self._widget = ParamWidget(self, window_id, parameters)
        if not self.is_collapsed():
            self.setWidget(self._widget)

    def event(self, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.y() < self.widget().geometry().top():
                self.__click = True
        elif event.type() == QEvent.MouseMove:
            self.__click = False
        elif event.type() == QEvent.MouseButtonRelease:
            if self.__click:
                self.title_click.emit()
                self.__click = False
        return QtGui.QDockWidget.event(self,event)

    def collapse(self, bool_collapse = True):
        self.expand(not bool_collapse)
    
    def expand(self, bool_expand = True):
        if bool_expand:
            self.setWidget(self._widget)
            self._widget.show()
            self.__panel.hide()
        else:
            self.setWidget(self.__panel)
            self.__panel.show()
            self._widget.hide()
    
    def is_collapsed(self):
        return self.widget() == self.__panel
        
class DockManager(QObject):
    apply_request = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')
    
    """Provides a dock for the Qt Simulator Widget to controll PID elements"""
    def __init__(self, parent):
        QObject.__init__(self, parent)
        self.docks = {}
        self.clear()

    def dock_to_name(self,dock):
        for k, vdock in self.docks.items():
            if vdock == dock:
                return k
        return "Unknown dock"

    def remove_by_name(self, name):
        if name in self.docks:
            old_dock = self.docks.pop(name)
            old_dock.destroyed[QObject].disconnect()
            old_dock.dockLocationChanged.disconnect()
            old_dock.topLevelChanged.disconnect()
            old_dock.title_click.disconnect()
            old_dock.apply_request.disconnect()
            old_dock.deleteLater()
            if old_dock in self.docks_left:
                self.docks_left.remove(old_dock)
                return 'left'
            elif old_dock in self.docks_right:
                self.docks_right.remove(old_dock)
                return 'right'
            return 'float'
        return 'none'

    def remove_by_obj(self, dock):
        #self.remove_dock(dock)
        dock.deleteLater()
    
    def clear(self):
        for k, dock in self.docks.items():
            dock.deleteLater()
        self.docks_left = []
        self.active_left = None
        self.docks_right = []
        self.active_right = None
        self.docks = {}
    
    def add_dock(self, robot_id, name, parameters, side):
        if name in self.docks:
            self.docks[name].reset(robot_id, robot_id.get_color(), parameters)
            return
        
        dock = ParamDock(self.parent(),
                         robot_id, name, robot_id.get_color(),
                         parameters)
        self.docks[name] = dock
        
        if side == 'left':
            dlist = self.docks_left
            self.parent().addDockWidget(Qt.LeftDockWidgetArea, dock)
            if not dlist:
                self.active_left = dock
        elif side == 'right':
            dlist = self.docks_right
            self.parent().addDockWidget(Qt.RightDockWidgetArea, dock)
            if not dlist:
                self.active_right = dock
        
        dlist.append(dock)
        dock.expand(len(dlist) == 1)

        dock.destroyed[QObject].connect(self.remove_dock)
        dock.dockLocationChanged.connect(self.dock_location_changed)
        dock.topLevelChanged.connect(self.dock_level_changed)
        dock.title_click.connect(self.dock_user_expanded)
        dock._widget.apply_request.connect(self.apply_request)
           
    def add_dock_left(self, robot_id, name, parameters):
        self.add_dock(robot_id, name, parameters, 'left')
        
    def add_dock_right(self, robot_id, name, parameters):
        self.add_dock(robot_id, name, parameters, 'right')
        
    @pyqtSlot(QObject)
    def remove_dock(self, dock):
        if dock in self.docks_left:
            self.docks_left.remove(old_dock)
        elif dock in self.docks_right:
            self.docks_right.remove(old_dock)
        for k,v in self.docks.items():
            if v == dock:
                del self.docks[k]
                break

    @pyqtSlot(bool)
    def dock_level_changed(self, tl):
        dock = self.sender()
        if tl:
            dock.expand()
            
            if dock in self.docks_left:
                self.docks_left.remove(dock)
            elif dock in self.docks_right:
                self.docks_right.remove(dock)
            else:
                raise ValueError("Dock not found")
            
            if self.active_left == dock: # show some other widget
                if self.docks_left:
                    self.active_left = self.docks_left[0]
                    self.active_left.expand()
                else:
                    self.active_left = None
            elif self.active_right == dock: # show some other widget
                if self.docks_right:
                    self.active_right = self.docks_right[0]
                    self.active_right.expand()
                else:
                    self.active_right = None
        # otherwise already shown. Wait for location change

    @pyqtSlot(Qt.DockWidgetArea)
    def dock_location_changed(self,loc):
        dock = self.sender()
        if loc == Qt.LeftDockWidgetArea:
            self.docks_left.append(dock)
            if self.active_left is not None:
                self.active_left.expand(False)
            self.active_left = dock
        elif loc == Qt.RightDockWidgetArea:
            self.docks_right.append(dock)
            if self.active_right is not None:
                self.active_right.expand(False)
            self.active_right = dock
        else:
            raise ValueError("Undefined dock location")
    
    @pyqtSlot()
    def dock_user_expanded(self):
        dock = self.sender()
        if dock.is_collapsed():
            if dock in self.docks_left:
                self.active_left.collapse()
                dock.expand()
                self.active_left = dock
            elif dock in self.docks_right:
                self.active_right.collapse()
                dock.expand()
                self.active_right = dock
            
