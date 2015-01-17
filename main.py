from __future__ import division
import sys
import OpenGL.GL as GL
import OpenGL.GLU as GLU
import OpenGL.GLUT as GLUT
from configs import Global

GLOBAL = Global()

class Display(object):
    """
    Basic display class -- used to call and initialize GLUT window
    """

    def __init__(self, display_res):
        """
        @display_res: 2D tuple, width x height of display (GLUT) window
        """
        
        # save init arguments for later use
        self.display_res = display_res

        # init GLUT
        GLUT.glutInit(sys.argv)
        GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA | GLUT.GLUT_DOUBLE | GLUT.GLUT_DEPTH | GLUT.GLUT_MULTISAMPLE)
        GLUT.glutInitWindowSize(*self.display_res)
        GLUT.glutInitWindowPosition(0, 0)

        # keep track of window
        self.window = GLUT.glutCreateWindow('Frightened Rabbit')

        # glut func setting
        GLUT.glutDisplayFunc(self.draw)
        #GLUT.glutReshapeFunc(self.reshape)
        #GLUT.glutMouseFunc(self.on_click)
        #GLUT.glutMotionFunc(self.on_mouse_move)
        #GLUT.glutKeyboardFunc(self.keyboard)

        # call refresh every 10 msecs
        #GLUT.glutTimerFunc(10, self.on_timer, 10)
        Display.reshape(*self.display_res)
    
    @staticmethod
    def reshape(w, h):
        GL.glViewport(0, 0, w, h)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        #GLU.gluPerspective(60., w / float(h), .1, 600000.)

    def on_timer(self, t):
        """Basic function to define timer for buffer refresh"""
        GLUT.glutTimerFunc(t, self.on_timer, t)
        GLUT.glutPostRedisplay()

    def keyboard(self, key, x, y):
        pass

    def on_mouse_move(self, x, y):
        pass

    def on_click(self, button, state, x, y):
        pass

    def run(self):
        """Start up the draw loop"""
        GLUT.glutMainLoop()

    def draw(self):
        """Draw Here!"""
        GL.glClearColor(0, 0, 1, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glColor3f(1,1,0)
        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glVertex2d(.2,.2)
        GL.glVertex2d(-.2,.2)
        GL.glVertex2d(.2,-.2)
        GL.glEnd()

        GL.glFlush()
        GLUT.glutSwapBuffers()

if __name__ == '__main__':
    display = Display((GLOBAL.WIDTH, GLOBAL.HEIGHT))
    display.run()
