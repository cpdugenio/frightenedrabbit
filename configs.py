class Singleton(type):
    """
    Singleton metaclass

    Notes
    -----
    To make a class a `Singleton`, set `__metaclass__ = Singleton` and call.

    ```
    class Global(Object):
        __metaclass__ = Singleton

    mySingleton = Global()
    sameSingleton = Global()
    assert mySingleton == sameSingleton
    ```
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Call your singleton class to get.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args)
        return cls._instances[cls]


class Global(object):
    """
    Singleton Global class used for configs

    Notes
    -----
    On `self.__init__()`, shaders are pulled from files and placed into their respective vars:
        `VERTEX_SHADER_LOC` => `VERTEX_SHADER_CODE`
        `FRAGMENT_SHADER_LOC` => `FRAGMENT_SHADER_CODE`
    """
    
    __metaclass__ = Singleton

    ###################
    # BEGIN CONFIGS
    ###################

    GLUT_DISPLAY = False

    MODELS_LOC = './models/'

    WIDTH = 600
    HEIGHT = 600

    REFRESH_TIMER = 1 # millisecs

    # UI defaults
    COLOR_DEFAULT = False
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
    VERTEX_SHADER_LOC = 'vertex.glsl'
    FRAGMENT_SHADER_LOC = 'fragment.glsl'

    CLEAR_COLOR = (.05, .05, .05, 1.)
    WIREFRAME_COLOR = (1,1,1,1)
    SOLID_COLOR = (1,.6,0,1)

    def __init__(self):
        pass
