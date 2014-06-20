# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pluginview.ui'
#
# Created: Tue Apr 15 16:04:23 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui


class Ui_PluginView(object):
    def setupUi(self, PluginView):
        PluginView.setObjectName("PluginView")
        PluginView.resize(773, 304)
        self.gridLayout = QtGui.QGridLayout(PluginView)
        self.gridLayout.setContentsMargins(2, 2, 2, 2)
        self.gridLayout.setObjectName("gridLayout")
        self.categoryWidget = QtGui.QTreeWidget(PluginView)
        self.categoryWidget.setAlternatingRowColors(True)
        self.categoryWidget.setIndentation(20)
        self.categoryWidget.setRootIsDecorated(True)
        self.categoryWidget.setUniformRowHeights(False)
        self.categoryWidget.setItemsExpandable(True)
        self.categoryWidget.setColumnCount(4)
        self.categoryWidget.setObjectName("categoryWidget")
        self.categoryWidget.header().setDefaultSectionSize(120)
        self.categoryWidget.header().setHighlightSections(False)
        self.categoryWidget.header().setMinimumSectionSize(35)
        self.gridLayout.addWidget(self.categoryWidget, 1, 0, 1, 1)

        self.retranslateUi(PluginView)
        QtCore.QMetaObject.connectSlotsByName(PluginView)

    def retranslateUi(self, PluginView):
        self.categoryWidget.setSortingEnabled(True)
        self.categoryWidget.headerItem().setText(0, QtGui.QApplication.translate("PluginView", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.categoryWidget.headerItem().setText(1, QtGui.QApplication.translate("PluginView", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.categoryWidget.headerItem().setText(2, QtGui.QApplication.translate("PluginView", "Version", None, QtGui.QApplication.UnicodeUTF8))
        self.categoryWidget.headerItem().setText(3, QtGui.QApplication.translate("PluginView", "Vendor", None, QtGui.QApplication.UnicodeUTF8))

