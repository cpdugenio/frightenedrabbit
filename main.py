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

        self.build()

        self.reshape(GLOBAL.WIDTH, GLOBAL.HEIGHT)

        self.prep_matrices()

    def display(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)

        gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

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
        position = np.zeros(4, [('position', np.float32, 3)])
        position['position'] = [ (-1,-1,0),   (-1,+1,0),   (+1,-1,0),   (+1,+1,0)   ]
        posBuffer = BufferHelper.sendToGPU('position', position, gl.GL_DYNAMIC_DRAW)
        BufferHelper.sendToShaders(self.program, 'position')

        color = np.zeros(4, [('color', np.float32, 4)])
        color['color'] = [(1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1)]
        colorBuffer = BufferHelper.sendToGPU('color', color, gl.GL_DYNAMIC_DRAW)
        BufferHelper.sendToShaders(self.program, 'color', 'colorx')

        # setup view matrix
        view_mat = np.array(Transform.lookat(GLOBAL.EYE, GLOBAL.LOOKAT, GLOBAL.UP))
        BufferHelper.sendUniformToShaders(self.program, 'view', view_mat, 'm4')

        # setup model matrix
        model_mat = np.matrix(np.identity(4, dtype=np.float32))
        model_mat *= Transform.translate(0,0,-10)
        BufferHelper.sendUniformToShaders(self.program, 'model', model_mat, 'm4')

    def run(self):
        glut.glutMainLoop()

if __name__ == '__main__':
    display = Display()
    display.run()
