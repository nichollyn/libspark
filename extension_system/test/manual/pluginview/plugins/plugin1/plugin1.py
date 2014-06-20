__author__ = 'kevin'

from PySide.QtCore import QObject

from _plugin1__iplugin_test__dev_ import easy_import_ as ei
if ei.initialized:
    from iplugin import IPlugin
    from pluginmanager import PluginManager
    

class MyPlugin1(IPlugin):
    def __init__(self, manager):
        super(MyPlugin1, self).__init__(manager)
        self.initializeCalled = False

    def initialize(self, arguments):
        self.initializeCalled = False
        obj = QObject(self)
        obj.setObjectName("MyPlugin1")
        self.addAutoReleaseObject(obj)

        found2 = False
        found3 = False
        for otherPluginObj in PluginManager.getInstance().allObjects():
            if otherPluginObj.objectName() == "MyPlugin2":
                found2 = True
            elif otherPluginObj.objectName() == "MyPlugin3":
                found3 = True
        if found2 and found3:
            return True, "No error"

        errorString = "object(s) missing from plugin(s):"
        if not found2:
            errorString += "plugin2"
        if not found3:
            errorString += "plugin3"
        return False, errorString

    def extensionsInitialized(self):
        if not self.initializeCalled:
            return
        obj = QObject(self)
        obj.setObjectName("MyPlugin1_running")
        self.addAutoReleaseObject(obj)




