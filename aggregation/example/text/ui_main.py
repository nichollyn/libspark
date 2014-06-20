# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Fri Apr  4 14:45:04 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_mainClass(object):
    def setupUi(self, mainClass):
        mainClass.setObjectName("mainClass")
        mainClass.resize(399, 176)
        self.vboxlayout = QtGui.QVBoxLayout(mainClass)
        self.vboxlayout.setObjectName("vboxlayout")
        self.comboBox = QtGui.QComboBox(mainClass)
        self.comboBox.setObjectName("comboBox")
        self.vboxlayout.addWidget(self.comboBox)
        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setObjectName("vboxlayout1")
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")
        self.label = QtGui.QLabel(mainClass)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.hboxlayout.addWidget(self.label)
        self.text1 = QtGui.QLabel(mainClass)
        self.text1.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text1.sizePolicy().hasHeightForWidth())
        self.text1.setSizePolicy(sizePolicy)
        self.text1.setObjectName("text1")
        self.hboxlayout.addWidget(self.text1)
        self.vboxlayout1.addLayout(self.hboxlayout)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")
        self.label_3 = QtGui.QLabel(mainClass)
        self.label_3.setObjectName("label_3")
        self.hboxlayout1.addWidget(self.label_3)
        self.text2 = QtGui.QLabel(mainClass)
        self.text2.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text2.sizePolicy().hasHeightForWidth())
        self.text2.setSizePolicy(sizePolicy)
        self.text2.setObjectName("text2")
        self.hboxlayout1.addWidget(self.text2)
        self.vboxlayout1.addLayout(self.hboxlayout1)
        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setObjectName("hboxlayout2")
        self.label_5 = QtGui.QLabel(mainClass)
        self.label_5.setObjectName("label_5")
        self.hboxlayout2.addWidget(self.label_5)
        self.text3 = QtGui.QLabel(mainClass)
        self.text3.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text3.sizePolicy().hasHeightForWidth())
        self.text3.setSizePolicy(sizePolicy)
        self.text3.setObjectName("text3")
        self.hboxlayout2.addWidget(self.text3)
        self.vboxlayout1.addLayout(self.hboxlayout2)
        self.vboxlayout.addLayout(self.vboxlayout1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem)

        self.retranslateUi(mainClass)
        QtCore.QMetaObject.connectSlotsByName(mainClass)

    def retranslateUi(self, mainClass):
        mainClass.setWindowTitle(QtGui.QApplication.translate("mainClass", "main", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("mainClass", "Text1:", None, QtGui.QApplication.UnicodeUTF8))
        self.text1.setText(QtGui.QApplication.translate("mainClass", "N/A", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("mainClass", "Text2:", None, QtGui.QApplication.UnicodeUTF8))
        self.text2.setText(QtGui.QApplication.translate("mainClass", "N/A", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("mainClass", "Text3:", None, QtGui.QApplication.UnicodeUTF8))
        self.text3.setText(QtGui.QApplication.translate("mainClass", "N/A", None, QtGui.QApplication.UnicodeUTF8))

