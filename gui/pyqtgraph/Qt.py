## Do all Qt imports from here to allow easier PyQt / PySide compatibility
import sys, re

## Automatically determine whether to use PyQt or PySide. 
## This is done by first checking to see whether one of the libraries
## is already imported. If not, then attempt to import PyQt4, then PySide.
if 'PyQt4' not in sys.modules:
    try:
        import PyQt4
    except ImportError:
        raise Exception("PyQtGraph couldn't import PyQt4.")

from PyQt4 import QtGui, QtCore
try:
    from PyQt4 import QtSvg
except ImportError:
    pass
try:
    from PyQt4 import QtOpenGL
except ImportError:
    pass

QtCore.Signal = QtCore.pyqtSignal
VERSION_INFO = 'PyQt4 ' + QtCore.PYQT_VERSION_STR + ' Qt ' + QtCore.QT_VERSION_STR


## Make sure we have Qt >= 4.7
versionReq = [4, 7]
QtVersion = QtCore.QT_VERSION_STR
m = re.match(r'(\d+)\.(\d+).*', QtVersion)
if m is not None and list(map(int, m.groups())) < versionReq:
    print(map(int, m.groups()))
    raise Exception('pyqtgraph requires Qt version >= %d.%d  (your version is %s)' % (versionReq[0], versionReq[1], QtVersion))

