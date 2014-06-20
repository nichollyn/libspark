__author__ = 'kevin'

from PySide.QtGui import QLineEdit, QPalette
from PySide.QtCore import Signal, Slot, Qt

from _utility__libspark_dev_ import interface_util_ as interface


TAG = "BaseValidatingLineEdit"


class EditState(object):
    Invalid, DisplayingInitialText, Valid = range(3)


class BaseValidatingLineEditPrivate(object):
    def __init__(self, widget):
        super(BaseValidatingLineEditPrivate, self).__init__()
        self.okTextColor = BaseValidatingLineEdit.textColor(widget)
        self.errorTextColor = Qt.red
        self.state = EditState.Invalid
        self.firstChange = True
        self.errorMessage = ""
        self.initialText = ""


class BaseValidatingLineEdit(QLineEdit):
    validChanged = Signal((), (bool,))
    validReturnPressed = Signal()

    def __init__(self, parent=None):
        super(BaseValidatingLineEdit, self).__init__(parent)
        self.private = BaseValidatingLineEditPrivate(self)
        self.textChanged.connect(self.slotChanged)

    @property
    def initialText(self):
        return self.private.initialText

    @initialText.setter
    def initialText(self, text):
        if self.private.initialText != text:
            self.private.initialText = text
            self.private.firstChange = True
            self.setText(text)

    @property
    def errorColor(self):
        return self.private.errorColor

    @errorColor.setter
    def errorColor(self, color):
        self.private.errorColor = color

    def state(self):
        return self.private.state

    def isValid(self):
        return self.private.state == EditState.Valid

    def errorMessage(self):
        return self.private.errorMessage

    def triggerChanged(self):
        self.slotChanged(self.text())

    @staticmethod
    def textColor(widget):
        return widget.palette().color(QPalette.Active, QPalette.Text)

    @staticmethod
    def setTextColor(widget, color):
        palette = widget.palette()
        palette.setColor(QPalette.Active, QPalette.Text, color)
        widget.setPalette(palette)

    def validate(self, value):
        interface.raiseMethodNotOverwrittenError(self, TAG, "validate")

    @Slot()
    def slotReturnPressed(self):
        if self.isValid():
            self.validReturnPressed.emit()

    @Slot()
    def slotChanged(self, text):
        self.private.errorMessage = ""
        # Are we displaying the initial text?
        isDisplayingInitialText = not self.private.initialText and text == self.private.initialText
        if isDisplayingInitialText:
            newState = EditState.DisplayingInitialText
        else:
            if self.validate(text, self.private.errorMessage):
                newState = EditState.Valid
            else:
                newState = EditState.Invalid
        self.setToolTip(self.private.errorMessage)

        if newState != self.private.state or self.private.firstChange:
            validHasChanged = ((self.state() == EditState.Valid) != (newState == EditState.Valid))
            self.private.state = newState
            self.private.firstChange = False
            if newState == EditState.Invalid:
                self.setTextColor(self, self.private.errorTextColor)
            else:
                self.setTextColor(self, self.private.okTextColor)
            if validHasChanged:
                self.validChanged[bool].emit(newState == EditState.Valid)
                self.validChanged.emit()