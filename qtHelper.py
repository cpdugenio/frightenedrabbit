#!/usr/bin/env python

import os

from PyQt4.QtCore import Qt, QTimer
from PyQt4 import QtGui
from PyQt4.QtOpenGL import QGLWidget, QGLFormat

from configs import Global


class QTMorphWidget(QtGui.QWidget):
    def __init__(self):
        super(QTMorphWidget, self).__init__()
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)
        self.setLayout(self.grid)
        self.rows = 0

    def clearWidget(self):
        # reparent trick to remove grid
        QtGui.QWidget().setLayout(self.grid)
        
        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        self.grid = grid

    def replaceWidget(self, replacementWidget):
        self.clearWidget()
        self.grid.addWidget(replacementWidget, 1, 1)


class QTMainWindow(QtGui.QWidget):
    """
    Wrapper widget class (has a grid to house other widgets)
    """
    def __init__(self, OpenGLWidget, SideBarWidget):
        super(QTMainWindow, self).__init__()

        self.GLWidget = OpenGLWidget
        self.sidebar = SideBarWidget

        # scale slider
        self.scaleSlider = QtGui.QSlider(Qt.Horizontal, self)
        self.scaleSlider.setRange(1,100)
        self.scaleSlider.setSliderPosition(10)
        self.scaleSlider.valueChanged[int].connect(self.GLWidget.changeScale)

        # reset rotation button
        self.resetRotationBtn = QtGui.QPushButton("Reset Rotation")
        self.resetRotationBtn.clicked.connect(self.GLWidget.resetRotation)

        self.initUI()

    def initUI(self):
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.GLWidget, 1, 1, 14, 14)
        grid.addWidget(self.scaleSlider, 15, 2, 1, 10)
        grid.addWidget(self.resetRotationBtn, 15, 12, 1, 3, alignment=Qt.AlignCenter)
        grid.addWidget(QtGui.QLabel('Scale'), 15, 1, 1, 1, alignment=Qt.AlignCenter)
        grid.addWidget(self.sidebar, 1, 15, 15, 5)

        # connect reset with everything
        self.sidebar.models_combo.activated[str].connect(self.resetUI)
        
        self.setLayout(grid) 
        
        self.setGeometry(0,0,Global.WIDTH,Global.HEIGHT)


    def resetUI(self, text = 'Box'):
        self.GLWidget.resetRotation()
        self.scaleSlider.setSliderPosition(10)
        self.sidebar.render_group_default.setChecked(True)

        if self.sidebar.color_checkbox.checkState() == Qt.Checked:
            if not Global.COLOR_DEFAULT:
                self.sidebar.color_checkbox.setCheckState(Qt.Unchecked)
        else:
            if Global.COLOR_DEFAULT:
                self.sidebar.color_checkbox.setCheckState(Qt.Checked)

        if self.sidebar.wireframe_checkbox.checkState() == Qt.Checked:
            if not Global.WIREFRAME_DEFAULT:
                self.sidebar.wireframe_checkbox.setCheckState(Qt.Unchecked)
        else:
            if Global.WIREFRAME_DEFAULT:
                self.sidebar.wireframe_checkbox.setCheckState(Qt.Checked)

        self.GLWidget.setModel(text)

        self.sidebar.replaceWidget(self.GLWidget.render_obj.getWidget())


class QTSideBar(QtGui.QWidget):
    """
    Sidebar UI class
    """
    def __init__(self, glwidget):
        super(QTSideBar, self).__init__()

        self.glwidget = glwidget

        self.initUI()

    def replaceWidget(self, newWidget):
        self.morphWidget.replaceWidget(newWidget)

    def initUI(self):

        # Setup Grid
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        self.grid = grid

        ##############################
        # Create and link gui objects
        ##############################

        # DROPDOWN
        self.models_combo = QtGui.QComboBox()
        self.models_label = QtGui.QLabel('Render Model: ')
        self.models_combo.addItem("Box")
        self.models_combo.addItem("UVSphere")
#        self.models_combo.addItem("UVMobius")
#        self.models_combo.addItem("UVKleinBottle")
        self.models_combo.addItem("UVTorus")
        for model in os.listdir(Global.MODELS_LOC):
            self.models_combo.addItem(Global.MODELS_LOC + model)

        # WIREFRAME
        self.wireframe_checkbox = QtGui.QCheckBox()
        self.wireframe_label = QtGui.QLabel('Toggle Wireframe')

        # COLOR
        self.color_checkbox = QtGui.QCheckBox()
        self.color_label = QtGui.QLabel('Toggle Color')

        if Global.COLOR_DEFAULT:
            self.color_checkbox.setCheckState(Qt.Checked)
        if Global.WIREFRAME_DEFAULT:
            self.wireframe_checkbox.setCheckState(Qt.Checked)

        self.color_checkbox.stateChanged[int].connect(self.glwidget.toggleColor)
        self.wireframe_checkbox.stateChanged[int].connect(self.glwidget.toggleWireframe)

        # create group box for render types
        self.render_group = QtGui.QGroupBox()
        vbox = QtGui.QVBoxLayout()
        render_buttons = [
            (QtGui.QRadioButton('Normals Shading'), self.glwidget.setNormalsShading),
            (QtGui.QRadioButton('Z-Buffer Shading'), self.glwidget.setZBufferShading),
        ]
        if len(render_buttons) > 0:
            render_buttons[0][0].setChecked(True)
            self.render_group_default = render_buttons[0][0]
        for button, event in render_buttons:
            vbox.addWidget(button)
            button.toggled[bool].connect(event)
        self.render_group.setLayout(vbox)

        # create morph widget for object specific qt attributes
        self.morphWidget = QTMorphWidget()

        ##################
        # Add gui to grid
        ##################
        grid.addWidget(self.models_label, 1, 1)
        grid.addWidget(self.models_combo, 1, 2, alignment=Qt.AlignCenter)
        
        grid.addWidget(self.wireframe_label, 2, 1)
        grid.addWidget(self.wireframe_checkbox, 2, 2, alignment=Qt.AlignCenter)

        grid.addWidget(self.color_label, 3, 1)
        grid.addWidget(self.color_checkbox, 3, 2, alignment=Qt.AlignCenter)

        grid.addWidget(self.render_group, 4, 1, len(render_buttons), 2)

        grid.addWidget(self.morphWidget, 4+len(render_buttons), 1, 7, 2)




        # Finalize
        self.setLayout(grid)





class QtHelper(object):

    QtMainWindow = None
    QtOpenGlWidget = None
    QtSideWidget = None

    @classmethod
    def getMainWindow(cls):
        if cls.QtMainWindow == None:
            raise ReferenceError
        else:
            return cls.QtMainWindow

    @classmethod
    def getOpenGLWidget(cls):
        if cls.QtOpenGlWidget == None:
            raise ReferenceError
        else:
            return cls.QtOpenGlWidget

    @classmethod
    def getSideWidget(cls):
        if cls.QtSideWidget == None:
            raise ReferenceError
        else:
            return cls.QtSideWidget

    @classmethod
    def createAllWindows(cls, QtOpenGlWidget, name = "Frightened Qt Rabbit"):
        cls.QtOpenGlWidget = QtOpenGlWidget
        cls.QtSideWidget = QTSideBar(QtOpenGlWidget)
        cls.QtMainWindow = QTMainWindow(QtOpenGlWidget, cls.QtSideWidget)
        cls.QtMainWindow.setWindowTitle(name)
        return cls.QtMainWindow

    
