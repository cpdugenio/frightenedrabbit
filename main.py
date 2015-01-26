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
from qtHelper import QtHelper

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

    def setNormalsShading(self, bool):
        self.render_obj.setNormalsShading(bool)

    def setZBufferShading(self, bool):
        self.render_obj.setZbufferShading(bool)

    def setModel(self, text):
        switch = {
            'Box' : Box,
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
        format.setSamples(128)
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

        self.parentWidget().resetUI()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.paintGL)
        self.timer.start(Global.REFRESH_TIMER)

    def resizeGL(self, width, height):
        """
        `resizeGL` is caled when widget is resized.
        Simply redirecting to `self.reshape`, the `GLUTDisplay` function for resizing.
        """
        self.reshape(width, height)

    


if __name__ == '__main__':
    if not Global.GLUT_DISPLAY:
        app = QtGui.QApplication(sys.argv)

        mainwindow = QtHelper.createAllWindows(QTDisplay())
        mainwindow.show()

        app.exec_()
    else:
        GLUTdisplay = GLUTDisplay()
        GLUTdisplay.run()
