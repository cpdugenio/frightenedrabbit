#!/usr/bin/env python

from __future__ import division
import os
import sys
import ctypes
import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut
import numpy as np
from OpenGL.arrays import vbo

from configs import Global
from shaderHelper import ShaderHelper
from bufferHelper import BufferHelper
from transforms import Transform

from objects import Box, Obj, UVObject, UVSphere, UVMobius, UVTorus, UVKlein

from PyQt4.QtCore import Qt, QTimer
from PyQt4 import QtGui
from PyQt4.QtOpenGL import QGLWidget, QGLFormat


default_obj = Box

class GLUTDisplay(object):
    """
    GLUT display class handling GLUT window display, render, and GL/GLUT flags

    Notes
    -----
    Configs in this class are linked to the config.Global class
    """

    def __init__(self):
        """
        Basic GLUT init and glut function definition.

        Notes
        -----
        `self.render_obj` is initialized here, which is then being used and drawn in `self.display`
        """
        
        glut.glutInit()
        glut.glutInitDisplayMode(glut.GLUT_RGBA | glut.GLUT_DOUBLE | glut.GLUT_DEPTH | glut.GLUT_MULTISAMPLE)
        glut.glutCreateWindow('Frightened Glut Rabbit')
        glut.glutReshapeWindow(Global.WIDTH, Global.HEIGHT)
        glut.glutReshapeFunc(self.reshape)
        glut.glutDisplayFunc(self.display)
        glut.glutKeyboardFunc(self.keyboard)
        glut.glutMouseFunc(self.glutMousePressEvent)
        glut.glutMotionFunc(self.glutMouseMoveEvent)
        glut.glutTimerFunc(Global.REFRESH_TIMER, self.onTimer, Global.REFRESH_TIMER)

        self.buildProgram()

        self.reshape(Global.WIDTH, Global.HEIGHT)

        # set object to be rendered
        self.render_obj = default_obj()

    def glutMouseMoveEvent(self, x, y):
        self.rotationMatrix *= Transform.yrotate((self.xorigpos - x) * -0.01)
        self.rotationMatrix *= Transform.xrotate((self.yorigpos - y) * -0.01)

        self.xorigpos, self.yorigpos = x, y

    def glutMousePressEvent(self, button, state, x, y):
        self.xorigpos, self.yorigpos = x, y

    @classmethod
    def onTimer(cls, t):
        """
        GLUT function to refresh the screen at given interval

        Parameters
        ----------
        t : int
            interval in milliseconds
        """
        glut.glutTimerFunc(t, cls.onTimer, t)
        glut.glutPostRedisplay()

    def display(self):
        """
        GLUT function to display and draw scene

        Notes
        -----
        `self.render_obj` is being drawn here, initialized in `self.__init__()`
        """

        gl.glClearColor(*Global.CLEAR_COLOR)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)

        self.prepTransformation()
        self.render_obj.draw()

        gl.glFlush()
        glut.glutSwapBuffers()

    def reshape(self, width, height):
        """
        GLUT reshape function with the addition of defining the projection matrix

        Parameters
        ----------
        width : int
        height : int

        Note
        ----
        You may need to call this class if is not automatically called by the GLUT function:
        If it is not called, the projection frustum is not created.
        """
        gl.glViewport(0, 0, width, height)

        self.projection_mat = Transform.perspective(Global.FOVY, width/height, Global.ZNEAR, Global.ZFAR)

    def keyboard(self, key, x, y ):
        """
        GLUT keyboard listener
        """
        if key == '\033':    #ESC
            sys.exit( )

    def buildProgram(self):
        """
        This function builds, compiles, and links the GPU program and shaders
        """
        

        # setup for mouseclick
        self.xrotate = 0
        self.yrotate = 0
        self.zrotate = 0 #not being used
        self.xorigpos = 0
        self.yorigpos = 0

        self.scale = 1.0

        self.rotationMatrix = np.matrix(np.identity(4, dtype=np.float32))

    def prepTransformation(self):
        """
        Setup of the view and model matrices are done
        """
        BufferHelper.sendUniformToShaders('projection', self.projection_mat, 'm4')

        # setup view matrix
        view_mat = np.array(Transform.lookat(Global.EYE, Global.LOOKAT, Global.UP))
        BufferHelper.sendUniformToShaders('view', view_mat, 'm4')

        # setup model matrix
        model_mat = np.matrix(np.identity(4, dtype=np.float32))
        # note that because GLSL uses row major, need to do SRT (instead of TRS)

        # scale
        model_mat *= Transform.scale(self.scale, self.scale, self.scale)

        # rotations
        model_mat *= self.rotationMatrix

        # transform
        model_mat *= Transform.translate(0,0,-25)
        BufferHelper.sendUniformToShaders('model', model_mat, 'm4')

    def run(self):
        """
        May be used to call main draw loop (note that this function only calls a static function)
        """
        glut.glutMainLoop()

    ##################
    # Qt Event Calls #
    ##################

    def changeScale(self, value):
        self.scale = value * 0.1

    def resetRotation(self):
        self.rotationMatrix = np.matrix(np.identity(4, dtype=np.float32))

    def toggleWireframe(self):
        self.render_obj.toggleWireframe()

    def toggleColor(self):
        self.render_obj.toggleColor()

    def changeuvV(self, value):
        self.render_obj.refreshUV()
        Global.MAX_V = value

    def changeuvU(self, value):
        self.render_obj.refreshUV()
        Global.MAX_U = value

    def setModel(self, text):
        switch = {
            'Box' : Box,
            'Grid' : UVObject,
            'UVSphere' : UVSphere,
            'UVMobius' : UVMobius,
            'UVTorus' : UVTorus,
            'UVKleinBottle' : UVKlein,
        }

        text = str(text)

        if text in switch.keys():
            self.render_obj = switch[text]()
        else:
            self.render_obj = Obj(open(text).read())

