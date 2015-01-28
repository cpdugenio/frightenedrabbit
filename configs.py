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

    WIDTH = 1600
    HEIGHT = 800

    REFRESH_TIMER = 1 # millisecs

    # UI defaults
    COLOR_DEFAULT = True
    WIREFRAME_DEFAULT = True

    # for UV objects
    MAX_U = 100
    MAX_V = 100

    # perspective frustum
    FOVY = 27.
    ZNEAR = 1
    ZFAR = 2000.

    # for camera transform
    EYE = (0,0,25)
    LOOKAT = (0,0,-15.)
    UP = (0.,1.,0.)

    LIGHTS = [
        # (ambient, diffuse, specular, position)
        ((0,0,.15,1), (0.1,0.3,1.0,1), (1,1,1,1), (0,0,40,1)),
        ((0,.15,0,1), (0.2,.4,.1,1), (1,1,1,1), (0,40,0,1)),
        ((.25,0,0,1), (0.4,.2,.1,1), (1,1,1,1), (-40,0,0,1)),
        ((0,0,0,1), (.7,.7,.7,1), (1,1,1,1), (0,-15,-100,1)),
        ((0,0,0,1), (1,1,1,1), (1,1,1,1), (0,15,-100,1)),
    ]

    # default shaders
    VERTEX_SHADER_LOC = 'shaders/basic.vert'
    FRAGMENT_SHADER_LOC = 'shaders/light.frag'

    CLEAR_COLOR = (.05, .05, .05, 1.)
    WIREFRAME_COLOR = (1,1,1,1)
    SOLID_COLOR = (.5,.5,.5,1)
