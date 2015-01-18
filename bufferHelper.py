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

# use and edit configs.Global class for configs
GLOBAL = Global()

class BufferHelper(object):
    """Keeps track of and provides useful functions for buffers and bufferIds on GPU"""

    buffers = {}

    @classmethod
    def bindBuffer(cls, name):
        buffer = cls.buffers[name]['bufferId']
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
    
    @classmethod
    def sendToGPU(cls, name, data, form):
        # ask for an empty buffer slot from GPU
        buffer = gl.glGenBuffers(1)

        # make this buffer default for usage
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)

        # upload data to this buffer
        gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_DYNAMIC_DRAW)

        # save buffer information
        cls.buffers[name] = {'bufferId': buffer, 'data': data}

        # return buffer id
        return buffer

    @classmethod
    def sendToShaders(cls, program, name, shader_vname = None):
        if not shader_vname:
            shader_vname = name

        # pull buffer information
        data = cls.buffers[name]['data']
        buffer = cls.buffers[name]['bufferId']

        # setup data
        stride = data.strides[0]
        offset = ctypes.c_void_p(0)  

        # query for shader variable information
        loc = gl.glGetAttribLocation(program, shader_vname)
        gl.glEnableVertexAttribArray(loc)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
        gl.glVertexAttribPointer(loc, data[0][0].size, gl.GL_FLOAT, False, stride, offset)

    @classmethod
    def sendUniformToShaders(cls, program, name, data, function_type):
        switch = {
            '1f': gl.glUniform1f,
            '2f': gl.glUniform2f,
            '3f': gl.glUniform3f,
            '4f': gl.glUniform4f,
            '1i': gl.glUniform1i,
            '2i': gl.glUniform2i,
            '3i': gl.glUniform3i,
            '4i': gl.glUniform4i,
            'm3': gl.glUniformMatrix3fv,
            'm4': gl.glUniformMatrix4fv,
        }
        
        loc = gl.glGetUniformLocation(program, name)
        if function_type[0] == 'm':
            switch[function_type](loc, 1, gl.GL_FALSE, data)
        else:
            switch[function_type](loc, *data)
        
