from PySide.QtCore import QObject

from _extension_system__libspark__dev_ import interface_util_ as interface


class IPluginPrivate(object):
    def __init__(self):
        self.pluginSpec = None
        self.addedObjectsInReverseOrder = []


class IPlugin(QObject):

    def __init__(self, pluginManager):
        super(IPlugin, self).__init__()
        self.private = IPluginPrivate()
        self.manager = pluginManager

    def initialize(self, arguments):
        """ Initialize the plugin
            Must return a truth value to indicate if the initialization succeed
            and an error string about the failed reason
        """
        interface.raiseMethodNotOverwrittenError(self, "IPlugin", "initialize")

    def extensionsInitialized(self):
        # todo: docstring
        """
        Docstring stub
        """
        interface.raiseMethodNotOverwrittenError(self, "IPlugin", "extensionsInitialized")

    def aboutToShutdown(self):
        # todo: docstring
        """
        Docstring stub
        """
        pass

    def remoteCommand(self, options, arguments):
        # todo: docstring
        """
        Docstring stub
        """
        pass

    def pluginSpec(self):
        return self.private.pluginSpec

    def addObject(self, obj):
        self.manager.addObject(obj)

    def addAutoReleaseObject(self, obj):
        self.private.addedObjectsInReverseOrder.insert(0, obj)
        self.manager.addObject(obj)

    def removeObject(self, obj):
        self.manager.removeObject(obj)