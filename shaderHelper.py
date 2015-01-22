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

class ShaderHelper(object):
    """Keeps track of and provides useful functions for handling shaders"""

    programs = {
        # (vertex_loc, fragment_loc) => program
    }


    program = None

    @classmethod
    def getProgram(cls):
        if cls.program is None:
            cls.buildAndUseProgram()            
        return cls.program

    @classmethod
    def buildAndUseProgram(cls, vertex_loc = Global.VERTEX_SHADER_LOC, fragment_loc = Global.FRAGMENT_SHADER_LOC):
        print 'building and using [v: %s, f: %s]' %(vertex_loc, fragment_loc)

        # check if vertex, fragment combo is already a program
        if (vertex_loc, fragment_loc) in cls.programs:

            program = cls.programs[(vertex_loc, fragment_loc)]
            gl.glUseProgram(program)
            cls.program = program
            print "Now using program", cls.program
            return

        # create program for GPU
        program  = gl.glCreateProgram()
        
        # check if shaders are already used
        vertex   = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        v_shader_code = open(vertex_loc).read()
        gl.glShaderSource(vertex, v_shader_code)
        gl.glCompileShader(vertex)
        gl.glAttachShader(program, vertex)

        fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        f_shader_code = open(fragment_loc).read()
        gl.glShaderSource(fragment, f_shader_code)
        gl.glCompileShader(fragment)
        gl.glAttachShader(program, fragment)

        cls.programs[(vertex_loc, fragment_loc)] = program

        # build and clean up
        gl.glLinkProgram(program)

        # Make program the default program
        gl.glUseProgram(program)

        cls.program = program
        print "Now using program", cls.program
