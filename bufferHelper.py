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
from shaderHelper import ShaderHelper

class BufferHelper(object):
    """Keeps track of and provides useful functions for buffers and bufferIds on GPU"""

    buffers = {}

    @classmethod
    def bindBuffer(cls, name):
        """
        Binds buffer by name

        Parameters
        ----------
        name : str
        """
        buffer = cls.buffers[name]['bufferId']
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
    
    @classmethod
    def sendToGPU(cls, name, data, form):
        """
        Sends data to GPU.

        Parameters
        ----------
        name : str
        data : numpy.array
        form : gl.GLenum
            GL_STREAM_DRAW, GL_STREAM_READ, GL_STREAM_COPY, GL_STATIC_DRAW, GL_STATIC_READ,
            GL_STATIC_COPY, GL_DYNAMIC_DRAW, GL_DYNAMIC_READ, or GL_DYNAMIC_COPY
        
        Notes
        -----
        `name` is used to save buffer in `self.buffers`
        """
        # ask for an empty buffer slot from GPU
        buffer = gl.glGenBuffers(1)

        # make this buffer default for usage
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)

        # upload data to this buffer
        gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, form)

        # save buffer information
        cls.buffers[name] = {'bufferId': buffer, 'data': data}

        # return buffer id
        return buffer

    @classmethod
    def sendToShaders(cls, name, shader_vname = None):
        """
        Pulls shader parameter `shader_vname` location and linked with GPU buffer at `name`

        Parameters
        ----------
        program : gl.GLuint
        name : str
        shader_vname : str

        Notes
        -----
        If `shader_vname` is not entered, will use `name` as shader parameter var name
        """
        if not shader_vname:
            shader_vname = name

        # pull buffer information
        data = cls.buffers[name]['data']
        buffer = cls.buffers[name]['bufferId']

        # setup data
        stride = data.strides[0]
        offset = ctypes.c_void_p(0)  

        # query for shader variable information
        loc = gl.glGetAttribLocation(ShaderHelper.getProgram(), shader_vname)
        gl.glEnableVertexAttribArray(loc)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
        gl.glVertexAttribPointer(loc, data[0][0].size, gl.GL_FLOAT, False, stride, offset)

    @classmethod
    def sendUniformToShaders(cls, name, data, function_type):
        """
        Send uniform information to the shaders (no GPU buffer upload necessary)

        Parameters
        ----------
        program : gl.GLuint
        name : str
            shader uniform var name
        data : int or list or numpy.array
            need to make sure coincides with function_type
        function_type : str
            see switch for available uniform types
        """
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
        
        loc = gl.glGetUniformLocation(ShaderHelper.getProgram(), name)
        if function_type[0] == 'm':
            switch[function_type](loc, 1, gl.GL_FALSE, data)
        else:
            switch[function_type](loc, *data)
        
