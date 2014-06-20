from PySide.QtCore import QObject


class IComboEntry(QObject):
    def __init__(self, title):
        super(IComboEntry, self).__init__()
        self._title = title

    @property
    def title(self):
        return self._title


class IText1(QObject):
    def __init__(self, text):
        super(IText1, self).__init__()
        self._text = text

    @property
    def text(self):
        return self._text


class IText2(QObject):
    def __init__(self, text):
        super(IText2, self).__init__()
        self._text = text

    @property
    def text(self):
        return self._text


class IText3(QObject):
    def __init__(self, text):
        super(IText3, self).__init__()
        self._text = text

    @property
    def text(self):
        return self._text

