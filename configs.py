class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args)
        return cls._instances[cls]


class Global(object):
    __metaclass__ = Singleton

    WIDTH = 500
    HEIGHT = 500

    def __init__(self):
        pass
