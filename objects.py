from __future__ import division
import sys
import numpy as np

import random

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

        self.wireframe_on = False
        self.color_on = True

    def draw(self):
        raise NotImplementedError

    def toggleWireframe(self):
        self.wireframe_on = not self.wireframe_on

    def toggleColor(self):
        self.color_on = not self.color_on

class Box(Object):
    """
    This is the basic box class to be rendered
    """

    def __init__(self, *args):
        """d
        Initialize VBO points
        """
        super(Box, self).__init__(*args)

        # positions
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

        # colors for positions
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

        # wire colors
        wireColor = np.zeros(8, [('wireColor', np.float32, 4)])
        wireColor['wireColor'] = [GLOBAL.WIREFRAME_COLOR for i in range(8)]
        wireColorBuffer = BufferHelper.sendToGPU('wireColor', wireColor, gl.GL_DYNAMIC_DRAW)

        # set up indices for drawing
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
        self.ind_buffer.bind()

    def draw(self):
        """
        Basic draw function which sends elements to the shaders.
        """
        if self.color_on:
            BufferHelper.sendToShaders(self.program, 'color', 'color')
            for i in range(6): # draw each side
                gl.glDrawElements(gl.GL_TRIANGLE_FAN, 4, gl.GL_UNSIGNED_INT, self.ind_buffer+4*4*i)

        if self.wireframe_on:
            BufferHelper.sendToShaders(self.program, 'wireColor', 'color')
            for i in range(6):
                gl.glDrawElements(gl.GL_LINE_LOOP, 4, gl.GL_UNSIGNED_INT, self.ind_buffer+4*4*i)


class Obj(Object):
    """
    Given obj specs, renders
    """

    def __init__(self, obj, *args):
        """
        Take everything from obj spec
        """
        super(Obj, self).__init__(*args)

        # init storage
        vertices_lines = []
        faces_lines = []

        for line in obj.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line[:2] == 'v ':
                vertices_lines.append(line)
            if line[:2] == 'f ':
                faces_lines.append(line)

        # clean up vertices
        vertices_all = [] # vertex buffer
        for line in vertices_lines:
            vertices_all.append( tuple([float(x) for x in line.split()[1:]]) )

        # clean up faces
        faces_all = [] # index buffer
        faces_v_num = [] # number of vertices to make face
        for line in faces_lines:
            v_num = 0
            for v in [int(x.split('//')[0]) for x in line.split()[1:]]:
                faces_all.append(v-1)
                v_num += 1
            faces_v_num.append(v_num)
        self.faces_v_num = faces_v_num

        # send vertices to GPU
        vertices = np.zeros(len(vertices_all), [('vertices', np.float32, 3)])
        vertices['vertices'] = vertices_all
        verticesBuffer = BufferHelper.sendToGPU('vertices', vertices, gl.GL_DYNAMIC_DRAW)
        BufferHelper.sendToShaders(self.program, 'vertices', 'position')

        # send colors to GPU
        color = np.zeros(len(vertices_all), [('color', np.float32, 4)])
        color['color'] = [(random.uniform(0,1),random.uniform(0,1),random.uniform(0,1),1) for x in vertices_all]
        colorBuffer = BufferHelper.sendToGPU('color', color, gl.GL_DYNAMIC_DRAW)

        # send wireframecolors to GPU
        wireframecolor = np.zeros(len(vertices_all), [('wireframeColor', np.float32, 4)])
        wireframecolor['wireframeColor'] = [(1,1,1,1) for x in vertices_all]
        wireframecolorBuffer = BufferHelper.sendToGPU('wireframeColor', wireframecolor, gl.GL_DYNAMIC_DRAW)

        # send indices as VBO
        indices = np.zeros(len(faces_all), [('indices', np.int32, 1)])
        indices['indices'] = faces_all
        self.ind_buffer = vbo.VBO(indices, target=gl.GL_ELEMENT_ARRAY_BUFFER)
        self.ind_buffer.bind()

    def draw(self):
        """
        Basic draw function, sending elements to shaders.
        """
        if self.color_on:
            BufferHelper.sendToShaders(self.program, 'color')
            accum_vertices = 0
            for n_vertices in self.faces_v_num:
                gl.glDrawElements(gl.GL_TRIANGLE_FAN, n_vertices, gl.GL_UNSIGNED_INT, self.ind_buffer+4*accum_vertices)
                accum_vertices += n_vertices

        if self.wireframe_on:
            BufferHelper.sendToShaders(self.program, 'wireframeColor', 'color')
            accum_vertices = 0
            for n_vertices in self.faces_v_num:
                gl.glDrawElements(gl.GL_LINE_LOOP, n_vertices, gl.GL_UNSIGNED_INT, self.ind_buffer+4*accum_vertices)
                accum_vertices += n_vertices
        
        
