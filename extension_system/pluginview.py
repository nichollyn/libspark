__author__ = 'kevin'

from PySide.QtGui import QWidget, QHeaderView, QIcon, QTreeWidgetItem
from PySide.QtCore import Signal, Slot, \
    Qt, QDir

from pluginmanager import PluginManager
from pluginspec import PluginSpec, PluginState
from _extension_system__libspark__dev_.dev_log_ import Log

from pluginview_ui import Ui_PluginView


TAG = "PluginView"


class ParsedState(object):
    ParsedNone = 1
    ParsedPartial = 2
    ParsedAll = 4
    ParsedWithErrors = 8

    def __init__(self):
        super(ParsedState, self).__init__()


C_LOAD = 1


class PluginView(QWidget):
    currentPluginChanged = Signal(PluginSpec)
    pluginActivated = Signal(PluginSpec)
    pluginSettingsChanged = Signal(PluginSpec)

    def __init__(self, manager, parent=None):
        super(PluginView, self).__init__(parent)

        self.private = PluginViewPrivate()
        self.allowCheckStateUpdate = True

        self.items = []
        self.specToItem = {}

        self.ui = Ui_PluginView()
        self.ui.setupUi(self)

        self.header = self.ui.categoryWidget.header()
        self.header.setResizeMode(0, QHeaderView.ResizeToContents)
        self.header.setResizeMode(2, QHeaderView.ResizeToContents)

        self.okIcon = QIcon(":/extensionsystem/images/ok.png")
        self.errorIcon = QIcon(":/extensionsystem/images/error.png")
        self.notLoadedIcon = QIcon(":/extension/images/notloaded.png")

        self.ui.categoryWidget.setColumnWidth(C_LOAD, 40)

        # Can not disable these
        self.whitelist = list("Core")

        self.private.manager = manager

        self.private.manager.pluginsChanged.connect(self.updateList)
        self.ui.categoryWidget.currentItemChanged.connect(self.selectPlugin)
        self.ui.categoryWidget.itemActivated.connect(self.activatePlugin)

        self.updateList()

    def currentPlugin(self):
        if not self.ui.categoryWidget.currentItem():
            return None
        if self.ui.categoryWidget.currentItem().data(0, Qt.UserRole):
            return self.ui.categoryWidget.currentItem().data(0, Qt.UserRole)
        return None

    @Slot()
    def updatePluginSettings(self, item, column):
        if not self.allowCheckStateUpdate:
            return
        self.allowCheckStateUpdate = False
        loadOnStartup = bool(item.data(C_LOAD, Qt.CheckStateRole))

        if isinstance(item.data(0, Qt.UserRole), PluginSpec):
            spec = item.data(0, Qt.UserRole)

            if column == C_LOAD:
                spec.setEnabled(loadOnStartup)
                self.updatePluginDependencies()
                if item.parent():
                    pluginCollection = item.parent().data(0, Qt.UserRole)
                    state = Qt.PartiallyChecked
                    loadCount = 0
                    for plugin in pluginCollection.plugins():
                        if plugin.isEnabled():
                            loadCount += 1
                    if loadCount == len(pluginCollection.plugins()):
                        state = Qt.Checked
                    elif loadCount == 0:
                        state = Qt.Unchecked
                    item.parent().setData(C_LOAD, Qt.CheckStateRole, state)

                self.pluginSettingsChanged.emit(spec)
        else:
            pluginCollection = item.data(0, Qt.UserRole)
            for plugin in pluginCollection.plugins:
                child = self.specToItem[plugin]

                if plugin.name() not in self.whitelist:
                    plugin.setEnabled(loadOnStartup)
                    state = Qt.Checked if loadOnStartup else Qt.Unchecked
                    child.setData(C_LOAD, Qt.CheckStateRole, state)
                else:
                    child.setData(C_LOAD, Qt.CheckStateRole, Qt.Checked)
                    child.setFlags(Qt.ItemIsSelectable)
            self.updatePluginDependencies()
            self.pluginSettingsChanged.emit(pluginCollection.plugins[0])

        self.allowCheckStateUpdate = True

    @Slot()
    def updateList(self):
        self.ui.categoryWidget.itemChanged.connect(self.updatePluginSettings)
        defaultCollection = None
        for pluginCollection in self.private.manager.pluginCollections().values():
            if not pluginCollection.name:
                defaultCollection = pluginCollection
                continue
            collectionItem = QTreeWidgetItem([pluginCollection.name(), "", "", "", ""])
            self.items.append(collectionItem)

            state, groupState = self.parsePluginSpecs(collectionItem, pluginCollection.plugins())

            collectionItem.setIcon(0, self.iconForState(state))
            collectionItem.setData(C_LOAD, Qt.CheckStateRole, groupState)
            collectionItem.setToolTip(C_LOAD, "Load on Startup")
            collectionItem.setData(0, Qt.UserRole, pluginCollection)
        # add all non-categorized plugins into utilities. could also be added as root items
        # but that makes the tree ugly
        defaultCollectionItem = QTreeWidgetItem(["Utilities", "", "", "", ""])
        self.items.append(defaultCollectionItem)
        state, groupState = self.parsePluginSpecs(defaultCollectionItem, defaultCollection.plugins)
        defaultCollectionItem.setIcon(0, self.iconForState(state))
        defaultCollectionItem.setData(C_LOAD, Qt.CheckStateRole, groupState)
        defaultCollectionItem.setToolTip(C_LOAD, "Load on Startup")
        defaultCollectionItem.setData(0, Qt.UserRole, defaultCollection)

        self.updatePluginDependencies()
        self.ui.categoryWidget.clear()
        if self.items:
            self.ui.categoryWidget.addTopLevelItems(self.items)
            self.ui.categoryWidget.expandAll()
        self.ui.categoryWidget.sortItems(0, Qt.AscendingOrder)
        if self.ui.categoryWidget.topLevelItemCount():
            self.ui.categoryWidget.setCurrentItem(self.ui.categoryWidget.topLevelItem(0))

    @Slot()
    def selectPlugin(self, current):
        if not current:
            self.currentPluginChanged.emit(0)
        elif isinstance(current.data(0, Qt.UserRole), PluginSpec):
            self.currentPluginChanged.emit(current.data(0, Qt.UserRole))
        else:
            self.currentPluginChanged.emit(0)

    @Slot()
    def activatePlugin(self, item):
        if isinstance(item.data(0, Qt.UserRole), PluginSpec):
            self.pluginActivated.emit(item.data(0, Qt.UserRole))
        else:
            self.pluginActivated.emit(0)

    def iconForState(self, state):
        if state & ParsedState.ParsedWithErrors:
            return self.errorIcon

        if state & ParsedState.ParsedNone or state & ParsedState.ParsedPartial:
            return self.notLoadedIcon

        return self.okIcon

    def updatePluginDependencies(self):
        for spec in PluginManager.getInstance().loadQueue():
            disableIndirectly = False
            if spec.name() in self.whitelist:
                continue
            for depSpec in spec.dependencySpecs():
                if not depSpec.isEnabled() or depSpec.isDisabledIndirectly():
                    disableIndirectly = True
                    break
            childItem = self.specToItem[spec]
            childItem.setDisabled(disableIndirectly)

            if disableIndirectly == spec.isDisabledIndirectly():
                continue
            spec.setDisabledIndirectly(disableIndirectly)

            if childItem.parent() and not childItem.parent().isExpanded():
                childItem.parent().setExpanded(True)

    def parsePluginSpecs(self, parentItem, plugins):
        ret = 0
        loadCount = 0

        for i in range(len(plugins)):
            spec = plugins[i]
            if spec.hasError():
                ret |= ParsedState.ParsedWithErrors
            pluginItem = QTreeWidgetItem([spec.name(), "",
                                         "{0} ({1})".format(spec.version(), spec.compatVersion()),
                                         spec.vendor()])
            pluginItem.setToolTip(0, QDir.toNativeSeparators(spec.filePath()))
            ok = not spec.hasError()
            icon = self.okIcon if ok else self.errorIcon
            if ok and spec.state() is not PluginState.Running:
                icon = self.notLoadedIcon
            pluginItem.setIcon(0, icon)
            pluginItem.setData(0, Qt.UserRole, spec)

            state = Qt.Unchecked
            if spec.isEnabled():
                state = Qt.Checked
                loadCount += 1

            if spec.name() not in self.whitelist:
                pluginItem.setData(C_LOAD, Qt.CheckStateRole, state)
            else:
                pluginItem.setData(C_LOAD, Qt.CheckStateRole, Qt.Checked)
                pluginItem.setFlags(Qt.ItemIsSelectable)
            pluginItem.setToolTip(C_LOAD, "Load on Startup")

            self.specToItem[spec] = pluginItem

            if parentItem:
                parentItem.addChild(pluginItem)
            else:
                self.items.append(pluginItem)

        if loadCount == len(plugins):
            groupState = Qt.Checked
            ret |= ParsedState.ParsedAll
        elif loadCount == 0:
            groupState = Qt.Unchecked
            ret |= ParsedState.ParsedNone
        else:
            groupState = Qt.PartiallyChecked
            ret |= ParsedState.ParsedPartial

        return ret, groupState


class PluginViewPrivate(object):
    def __init__(self):
        super(PluginViewPrivate, self).__init__()
        self.manager = None
