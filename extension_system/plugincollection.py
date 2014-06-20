class PluginCollection(object):
    def __init__(self, name):
        super(PluginCollection, self).__init__()
        self.__name = name
        self.__plugins = []

    @property
    def name(self):
        return self.__name

    @property
    def plugins(self):
        return self.__plugins

    def addPlugin(self, spec):
        self.__plugins.append(spec)

    def removePlugin(self, spec):
        self.__plugins.remove(spec)
