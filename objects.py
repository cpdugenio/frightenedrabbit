from __future__ import division
import sys
import numpy as np

import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut

from OpenGL.arrays import vbo
import ctypes

from configs import Global
from shaderHelper import ShaderHelper
from bufferHelper import BufferHelper

# use and edit configs.Global class for configs
GLOBAL = Global()

class Object(object):
    """
    This is the base class for rendering objects
    """

    def __init__(self):
        self.wireframe_on = Global.WIREFRAME_DEFAULT
        self.color_on = Global.COLOR_DEFAULT
        self.buildShaders()

    def draw(self):
        raise NotImplementedError

    def toggleWireframe(self):
        self.wireframe_on = not self.wireframe_on

    def toggleColor(self):
        self.color_on = not self.color_on

    def refreshUV(self):
        pass

    def buildShaders(self):
        raise NotImplementedError

class UVObject(Object):
    """
    Base class for UV objects
    """

    def buildShaders(self):
        ShaderHelper.buildAndUseProgram()

    def __init__(self):
        super(UVObject, self).__init__()

        self.initUV()

    def refreshUV(self):
        self.initUV()

    def initUV(self):
        self.maxU, self.maxV = GLOBAL.MAX_U, GLOBAL.MAX_V
        point = []
        self.faces_v_num = []
        for u in range(self.maxU):
            for v in range(self.maxV):
                point.append((u/(self.maxU),v/(self.maxV),0,1.0))
                point.append((u/(self.maxU),(v+1)/(self.maxV),0,1.0))
                point.append(((u+1)/(self.maxU),(v+1)/(self.maxV),0,1.0))
                point.append(((u+1)/(self.maxU),v/(self.maxV),0,1.0))
                self.faces_v_num.append(4)

        acc = self.faces_v_num[::]
        acc.insert(0,0)
        self.faces_v_start = np.cumsum(acc)
        self.faces_len = len(self.faces_v_num)

        position = np.zeros(self.maxU * self.maxV * 4, [('position', np.float32, 4)])
        position['position'] = point
        BufferHelper.sendToGPU('position', position, gl.GL_DYNAMIC_DRAW)
        BufferHelper.sendToShaders('position')

        normal = np.zeros(self.maxU * self.maxV * 4, [('normal', np.float32, 4)])
        normal['normal'] = [(x[0], x[1], x[2], 0.0) for x in point]
        BufferHelper.sendToGPU('normal', normal, gl.GL_DYNAMIC_DRAW)
        BufferHelper.sendToShaders('normal')        

        color = np.zeros(self.maxU * self.maxV * 4, [('color', np.float32, 4)])
        color['color'] = [GLOBAL.SOLID_COLOR for x in position]
        BufferHelper.sendToGPU('color', color, gl.GL_DYNAMIC_DRAW)

        wireframecolor = np.zeros(self.maxU * self.maxV * 4, [('wireframeColor', np.float32, 4)])
        wireframecolor['wireframeColor'] = [GLOBAL.WIREFRAME_COLOR for x in position]
        BufferHelper.sendToGPU('wireframeColor', wireframecolor, gl.GL_DYNAMIC_DRAW)

        

    def draw(self):
        if self.color_on:
            # make sure polygons draw under wireframe
            gl.glPolygonOffset(2.5, 0);
            gl.glEnable(gl.GL_POLYGON_OFFSET_FILL);

            BufferHelper.sendToShaders('color')
            gl.glMultiDrawArrays(gl.GL_TRIANGLE_FAN, self.faces_v_start, self.faces_v_num, self.faces_len)

            gl.glDisable(gl.GL_POLYGON_OFFSET_FILL);


        if self.wireframe_on:
            BufferHelper.sendToShaders('wireframeColor', 'color')
            gl.glMultiDrawArrays(gl.GL_LINE_LOOP, self.faces_v_start, self.faces_v_num, self.faces_len)


class UVSphere(UVObject):
    def buildShaders(self):
        ShaderHelper.buildAndUseProgram('sphere.glsl', 'uvfragment.glsl')

    def __init__(self):
        super(UVSphere, self).__init__()
        
