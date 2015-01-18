from __future__ import division
import sys
import numpy as np

import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut

from OpenGL.arrays import vbo
import ctypes

from configs import Global
from bufferHelper import BufferHelper

# use and edit configs.Global class for configs
GLOBAL = Global()

class Object(object):
    """
    This is the base class for rendering objects
    """

    def __init__(self, program):
        self.program = program
        print program

    def draw(self):
        raise NotImplementedError


class Box(Object):
    """
    This is the basic box class
    """

    def __init__(self, *args):
        """
        Initialize VBO points
        """
        super(Box, self).__init__(*args)

        position = np.zeros(8, [('position', np.float32, 3)])
        position['position'] = [
            (-1,-1,-1),
            (-1, 1,-1),
            ( 1, 1,-1),
            ( 1,-1,-1),
            (-1,-1, 1),
            (-1, 1, 1),
            ( 1, 1, 1),
            ( 1,-1, 1),
        ]
        posBuffer = BufferHelper.sendToGPU('position', position, gl.GL_DYNAMIC_DRAW)
        BufferHelper.sendToShaders(self.program, 'position')

        color = np.zeros(8, [('color', np.float32, 4)])
        color['color'] = [
            (0,0,0,1),
            (0,1,0,1),
            (1,1,0,1),
            (1,0,0,1),
            (0,0,1,1),
            (0,1,1,1),
            (1,1,1,1),
            (1,0,1,1),
        ]
        colorBuffer = BufferHelper.sendToGPU('color', color, gl.GL_DYNAMIC_DRAW)
        BufferHelper.sendToShaders(self.program, 'color', 'colorx')

        indices = np.zeros(4*6, [('indices', np.int32, 1)])

        indices['indices'] = [
            0,1,2,3, #back
            4,5,6,7, #front
            2,3,7,6, #right
            0,1,5,4, #left
            0,3,7,4, #bottom
            1,2,6,5, #top
        ]
        
        self.ind_buffer = vbo.VBO(indices, target=gl.GL_ELEMENT_ARRAY_BUFFER)

    def draw(self):

#        gl.glDrawArrays(gl.GL_TRIANGLE_FAN, 0, 4)
        self.ind_buffer.bind()

        for i in range(6):
            gl.glDrawElements(gl.GL_TRIANGLE_FAN, 4, gl.GL_UNSIGNED_INT, self.ind_buffer+16*i)


