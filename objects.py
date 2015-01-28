from __future__ import division
import sys
import numpy as np

import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut
from OpenGL.constants import GLfloat_4

from OpenGL import arrays
from OpenGL.arrays import vbo
import ctypes

from PyQt4.QtCore import Qt
from PyQt4 import QtGui
from PyQt4.QtOpenGL import QGLWidget, QGLFormat

from configs import Global
from shaderHelper import ShaderHelper
from bufferHelper import BufferHelper


class Object(object):
    """
    This is the base class for rendering objects
    """

    def __init__(self):
        self.wireframe_on = Global.WIREFRAME_DEFAULT
        self.color_on = Global.COLOR_DEFAULT
        self.buildShaders()

        self.setupLights()

        self.lights_on = False
        self.setLightsShading(True)
        self.setNormalsShading(False)
        self.setZbufferShading(False)

        BufferHelper.sendUniformToShaders('eye', Global.EYE, '3f')

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

    def testFunction(self, value):
        print value

    def setNormalsShading(self, bool):
        BufferHelper.sendUniformToShaders('normalsShading', [bool], '1i')

    def setZbufferShading(self, bool):
        BufferHelper.sendUniformToShaders('zbufferShading', [bool], '1i')

    def setLightsShading(self, bool):
        self.light_on = bool
        if bool:
            BufferHelper.sendUniformToShaders('activeLights', [self.activeLights], '1i')
        else:
            BufferHelper.sendUniformToShaders('activeLights', [0], '1i')

    def setupLights(self):
        self.lights = [[GLfloat_4(*attr) for attr in light] for light in Global.LIGHTS]
    
        for i, light in enumerate(self.lights):
            amb, diff, spec, pos = light
            light = eval("gl.GL_LIGHT%d" % i)
            gl.glLightfv(light, gl.GL_AMBIENT, amb)
            gl.glLightfv(light, gl.GL_DIFFUSE, diff)
            gl.glLightfv(light, gl.GL_SPECULAR, spec)
            gl.glLightfv(light, gl.GL_POSITION, pos)

        self.activeLights = len(self.lights)

    def setLayoutAttr(self, layout):
        """
        Return (current row nums, current max colspan)
        """
        return (0,0)

    def getWidget(self):
        widget = QtGui.QWidget()
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        self.setLayoutAttr(grid)
        widget.setLayout(grid)
        return widget

class UVObject(Object):
    """
    Base class for UV objects
    """

    def buildShaders(self):
        ShaderHelper.buildAndUseProgram()

    def __init__(self):
        super(UVObject, self).__init__()

        self.U, self.V = 20, 20

        self.initUV()

    def changeV(self, value):
        self.V = value
        self.initUV()

    def changeU(self, value):
        self.U = value
        self.initUV()

    def initUV(self):
        self.maxU, self.maxV = self.U, self.V
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

        color = np.zeros(self.maxU * self.maxV * 4, [('color', np.float32, 4)])
        color['color'] = [Global.SOLID_COLOR for i in range(len(position))]
        BufferHelper.sendToGPU('color', color, gl.GL_DYNAMIC_DRAW)

        wireframecolor = np.zeros(self.maxU * self.maxV * 4, [('wireframeColor', np.float32, 4)])
        wireframecolor['wireframeColor'] = [Global.WIREFRAME_COLOR for x in position]
        BufferHelper.sendToGPU('wireframeColor', wireframecolor, gl.GL_DYNAMIC_DRAW)


    def setLayoutAttr(self, layout):
        """
        Return (current row nums, current max colspan)
        """
        u_slider = QtGui.QSlider(Qt.Horizontal)
        u_slider.setRange(2, Global.MAX_U)
        u_slider.setSliderPosition(self.U)
        u_slider.valueChanged[int].connect(self.changeU)
        
        v_slider = QtGui.QSlider(Qt.Horizontal)
        v_slider.setRange(2, Global.MAX_V)
        v_slider.setSliderPosition(self.V)
        v_slider.valueChanged[int].connect(self.changeV)

        layout.addWidget(QtGui.QLabel('U:'), 1, 1)
        layout.addWidget(u_slider, 1, 2, 1, 3)
        layout.addWidget(QtGui.QLabel('V:'), 2, 1)
        layout.addWidget(v_slider, 2, 2, 1, 3)
        return (2,4)
        

    def draw(self):
        if self.color_on:
            # make sure polygons draw under wireframe
            BufferHelper.sendUniformToShaders('wireframe', [0], '1i')

            gl.glPolygonOffset(5, 0);
            gl.glEnable(gl.GL_POLYGON_OFFSET_FILL);

            BufferHelper.sendToShaders('color')
            gl.glMultiDrawArrays(gl.GL_TRIANGLE_FAN, self.faces_v_start, self.faces_v_num, self.faces_len)

            gl.glDisable(gl.GL_POLYGON_OFFSET_FILL);

        if self.wireframe_on:
            BufferHelper.sendUniformToShaders('wireframe', [1], '1i')

            BufferHelper.sendToShaders('wireframeColor', 'color')
            gl.glMultiDrawArrays(gl.GL_LINE_LOOP, self.faces_v_start, self.faces_v_num, self.faces_len)


