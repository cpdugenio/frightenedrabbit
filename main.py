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

class Display(object):

    def __init__(self):
        # GLUT init
        glut.glutInit()
        glut.glutInitDisplayMode(glut.GLUT_RGBA | glut.GLUT_DOUBLE | glut.GLUT_DEPTH | glut.GLUT_MULTISAMPLE)
        glut.glutCreateWindow('Frightened Rabbit')
        glut.glutReshapeWindow(GLOBAL.WIDTH, GLOBAL.HEIGHT)
        glut.glutReshapeFunc(self.reshape)
        glut.glutDisplayFunc(self.display)
        glut.glutKeyboardFunc(self.keyboard)
        glut.glutTimerFunc(10, self.on_timer, 10)

        self.build()

        self.reshape(GLOBAL.WIDTH, GLOBAL.HEIGHT)

        self.prep_matrices()

        self.render_obj = Box(self.program)

    @classmethod
    def on_timer(cls, t):
        glut.glutTimerFunc(t, cls.on_timer, t)
        glut.glutPostRedisplay()

    def display(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)

        self.render_obj.draw()

        gl.glFlush()
        glut.glutSwapBuffers()

    def reshape(self, width, height):
        gl.glViewport(0, 0, width, height)

        projection_mat = Transform.perspective(GLOBAL.FOVY, width/height, GLOBAL.ZNEAR, GLOBAL.ZFAR)
        BufferHelper.sendUniformToShaders(self.program, 'projection', projection_mat, 'm4')

    def keyboard(self, key, x, y ):
        if key == '\033':    #ESC
            sys.exit( )

    def build(self):
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

    def prep_matrices(self):
        # setup view matrix
        view_mat = np.array(Transform.lookat(GLOBAL.EYE, GLOBAL.LOOKAT, GLOBAL.UP))
        BufferHelper.sendUniformToShaders(self.program, 'view', view_mat, 'm4')

        # setup model matrix
        model_mat = np.matrix(np.identity(4, dtype=np.float32))
        model_mat *= Transform.translate(0,0,-15)
        BufferHelper.sendUniformToShaders(self.program, 'model', model_mat, 'm4')

    def run(self):
        glut.glutMainLoop()

class QTDisplay(QGLWidget, Display):
    def __init__(self, parent = None):
        super(QTDisplay, self).__init__(parent)
        format = self.format()
        format.setSamples(8)
        format.setSampleBuffers(True)
        self.setFormat(format)
        
    def paintGL(self):
        self.display()
        print 'displaying'

    def initializeGL(self):
        self.build()

        self.prep_matrices()

        self.render_obj = Box(self.program)        
        
    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)
        projection_mat = Transform.perspective(GLOBAL.FOVY, width/height, GLOBAL.ZNEAR, GLOBAL.ZFAR)
        BufferHelper.sendUniformToShaders(self.program, 'projection', projection_mat, 'm4')

    def display(self):
        super(QTDisplay, self).display()

if __name__ == '__main__':
    app = QtGui.QApplication(["Winfred's PyQt OpenGL"])
    widget = QTDisplay()
    widget.resize(GLOBAL.WIDTH, GLOBAL.HEIGHT)
    widget.show()
    app.exec_()

    #display = Display()
    #display.run()
