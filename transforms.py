#!/usr/bin/env python

from __future__ import division
import numpy as np
from numpy.linalg import norm, inv

class Transform(object):
    @staticmethod
    def translate(x, y, z):
        """
        Returns
        -------
        numpy.matrix
            4x4 translate matrix which is okay to be multiplied and sent directly to shader.
        """
        T = np.identity(4, dtype=np.float32)
        T[0:3,3] = [x,y,z]

        return np.matrix(T.T)

    @staticmethod
    def scale(x, y, z):
        """
        Returns
        -------
        numpy.matrix
            4x4 scale matrix which is okay to be multiplied and sent directly to shader.
        """
        T = np.identity(4, dtype=np.float32)
        T[0,0] = x
        T[1,1] = y
        T[2,2] = z
        return np.matrix(T.T)
        
    @staticmethod
    def lookat(eye, lookat, up):
        """
        http://webglfactory.blogspot.com/2011/06/how-to-create-view-matrix.html

        Parameters
        ----------
        eye : tuple
            3-D tuple defining eye location
        lookat : tuple
            3-D tuple defining point to center on screen
        up : tuple
            3-D tuple defining what is up

        Returns
        -------
        numpy.mat
            Numpy 4x4 transformation lookAt matrix
        """
        
        E = np.array(eye)
        C = np.array(lookat)
        U = np.array(up)

        Vz = E - C
        Vz /= norm(Vz)
        Vx = np.cross(U, Vz)
        Vx /= norm(Vx)
        Vy = np.cross(Vz, Vx)

        M = np.identity(4, dtype=np.float32)
        M[0,0:3] = Vx
        M[1,0:3] = Vy
        M[2,0:3] = Vz
        M[3,0:3] = E
        
        return inv(M)

    @staticmethod
    def frustum(right, left, top, bottom, near, far):
        """
        http://www.songho.ca/opengl/gl_projectionmatrix.html

        Parameters
        ----------
        right : float
        left : float
        top : float
        bottom : float
        near : float
        far : float

        
        Returns
        -------
        numpy.mat
            Numpy 4x4 frustum matrix


        Notes
        -----
        This function does not validate values (i.e. if near < far)
        """
        frust = np.zeros((4,4), dtype=np.float32)
        frust[0,0] = 2. * near / (right - left)
        frust[0,2] = (right + left) / (right - left)
        frust[1,1] = 2. * near / (top - bottom)
        frust[1,3] = (top+bottom) / (top - bottom)
        frust[2,2] = -(far+near) / (far - near)
        frust[2,3] = -2. * far * near / (far - near)
        frust[3,2] = -1.
        return frust.T

    @staticmethod
    def perspective(fovy, aspect, near, far):
        """
        http://www.songho.ca/opengl/gl_projectionmatrix.html

        Parameters
        ----------
        fovy : float
            FULL field of view, y-axis (in degrees, from top to bottom of frustum)
        aspect: float
            width / height
        near : float
        far : float

        
        Returns
        -------
        numpy.mat
            Numpy 4x4 perspective matrix
        """
        top = np.tan(fovy * np.pi / 360.0) * near
        right = aspect * top

        return Transform.frustum(right, -right, top, -top, near, far)