class UVSphere(UVObject):
    def buildShaders(self):
        ShaderHelper.buildAndUseProgram('shaders/sphere.vert')

    def __init__(self):
        super(UVSphere, self).__init__()

class UVMobius(UVObject):
    def buildShaders(self):
        ShaderHelper.buildAndUseProgram('shaders/mobius.vert')

    def __init__(self):
        super(UVMobius, self).__init__()

class UVTorus(UVObject):
    def buildShaders(self):
        ShaderHelper.buildAndUseProgram('shaders/torus.vert')

    def __init__(self):
        super(UVTorus, self).__init__()
        self.defaultOuterRad = 10
        self.defaultInnerRad = 3
        self.changeOuterRadius(self.defaultOuterRad)
        self.changeInnerRadius(self.defaultInnerRad)

    def changeOuterRadius(self, value):
        BufferHelper.sendUniformToShaders('RADIUS', [value/10.0], '1f')

    def changeInnerRadius(self, value):
        BufferHelper.sendUniformToShaders('r', [value/10.0], '1f')

    def setLayoutAttr(self, layout):
        rows, colspan = super(UVTorus, self).setLayoutAttr(layout)

        ri_slider = QtGui.QSlider(Qt.Horizontal)
        ri_slider.setRange(1, 100)
        ri_slider.setSliderPosition(self.defaultInnerRad)
        ri_slider.valueChanged[int].connect(self.changeInnerRadius)

        ro_slider = QtGui.QSlider(Qt.Horizontal)
        ro_slider.setRange(1, 100)
        ro_slider.setSliderPosition(self.defaultOuterRad)
        ro_slider.valueChanged[int].connect(self.changeOuterRadius)
        
        layout.addWidget(QtGui.QLabel('Inner Radius'), rows+1, 1)
        layout.addWidget(ri_slider, rows+1, 2, 1, colspan-3)

        layout.addWidget(QtGui.QLabel('Outer Radius'), rows+2, 1)
        layout.addWidget(ro_slider, rows+2, 2, 1, colspan-3)
        
        return (rows+2, colspan)


