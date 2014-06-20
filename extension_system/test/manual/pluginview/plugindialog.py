__author__ = 'kevin'

import sys

from PySide.QtGui import QApplication, QWidget, \
    QPushButton, QVBoxLayout, QHBoxLayout
from PySide.QtCore import Slot

from _pluginview__extension_system_test__dev_ import easy_import_ as ei
if ei.initialized:
    from pluginmanager import PluginManager
    from pluginview import PluginView


class PluginDialog(QWidget):
    def __init__(self, pluginManager):
        super(PluginDialog, self).__init__()

        self.view = PluginView(pluginManager, self)

        self.vbLayout = QVBoxLayout(self)
        self.vbLayout.setContentsMargins(0, 0, 0, 0)
        self.vbLayout.setSpacing(0)
        self.vbLayout.addWidget(self.view)

        self.hbLayout = QHBoxLayout()
        self.vbLayout.addLayout(self.hbLayout)
        self.hbLayout.setContentsMargins(0, 0, 0, 0)
        self.hbLayout.setSpacing(6)

        self.detailsButton = QPushButton("Details", self)
        self.errorDetailsButton = QPushButton("Error Details", self)
        self.detailsButton.setEnabled(False)
        self.errorDetailsButton.setEnabled(False)

        self.hbLayout.addWidget(self.detailsButton)
        self.hbLayout.addWidget(self.errorDetailsButton)
        self.hbLayout.addStretch(5)

        self.resize(650, 300)
        self.setWindowTitle("Installed Plugins")

        self.view.currentPluginChanged.connect(self.updateButtons)
        self.view.pluginActivated.connect(self.openDetails)
        self.detailsButton.clicked.connect(self.openDetails)
        self.errorDetailsButton.clicked.connect(self.openErrorDetails)

    @Slot()
    def updateButtons(self):
        # todo
        pass

    @Slot()
    def openDetails(self):
        # todo
        pass

    @Slot()
    def openDetails(self, spec):
        # todo
        print("TODO open details")
        pass

    @Slot()
    def openErrorDetails(self):
        # todo
        pass


def main():
    manager = PluginManager()
    manager.setPluginPaths(["plugins"])
    manager.loadPlugins()
    app = QApplication(sys.argv)

    dialog = PluginDialog(manager)

    dialog.show()
    app.exec_()

if __name__ == "__main__":
    main()