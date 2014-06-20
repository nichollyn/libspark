__author__ = 'kevin'

from PySide.QtCore import QObject

from _plugin2__iplugin_test__dev_ import easy_import_ as ei
if ei.initialized:
    from iplugin import IPlugin


class MyPlugin2(IPlugin):
    def __init__(self, manager):
        super(MyPlugin2, self).__init__(manager)
        self.initializeCalled = False

    def initialize(self, arguments):
        self.initializeCalled = True
        obj = QObject(self)
        obj.setObjectName("MyPlugin2")
        self.addAutoReleaseObject(obj)

        return True, "No error"

    def extensionsInitialized(self):
        if not self.initializeCalled:
            return
        obj = QObject(self)
        obj.setObjectName("MyPlugin2_running")
        self.addAutoReleaseObject(obj)




