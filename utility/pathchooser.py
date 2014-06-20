__author__ = 'kevin'

from PySide.QtGui import QWidget, QHBoxLayout
from PySide.QtCore import Signal, Slot

from basevalidatinglineedit import BaseValidatingLineEdit


class PathKind(object):
    Directory, File, Command = range(3)

    def __init__(self):
        pass


class PathValidatingLineEdit(BaseValidatingLineEdit):
    def __init__(self, chooser, parent=None):
        super(PathValidatingLineEdit, self).__init__(parent)
        self.chooser = chooser

    def validate(self, value):
        return self.chooser.validatePath(value)


class PathChooserPrivate(object):
    def __init__(self, chooser):
        super(PathChooserPrivate, self).__init__()
        self.hLayout = QHBoxLayout()
        self.lineEdit = PathValidatingLineEdit(chooser)
        self.acceptingKind = PathKind.Directory
        self.dialogTitleOverride = ""
        self.dialogFilter = ""
        self.initialBrowsePathOverride = ""


class PathChooser(QWidget):
    validChanged = Signal((), (bool,))
    changed = Signal(str)
    editingFinished = Signal()
    beforeBrowsing = Signal()
    browsingFinished = Signal()
    returnPressed = Signal()

    def __init__(self, parent=None):
        super(PathChooser, self).__init__(parent)
        self.private = PathChooserPrivate(self)
        self.private.hLayout.setContentsMargins(0, 0, 0, 0)
        self.private.lineEdit.validReturnPressed.connect(Signal(self.returnPressed))
        self.private.lineEdit.textChanged.connect(self.changed)
        self.private.lineEdit.validChanged.connect(self.validChanged)
        self.private.lineEdit.validChanged[bool].connect(self.validChanged[bool])


    @Slot(str)
    def setPath(self, path):
        # todo
        pass

    @Slot()
    def slotBrowse(self):
        # todo
        pass



