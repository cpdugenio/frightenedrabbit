from __future__ import division
import sys
import numpy

import OpenGL.GL as GL
import OpenGL.GLU as GLU
import OpenGL.GLUT as GLUT

from OpenGL.arrays import vbo

from configs import Global

# use and edit configs.Global class for configs
GLOBAL = Global()

class Object(object):
    """
    This is the base class for rendering objects
    """

    def __init__(self):
        pass

    def draw(self):
        raise NotImplementedError


class Box(Object):
    """
    This is the basic box class
    """

    def __init__(self):
        """
        Initialize VBO points
        """
        super(Box, self).__init__()

        v_data = np.zeros(4, [('pos', np.float32, 3)])
        v_data['pos'] = [
            (-1,-1,-1),
            (-1, 1,-1),
            ( 1, 1,-1),
            ( 1,-1,-1),
            (-1,-1, 1),
            (-1, 1, 1),
            ( 1, 1, 1),
            ( 1,-1, 1),
        ]
        vBuffer = BufferHelper.sendToGPU('pos', v_data, gl.GL_DYNAMIC_DRAW)
        BufferHelper.sendToShaders(self.program, 'position')

    def draw(self):
        print 'test'


        