class Box(Object):
    """
    This is the basic box class to be rendered
    """


    def buildShaders(self):
        ShaderHelper.buildAndUseProgram()

    def __init__(self):
        """
        Initialize VBO points
        """

        super(Box, self).__init__()

        # positions
        position = np.zeros(8, [('position', np.float32, 4)])
        position['position'] = [
            (-1,-1,-1, 1),
            (-1, 1,-1, 1),
            ( 1, 1,-1, 1),
            ( 1,-1,-1, 1),
            (-1,-1, 1, 1),
            (-1, 1, 1, 1),
            ( 1, 1, 1, 1),
            ( 1,-1, 1, 1),
        ]
        posBuffer = BufferHelper.sendToGPU('position', position, gl.GL_DYNAMIC_DRAW)
        BufferHelper.sendToShaders('position')

        # normals
        normal = np.zeros(8, [('normal', np.float32, 3)])
        normal['normal'] = [x[:3] for x in position['position']]
        BufferHelper.sendToGPU('normal', normal, gl.GL_DYNAMIC_DRAW)
        BufferHelper.sendToShaders('normal')
        

        # colors for positions
        color = np.zeros(8, [('color', np.float32, 4)])
        color['color'] = [GLOBAL.SOLID_COLOR for x in position]
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
            # make sure polygons draw under wireframe
            gl.glPolygonOffset(2.5, 0);
            gl.glEnable(gl.GL_POLYGON_OFFSET_FILL);

            BufferHelper.sendToShaders('color', 'color')
            for i in range(6): # draw each side
                gl.glDrawElements(gl.GL_TRIANGLE_FAN, 4, gl.GL_UNSIGNED_INT, self.ind_buffer+4*4*i)

            gl.glDisable(gl.GL_POLYGON_OFFSET_FILL);


        if self.wireframe_on:
            BufferHelper.sendToShaders('wireColor', 'color')
            for i in range(6):
                gl.glDrawElements(gl.GL_LINE_LOOP, 4, gl.GL_UNSIGNED_INT, self.ind_buffer+4*4*i)


class Obj(Object):
    """
    Given obj specs, renders
    """

    def buildShaders(self):
        ShaderHelper.buildAndUseProgram()


    def __init__(self, obj):
        """
        Take everything from obj spec
        """

        super(Obj, self).__init__()

        # init storage
        vertices_lines = []
        faces_lines = []
        normals_lines = []

        for line in obj.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line[:2] == 'v ':
                vertices_lines.append(line)
            elif line[:2] == 'f ':
                faces_lines.append(line)
            elif line[:3] == 'vn ':
                normals_lines.append(line)

        # clean up vertices
        vertices_all = [] # vertex buffer
        for line in vertices_lines:
            vertices_all.append( tuple([float(x) for x in line.split()[1:] + [1.0]]) )

        # clean up vertices normals
        normals_all = [] # normal buffer
        for line in normals_lines:
            normals_all.append( tuple([float(x) for x in line.split()[1:]]) )

        # clean up faces
        faces_v_num = [] # number of vertices to make face
        faces_ordered = [] # list of indices in order of face-indices
        normals_ordered = [] # list of normals aligned with faces
        
        # convert each face to list of corresponding vertices
        for line in faces_lines:
            v_num = 0
            for v in [int(x.split('//')[0])-1 for x in line.split()[1:]]:
                faces_ordered.append(vertices_all[v])
                v_num += 1
            if len(normals_all):
                for v in [int(x.split('//')[1])-1 for x in line.split()[1:]]:
                    normals_ordered.append(normals_all[v])
            faces_v_num.append(v_num)

        self.faces_v_num = faces_v_num # number of vertices per face
        acc = self.faces_v_num[::]
        acc.insert(0,0) # begin at zero index
        self.faces_v_start = np.cumsum(acc) # start of corresponding face
        self.faces_len = len(faces_v_num)
        
        # send ordered normals to GPU
        normal = np.zeros(len(faces_ordered), [('normal', np.float32, 3)])
        if len(normals_ordered):
            normal['normal'] = normals_ordered
        else:
            normal['normal'] = [(0,0,0) for x in faces_ordered]
        BufferHelper.sendToGPU('normal', normal, gl.GL_DYNAMIC_DRAW)
        BufferHelper.sendToShaders('normal')

        # send ordered vertices to GPU
        vertices = np.zeros(len(faces_ordered), [('vertices', np.float32, 4)])
        vertices['vertices'] = faces_ordered
        BufferHelper.sendToGPU('vertices', vertices, gl.GL_DYNAMIC_DRAW)
        BufferHelper.sendToShaders('vertices', 'position')

        # send colors to GPU
        color = np.zeros(len(faces_ordered), [('color', np.float32, 4)])
        color['color'] = [GLOBAL.SOLID_COLOR for x in faces_ordered]
        BufferHelper.sendToGPU('color', color, gl.GL_DYNAMIC_DRAW)

        # send wireframecolors to GPU
        wireframecolor = np.zeros(len(faces_ordered), [('wireframeColor', np.float32, 4)])
        wireframecolor['wireframeColor'] = [GLOBAL.WIREFRAME_COLOR for x in faces_ordered]
        BufferHelper.sendToGPU('wireframeColor', wireframecolor, gl.GL_DYNAMIC_DRAW)


        
    def draw(self):
        """
        Basic draw function, sending elements to shaders.
        """

        if self.color_on:
            # make sure polygons draw under wireframe
            gl.glPolygonOffset(2.5, 0);
            gl.glEnable(gl.GL_POLYGON_OFFSET_FILL);
            
            BufferHelper.sendToShaders('color')
            gl.glMultiDrawArrays(gl.GL_TRIANGLE_FAN, self.faces_v_start, self.faces_v_num, self.faces_len)
            
            gl.glDisable(gl.GL_POLYGON_OFFSET_FILL);

        if self.wireframe_on:
            BufferHelper.sendToShaders('wireframeColor', 'color')
            gl.glMultiDrawArrays(gl.GL_LINE_LOOP, self.faces_v_start, self.faces_v_num, self.faces_len)
