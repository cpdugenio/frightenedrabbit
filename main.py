#!/usr/bin/env python

from __future__ import division
import sys
import ctypes
import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut
import numpy as np
from OpenGL.arrays import vbo
from configs import Global
from bufferHelper import BufferHelper
from transforms import Transform
from objects import Box

from PyQt4 import QtGui
from PyQt4.QtOpenGL import QGLWidget, QGLFormat

# use and edit configs.Global class for configs
GLOBAL = Global()

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
        glut.glutReshapeWindow(GLOBAL.WIDTH, GLOBAL.HEIGHT)
        glut.glutReshapeFunc(self.reshape)
        glut.glutDisplayFunc(self.display)
        glut.glutKeyboardFunc(self.keyboard)
        glut.glutTimerFunc(GLOBAL.REFRESH_TIMER, self.onTimer, GLOBAL.REFRESH_TIMER)

        self.buildProgram()

        self.reshape(GLOBAL.WIDTH, GLOBAL.HEIGHT)

        self.prepTransformation()

        # set object to be rendered
        self.render_obj = Box(self.program)

    def getProgram(self):
        """
        Basic getter class for (GPU-linked) program -- raises error if not initialized

        Notes
        -----
        Must call `self.buildProgram()` before using this function
        """
        if self.program:
            return self.program
        else:
            raise RuntimeWarning

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
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)

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

        projection_mat = Transform.perspective(GLOBAL.FOVY, width/height, GLOBAL.ZNEAR, GLOBAL.ZFAR)
        BufferHelper.sendUniformToShaders(self.getProgram(), 'projection', projection_mat, 'm4')

    def keyboard(self, key, x, y ):
        """
        GLUT keyboard listener
        """
        if key == '\033':    #ESC
            sys.exit( )

    def buildProgram(self):
        """
        This function builds, compiles, and links the GPU program and shaders

        Note
        ----
        This function initializes the `self.program` var
        """
        # create shaders and program from GPU
        program  = gl.glCreateProgram()
        vertex   = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        self.program = program

        # set and compile shaders
        gl.glShaderSource(vertex, GLOBAL.VERTEX_SHADER_CODE)
        gl.glShaderSource(fragment, GLOBAL.FRAGMENT_SHADER_CODE)
        gl.glCompileShader(vertex)
        gl.glCompileShader(fragment)

        # link shaders to  program
        gl.glAttachShader(program, vertex)
        gl.glAttachShader(program, fragment)

        # build and clean up
        gl.glLinkProgram(program)
        gl.glDetachShader(program, vertex)
        gl.glDetachShader(program, fragment)

        # Make program the default program
        gl.glUseProgram(program)

    def prepTransformation(self):
        """
        Setup of the view and model matrices are done
        """
        # setup view matrix
        view_mat = np.array(Transform.lookat(GLOBAL.EYE, GLOBAL.LOOKAT, GLOBAL.UP))
        BufferHelper.sendUniformToShaders(self.getProgram(), 'view', view_mat, 'm4')

        # setup model matrix
        model_mat = np.matrix(np.identity(4, dtype=np.float32))
        model_mat *= Transform.translate(0,0,-15)
        BufferHelper.sendUniformToShaders(self.getProgram(), 'model', model_mat, 'm4')

    def run(self):
        """
        May be used to call main draw loop (note that this function only calls a static function)
        """
        glut.glutMainLoop()


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
        
    def paintGL(self):
        """
        `paintGL` is called when drawing to the widget is necessary.
        Simply redirecting to `self.display`, the `GLUTDisplay` function for drawing.
        """
        self.display()

    def initializeGL(self):
        """
        Function is called after openGL is set up and ready -- can being to interact with GPU and shaders here.
        """
        self.buildProgram()

        self.prepTransformation()

        self.render_obj = Box(self.getProgram())        
        
    def resizeGL(self, width, height):
        """
        `resizeGL` is caled when widget is resized.
        Simply redirecting to `self.reshape`, the `GLUTDisplay` function for resizing.
        """
        self.reshape(width, height)

if __name__ == '__main__':
    
    if not GLOBAL.GLUT_DISPLAY:
        app = QtGui.QApplication(sys.argv)
        widget = QTDisplay()
        widget.resize(GLOBAL.WIDTH, GLOBAL.HEIGHT)
        widget.setWindowTitle("Frightened Qt Rabbit")
        widget.show()
        app.exec_()
    else:
        GLUTdisplay = GLUTDisplay()
        GLUTdisplay.run()
