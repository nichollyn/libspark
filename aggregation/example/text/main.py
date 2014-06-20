import sys

from PySide.QtGui import QWidget, QApplication, QMessageBox
from PySide.QtCore import Slot, QCoreApplication

from _text__libspark_aggregation__dev_ import easy_import_ as ei
from _text__libspark_aggregation__dev_.easy_import_ import PackageInfo as pkginfo

if ei.initialized:
    import aggregation
    from aggregation import Aggregate

from myinterfaces import IComboEntry, IText1, IText2, IText3
from ui_main import Ui_mainClass


class MyMain(QWidget):
    def __init__(self, parent=None, flags=0):
        super(MyMain, self).__init__(parent, flags)

        self.__ui = Ui_mainClass()
        self.__ui.setupUi(self)
        self.__ui.comboBox.currentIndexChanged.connect(self.select)

        self.__entries = []

    @Slot()
    def select(self, index):
        entry = self.__entries[index]
        t1 = aggregation.query(entry, IText1)
        t2 = aggregation.query(entry, IText2)
        t3 = aggregation.query(entry, IText3)

        self.__ui.text1.setText(t1.text if t1 is not None else self.tr("N/A"))
        self.__ui.text2.setText(t2.text if t2 is not None else self.tr("N/A"))
        self.__ui.text3.setText(t3.text if t3 is not None else self.tr("N/A"))
        self.__ui.text1.setEnabled(t1 is not None)
        self.__ui.text2.setEnabled(t2 is not None)
        self.__ui.text3.setEnabled(t3 is not None)

    def add(self, obj):
        self.__entries.append(obj)
        self.__ui.comboBox.addItem(obj.title)


def main():
    app = QApplication(sys.argv)
    if not ei.initialized:
        msg = QCoreApplication.translate(
            pkginfo.package_name,
            "Dependencies of '{0}' are not ready. \n\n".format(pkginfo.package_name) +
            "Test 'initialized' value in '_easy_import_' to find the reason.")
        QMessageBox.warning(None, pkginfo.package_name, msg)
        return sys.exit(app.exec_())

    window = MyMain()

    obj1 = IComboEntry("Entry without text")

    obj2 = Aggregate()
    combo_entry2 = IComboEntry("Entry with text2")
    combo_entry2.setObjectName("Combo Entry 2")
    obj2.add(combo_entry2)
    itext2 = IText2("This is a text for label 2")
    itext2.setObjectName("IText 2 (IText2)")
    obj2.add(itext2)

    obj3 = Aggregate()
    combo_entry3 = IComboEntry("Entry with text 1 and text 2")
    combo_entry3.setObjectName("Combo Entry 3")
    obj3.add(combo_entry3)
    itext31 = IText1("I love PySide!")
    itext31.setObjectName("IText 3 - 1 (IText1)")
    obj3.add(itext31)
    itext32 = IText2("There are software companies...")
    itext32.setObjectName("IText 3 - 2 (IText2)")
    obj3.add(itext32)

    obj4 = Aggregate()
    combo_entry4 = IComboEntry("Entry with text 1 and text 3")
    combo_entry4.setObjectName("Combo Entry 4")
    obj4.add(combo_entry4)
    itext41 = IText1("Some text written here.")
    itext41.setObjectName("IText 4 - 1 (IText1)")
    obj4.add(itext41)
    itext42 = IText3("I'm a troll.")
    itext42.setObjectName("IText 4 -2 (IText3")
    obj4.add(itext42)

    # the API takes IComboEntries, so we convert them to it
    # the MyMain objects takes the ownership of the whole aggregations
    window.add(aggregation.query(obj1, IComboEntry))
    window.add(aggregation.query(obj2, IComboEntry))
    window.add(aggregation.query(obj3, IComboEntry))
    window.add(aggregation.query(obj4, IComboEntry))
    window.show()

    app.exec_()


if __name__ == "__main__":
    main()