class QTDisplay(QGLWidget, GLUTDisplay):
    """
    PyQt4 OpenGL display class, re-using GLUTDisplay functions
    """
    def __init__(self, parent = None):
        """
        Basic init of widget class
        """
        super(QTDisplay, self).__init__(parent)

        # turn on multisampling
        format = self.format()
        format.setSampleBuffers(True)
        self.setFormat(format)

    def mouseMoveEvent(self, event):
        self.glutMouseMoveEvent(event.pos().x(), event.pos().y())

    def mousePressEvent(self, event):
        self.glutMousePressEvent(None, None, event.pos().x(), event.pos().y())

    def paintGL(self):
        """
        `paintGL` is called when drawing to the widget is necessary.
        Simply redirecting to `self.display`, the `GLUTDisplay` function for drawing.
        """
        self.display()
        self.swapBuffers()

    def initializeGL(self):
        """
        Function is called after openGL is set up and ready -- can being to interact with GPU and shaders here.
        """

        self.buildProgram()

        self.render_obj = default_obj()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.paintGL)
        self.timer.start(Global.REFRESH_TIMER)
        
    def resizeGL(self, width, height):
        """
        `resizeGL` is caled when widget is resized.
        Simply redirecting to `self.reshape`, the `GLUTDisplay` function for resizing.
        """
        self.reshape(width, height)


class QTMainWindow(QtGui.QWidget):
    """
    Wrapper widget class (has a grid to house other widgets)
    """
    def __init__(self):
        super(QTMainWindow, self).__init__()

        self.GLWidget = QTDisplay()
        self.sidebar = QTSideBar(self.GLWidget)

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
        
        self.setGeometry(0,0,1000,700)


    def resetUI(self, text = 'Box'):
        self.GLWidget.resetRotation()
        self.scaleSlider.setSliderPosition(10)

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




class QTSideBar(QtGui.QWidget):
    """
    Sidebar UI class
    """
    def __init__(self, glwidget):
        super(QTSideBar, self).__init__()

        self.glwidget = glwidget

        self.initUI()

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
        self.models_combo.addItem("Grid")
        self.models_combo.addItem("UVSphere")
        self.models_combo.addItem("UVMobius")
        self.models_combo.addItem("UVKleinBottle")
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

        # scale slider
        self.uv_v_slider = QtGui.QSlider(Qt.Horizontal, self)
        self.uv_v_label = QtGui.QLabel('V:')
        self.uv_v_slider.setRange(2,100)
        self.uv_v_slider.setSliderPosition(Global.MAX_U)
        self.uv_v_slider.valueChanged[int].connect(self.glwidget.changeuvV)

        self.uv_u_slider = QtGui.QSlider(Qt.Horizontal, self)
        self.uv_u_label = QtGui.QLabel('U:')
        self.uv_u_slider.setRange(2,100)
        self.uv_u_slider.setSliderPosition(Global.MAX_U)
        self.uv_u_slider.valueChanged[int].connect(self.glwidget.changeuvU)

        ##################
        # Add gui to grid
        ##################
        grid.addWidget(self.models_label, 1, 1)
        grid.addWidget(self.models_combo, 1, 2, alignment=Qt.AlignCenter)
        
        grid.addWidget(self.wireframe_label, 2, 1)
        grid.addWidget(self.wireframe_checkbox, 2, 2, alignment=Qt.AlignCenter)

        grid.addWidget(self.color_label, 3, 1)
        grid.addWidget(self.color_checkbox, 3, 2, alignment=Qt.AlignCenter)

        grid.addWidget(self.uv_u_label, 4, 1)
        grid.addWidget(self.uv_u_slider, 4, 2, alignment=Qt.AlignCenter)
        grid.addWidget(self.uv_v_label, 4, 3)
        grid.addWidget(self.uv_v_slider, 4, 4, alignment=Qt.AlignCenter)


        # Finalize
        self.setLayout(grid)


if __name__ == '__main__':
    if not Global.GLUT_DISPLAY:
        app = QtGui.QApplication(sys.argv)

        mainwindow = QTMainWindow()
        mainwindow.setWindowTitle("Frightened Qt Rabbit")
        mainwindow.show()

        app.exec_()
    else:
        GLUTdisplay = GLUTDisplay()
        GLUTdisplay.run()
