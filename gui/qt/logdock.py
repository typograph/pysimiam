from PyQt4 import QtGui
from PyQt4.QtCore import Qt, pyqtSignal

class LogDock(QtGui.QDockWidget):
    closed = pyqtSignal(bool)
    def __init__(self, parent):
        """Construct a new dockwindow with the log """
        
        QtGui.QDockWidget.__init__(self, "Message log", parent)
        self.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)

        self.table = QtGui.QTableWidget(0,2,self)
        self.table.setHorizontalHeaderLabels(["Sender","Message"])

        self.table.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        hhdrs = self.table.horizontalHeader()       
        hhdrs.setResizeMode(0,QtGui.QHeaderView.ResizeToContents)
        hhdrs.setResizeMode(1,QtGui.QHeaderView.Stretch)

        self.setWidget(self.table)

    def append(self,message,name,color):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row,0,QtGui.QTableWidgetItem(name))
        self.table.setItem(row,1,QtGui.QTableWidgetItem(message))
        clr = QtGui.QTableWidgetItem(" ")
        self.table.setVerticalHeaderItem(row,clr)
        if color is not None:
            clr.setBackground(QtGui.QColor(color))

    def closeEvent(self,event):
        super(LogDock,self).closeEvent(event)
        if event.isAccepted():
            print('closed')
            self.closed.emit(True)