class UVKlein(UVObject):
    def buildShaders(self):
        ShaderHelper.buildAndUseProgram('shaders/klein.vert')
        self.defaultRad = 25
        self.changeRadius(self.defaultRad)

    def __init__(self):
        super(UVKlein, self).__init__()

    def setLayoutAttr(self, layout):
        rows, colspan = super(UVKlein, self).setLayoutAttr(layout)

        r_slider = QtGui.QSlider(Qt.Horizontal)
        r_slider.setRange(1, 100)
        r_slider.setSliderPosition(self.defaultRad)
        r_slider.valueChanged[int].connect(self.changeRadius)
        
        layout.addWidget(QtGui.QLabel('Radius'), rows+1, 1)
        layout.addWidget(r_slider, rows+1, 2, 1, colspan-3)
        
        return (rows+1, colspan)

    def changeRadius(self, value):
        BufferHelper.sendUniformToShaders('r', [value/10.0], '1f')
        

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
        position = np.zeros(24, [('position', np.float32, 4)])
        position['position'] = [
            # top
            (-1.0, 1.0,-1.0, 1.0),
            ( 1.0, 1.0,-1.0, 1.0),
            ( 1.0, 1.0, 1.0, 1.0),
            (-1.0, 1.0, 1.0, 1.0),
            # bottom
            (-1.0,-1.0,-1.0, 1.0),
            ( 1.0,-1.0,-1.0, 1.0),
            ( 1.0,-1.0, 1.0, 1.0),
            (-1.0,-1.0, 1.0, 1.0),
            # right
            ( 1.0,-1.0,-1.0, 1.0),
            ( 1.0, 1.0,-1.0, 1.0),
            ( 1.0, 1.0, 1.0, 1.0),
            ( 1.0,-1.0, 1.0, 1.0),
            # left
            (-1.0,-1.0,-1.0, 1.0),
            (-1.0, 1.0,-1.0, 1.0),
            (-1.0, 1.0, 1.0, 1.0),
            (-1.0,-1.0, 1.0, 1.0),
            # front
            (-1.0,-1.0, 1.0, 1.0),
            ( 1.0,-1.0, 1.0, 1.0),
            ( 1.0, 1.0, 1.0, 1.0),
            (-1.0, 1.0, 1.0, 1.0),
            # back
            (-1.0,-1.0,-1.0, 1.0),
            ( 1.0,-1.0,-1.0, 1.0),
            ( 1.0, 1.0,-1.0, 1.0),
            (-1.0, 1.0,-1.0, 1.0),
        ]
        posBuffer = BufferHelper.sendToGPU('position', position, gl.GL_DYNAMIC_DRAW)
        BufferHelper.sendToShaders('position')

        # normals
        normal = np.zeros(24, [('normal', np.float32, 3)])
        normal['normal'] = [
            (0, 1.0, 0),
        ] * 4 + [
            (0,-1.0, 0),
        ] * 4 + [
            (1.0, 0 ,0),
        ] * 4 + [
            (-1.0,0, 0),
        ] * 4 + [
            (0, 0, 1.0),
        ] * 4 + [
            (0, 0,-1.0),
        ] * 4
        BufferHelper.sendToGPU('normal', normal, gl.GL_DYNAMIC_DRAW)
        BufferHelper.sendToShaders('normal')
        
        # colors for positions
        color = np.zeros(24, [('color', np.float32, 4)])
        color['color'] = [Global.SOLID_COLOR for i in range(24)]
        colorBuffer = BufferHelper.sendToGPU('color', color, gl.GL_DYNAMIC_DRAW)

        # wire colors
        wireColor = np.zeros(24, [('wireColor', np.float32, 4)])
        wireColor['wireColor'] = [Global.WIREFRAME_COLOR for i in range(24)]
        wireColorBuffer = BufferHelper.sendToGPU('wireColor', wireColor, gl.GL_DYNAMIC_DRAW)

        # set up indices for drawing
        indices = np.zeros(24, [('indices', np.int32, 1)])
        indices['indices'] = range(24)
        self.ind_buffer = vbo.VBO(indices, target=gl.GL_ELEMENT_ARRAY_BUFFER)
        self.ind_buffer.bind()

    def draw(self):
        """
        Basic draw function which sends elements to the shaders.
        """
        if self.color_on:
            # make sure polygons draw under wireframe
#            gl.glPolygonOffset(2.5, 0);
#            gl.glEnable(gl.GL_POLYGON_OFFSET_FILL);
            BufferHelper.sendUniformToShaders('wireframe', [0], '1i')

            BufferHelper.sendToShaders('color', 'color')
            for i in range(6): # draw each side
                gl.glDrawElements(gl.GL_TRIANGLE_FAN, 4, gl.GL_UNSIGNED_INT, self.ind_buffer+4*4*i)

#            gl.glDisable(gl.GL_POLYGON_OFFSET_FILL);

        if self.wireframe_on:
            BufferHelper.sendUniformToShaders('wireframe', [1], '1i')
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
        color['color'] = [Global.SOLID_COLOR for x in faces_ordered]
        BufferHelper.sendToGPU('color', color, gl.GL_DYNAMIC_DRAW)

        # send wireframecolors to GPU
        wireframecolor = np.zeros(len(faces_ordered), [('wireframeColor', np.float32, 4)])
        wireframecolor['wireframeColor'] = [Global.WIREFRAME_COLOR for x in faces_ordered]
        BufferHelper.sendToGPU('wireframeColor', wireframecolor, gl.GL_DYNAMIC_DRAW)


        
    def draw(self):
        """
        Basic draw function, sending elements to shaders.
        """

        if self.color_on:
            # make sure polygons draw under wireframe
            BufferHelper.sendUniformToShaders('wireframe', [0], '1i')
            gl.glPolygonOffset(2.5, 0);
            gl.glEnable(gl.GL_POLYGON_OFFSET_FILL);
            
            BufferHelper.sendToShaders('color')
            gl.glMultiDrawArrays(gl.GL_TRIANGLE_FAN, self.faces_v_start, self.faces_v_num, self.faces_len)
            
            gl.glDisable(gl.GL_POLYGON_OFFSET_FILL);

        if self.wireframe_on:
            BufferHelper.sendUniformToShaders('wireframe', [1], '1i')
            BufferHelper.sendToShaders('wireframeColor', 'color')
            gl.glMultiDrawArrays(gl.GL_LINE_LOOP, self.faces_v_start, self.faces_v_num, self.faces_len)

