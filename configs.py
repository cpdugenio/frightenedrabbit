class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args)
        return cls._instances[cls]


class Global(object):
    __metaclass__ = Singleton

    WIDTH = 600
    HEIGHT = 600

    FOVY = 27.
    ZNEAR = 1
    ZFAR = 2000.

    EYE = (10,10,1)
    LOOKAT = (0,0,-15.)
    UP = (0.,1.,0.)

    VERTEX_SHADER_CODE = """
    uniform mat4 projection;
    uniform mat4 view;
    uniform mat4 model;

    attribute vec4 colorx;
    attribute vec3 position;
    varying vec4 v_color;
    void main()
    {
        gl_Position = projection * view * model * vec4(position, 1.0);
        v_color = colorx;
    } """


    FRAGMENT_SHADER_CODE = """
    varying vec4 v_color;
    void main()
    {
        //gl_FragColor = vec4(1.0,1.0,1.0,1.0);
        gl_FragColor = v_color;
    }
    """

    def __init__(self):
        pass
