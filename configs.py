class Global(object):
    """
    Global class used for configs

    Notes
    -----
    On `self.__init__()`, shaders are pulled from files and placed into their respective vars:
        `VERTEX_SHADER_LOC` => `VERTEX_SHADER_CODE`
        `FRAGMENT_SHADER_LOC` => `FRAGMENT_SHADER_CODE`
    """
    
    ###################
    # BEGIN CONFIGS
    ###################

    GLUT_DISPLAY = False

    MODELS_LOC = './models/'

    WIDTH = 600
    HEIGHT = 600

    REFRESH_TIMER = 1 # millisecs

    # UI defaults
    COLOR_DEFAULT = True
    WIREFRAME_DEFAULT = True

    # for UV objects
    MAX_U = 25
    MAX_V = 25

    # perspective frustum
    FOVY = 27.
    ZNEAR = 1
    ZFAR = 2000.

    # for camera transform
    EYE = (0,0,0)
    LOOKAT = (0,0,-15.)
    UP = (0.,1.,0.)

    # default shaders
    VERTEX_SHADER_LOC = 'basic.vert'
    FRAGMENT_SHADER_LOC = 'light.frag'

    CLEAR_COLOR = (.05, .05, .05, 1.)
    WIREFRAME_COLOR = (1,1,1,1)
    SOLID_COLOR = (1,.6,0,1)
