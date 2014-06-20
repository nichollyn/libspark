__author__ = 'kevin'

from PySide.QtCore import QObject, QRect
from PySide.QtGui import QWidget, QApplication, \
    QPainter, QPalette, QStyleOption, QPixmapCache, QStyle


class StyledBar(QWidget):
    def __init__(self, parent):
        super(StyledBar, self).__init__(parent)
        self.setProperty("panelwidget", True)
        self.setProperty("panelwidget_singlerow", True)
        self.setProperty("lightColored", False)

    def setSingleRow(self, singleRow):
        self.setProperty("panelwidget_singlerow", singleRow)

    def isSingleRow(self):
        return self.property("panelwidget_singlerow")

    def setLightColored(self, lightColored):
        self.setProperty("lightColored", lightColored)

    def isLightColored(self):
        return self.property("lightColored")

    def paintEvent(self, event):
        painter = QPainter(self)
        option = QStyleOption()
        option.rect = self.rect()
        option.state = QStyle.State_Horizontal
        self.style().drawControl(QStyle.CE_ToolBar, option, painter, self)


class StyledSeparator(QWidget):
    def __init__(self, parent):
        super(StyledSeparator, self).__init__(parent)
        self.setFixedWidth(10)

    def paintEvent(self, event):
        painter = QPainter(self)
        option = QStyleOption()
        option.rect = self.rect()
        option.state = QStyle.State_Horizontal
        option.palette = self.palette()
        self.style().drawPrimitive(QStyle.PE_IndicatorToolBarSeparator, option, painter, self)






