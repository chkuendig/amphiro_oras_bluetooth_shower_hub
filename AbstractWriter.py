import abc

class AbstractWriter(object):
    __metaclass__ = abc.ABCMeta

    # All sensors can receive configurations as constructor.
    @abc.abstractmethod
    def __init__(self, Config):
        pass

    # Write data to writers target
    # This is abstract method that inheriting classes must implement
    @abc.abstractmethod
    def write(self, dataDict, rawData1, rawData2 ):
        pass

