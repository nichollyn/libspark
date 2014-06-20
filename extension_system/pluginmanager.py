from PySide.QtCore import QObject, \
    QWriteLocker, QReadLocker, QReadWriteLock, \
    qWarning, \
    Signal, Slot, \
    QFileInfo, QDir, \
    QSettings

from pluginspec import PluginSpec, PluginState
from plugincollection import PluginCollection
from optionsparser import OptionsParser

from _extension_system__libspark__dev_ import easy_import_ as ei
if ei.initialized:
    from aggregation import aggregation
from _extension_system__libspark__dev_.easy_import_ import BColors
from _extension_system__libspark__dev_.dev_log_ import Log


TAG = "PluginManager"

def indentTextStream(textStream, indentLen):
    blank = ' '
    for i in range(indentLen):
        textStream << blank


def formatOptions(textStream, opt, param, description, optionIndentation, descriptionIndentation):
    remainingIndent = descriptionIndentation - optionIndentation - len(opt)
    indentTextStream(textStream, optionIndentation)
    textStream << opt
    if param:
        textStream << " <" << param << '>'
        remainingIndent -= 3 + len(param)
    indentTextStream(textStream, max(1, remainingIndent))
    textStream << description << '\n'


ARGUMENT_KEYWORD = ":arguments"
IGNORED_PLUGINS = "Plugins/Ignored"
FORCEENABLED_PLUGINS = "Plugins/ForceEnabled"


class PluginManager(QObject):
    objectAdded = Signal(QObject)
    aboutToRemoveObject = Signal(QObject)
    pluginsChanged = Signal()

    @staticmethod
    def getInstance():
        if not hasattr(PluginManager.getInstance, "instance"):
            PluginManager.getInstance.instance = PluginManager()

        return PluginManager.getInstance.instance

    def __init__(self):
        super(PluginManager, self).__init__()
        self.private = PluginManagerPrivate(self)
        self.lock = QReadWriteLock()

    @Slot()
    def remoteArguments(self, serializedArgument):
        # todo
        pass

    @Slot()
    def __startTests(self):
        # todo
        pass

    def addObject(self, obj):
        self.private.addObject(obj)

    def removeObject(self, obj):
        self.private.removeObject(obj)

    def allObjects(self):
        return self.private.allObjects

    def getObjects(self, classinfo):
        QReadLocker(self.lock)
        results = []
        allObjects = self.allObjects()
        for obj in allObjects:
            result = aggregation.query_all(obj, classinfo)
            if result:
                results.append(result)

        return results

    def getObject(self, classinfo):
        QReadLocker(self.lock)
        allObjects = self.allObjects()
        result = None
        for obj in allObjects:
            result = aggregation.query(obj, classinfo)
            if result:
                break

        return result

    def loadQueue(self):
        return self.private.loadQueue()

    def loadPlugins(self):
        return self.private.loadPlugins()

    def pluginPaths(self):
        return self.private.pluginPaths

    def setPluginPaths(self, paths):
        self.private.setPluginPaths(paths)

    def plugins(self):
        return self.private.pluginSpecs

    def pluginCollections(self):
        return self.private.pluginCategories

    def fileExtension(self):
        return self.private.extension

    def setFileExtension(self, extension):
        self.private.extension = extension

    def loadSettings(self):
        self.private.loadSettings()

    def writeSettings(self):
        self.private.writeSettings()

    def arguments(self):
        return self.private.arguments

    def parseOptions(self, args, appOptions, foundAppOptions):
        options = OptionsParser(args, appOptions, foundAppOptions, self.private)
        return options.parse()

    @staticmethod
    def formatOptions(textStream, optionIndentation, descriptionIndentation):
        formatOptions(textStream, OptionsParser.NO_LOAD_OPTION,
                      "plugin", "Do not load <plugin>",
                      optionIndentation, descriptionIndentation)
        formatOptions(textStream, OptionsParser.PROFILE_OPTION,
                      "", "Profile plugin loading",
                      optionIndentation, descriptionIndentation)

    def formatPluginOptions(self, textStream, optionIndentation, descriptionIndentation):
        # todo
        pass

    def formatPluginVersions(self, textStream):
        # todo
        pass

    def serializedArguments(self):
        seperator = '|'
        rc = ""
        for spec in self.plugins():
            if spec.arguments():
                if rc:
                    rc += seperator
                rc += ':'
                rc += spec.name()
                rc += seperator
                rc += (spec.arguments() + seperator)
        if self.private.arguments:
            if rc:
                rc += seperator
            rc += ARGUMENT_KEYWORD
            # If the argument appears to be a file, make it absolute
            # when sending to another instance
            for argument in self.private.arguments:
                rc += seperator
                fi = QFileInfo(argument)
                if fi.exists() and fi.isRelative():
                    rc += fi.absoluteFilePath()
                else:
                    rc += argument
        return rc

    def runningTests(self):
        # todo
        pass

    def profilingReport(self, what, spec):
        # todo
        pass


class PluginManagerPrivate(object):
    def __init__(self, pluginManager):
        super(PluginManagerPrivate, self).__init__()
        self.pluginManager = pluginManager
        self.extension = "xml"
        self.profileElapsedMS = 0
        self.profilingVerbosity = 0
        self.pluginCategories = {}
        self.pluginSpecs = []
        self.testSpecs = []
        self.pluginPaths = []
        self.allObjects = []
        self.disabledPlugins = []
        self.forceEnabledPlugins = []
        self.arguments = []
        self.defaultCollection = None

    @staticmethod
    def createSpec():
        return PluginSpec()

    @staticmethod
    def privateSpec(spec):
        return spec.private

    def addObject(self, obj):
        QWriteLocker(self.pluginManager.lock)
        if not obj:
            qWarning("PluginManagerPrivate.addObject(): trying to add None object")
            return
        if obj in self.allObjects:
            qWarning("PluginManagerPrivate.addObject(): trying to add duplicate object")
            return

        self.allObjects.append(obj)

    def removeObject(self, obj):
        if not obj:
            qWarning("PluginManagerPrivate.removeObject(): trying to remove null object")
            return
        if obj not in self.allObjects:
            qWarning(("PluginManagerPrivate.removeObject(): object not in list: " + obj.objectName()))
            return
        self.pluginManager.aboutToRemoveObject.emit(obj)
        QWriteLocker(self.pluginManager.lock)
        self.allObjects[:] = []

    def loadPlugins(self):
        queue = self.loadQueue()
        for spec in queue:
            self.loadPlugin(spec, PluginState.Loaded)
        for spec in queue:
            self.loadPlugin(spec, PluginState.Initialized)
        for item in reversed(queue):
            self.loadPlugin(item, PluginState.Running)
        self.pluginManager.pluginsChanged.emit()

    def setPluginPaths(self, paths):
        self.pluginPaths = paths
        self.loadSettings()
        self.__readPluginPaths()

    def loadQueue(self):
        queue = []
        for spec in self.pluginSpecs:
            circularityCheckQueue = []
            self.__loadQueue(spec, queue, circularityCheckQueue)
        return queue

    def loadPlugin(self, spec, destState):
        if spec.hasError() or spec.state() != destState-1:
            return None
        # don't load disabled plugins
        if (spec.isDisabledIndirectly() or not spec.isEnabled()) \
           and destState == PluginState.Loaded:
            return
        if destState == PluginState.Running:
            self.profilingReport(">initializeExtensions", spec)
            spec.private.initializeExtensions()
            self.profilingReport("<initializeExtensions", spec)
            return
        elif destState == PluginState.Deleted:
            spec.private.kill()
            return

        for depSpec in spec.dependencySpecs():
            if depSpec.state() != destState:
                spec.private.hasError = True
                spec.private.errorString = "Cannot load plugin because dependency failed to load: " \
                                           "{name}({ver})\nReason: {err}".format(
                                               name=depSpec.name(), ver=depSpec.version(),
                                               err=depSpec.errorString())
                return
        if destState == PluginState.Loaded:
            self.profilingReport(">loadLibrary", spec)
            spec.private.loadLibrary()
            self.profilingReport("<loadLibrary", spec)
        elif destState == PluginState.Initialized:
            self.profilingReport(">initializePlugin", spec)
            spec.private.initializePlugin()
            self.profilingReport("<initializePlugin", spec)
        elif destState == PluginState.Stopped:
            self.profilingReport(">stop", spec)
            spec.private.stop()
            self.profilingReport("<stop", spec)

    def resolveDependencies(self):
        for spec in self.pluginSpecs:
            spec.private.resolveDependencies(self.pluginSpecs)
        for spec in self.loadQueue():
            spec.private.disableIndirectlyIfDependencyDisabled()

    def initProfiling(self):
        # todo
        pass

    def profilingReport(self, what, spec=None):
        # todo
        pass

    def loadSettings(self):
        settings = QSettings(QSettings.IniFormat, QSettings.UserScope,
                             "SparseBoolean", "Android Develop and Test Assistant")
        self.disabledPlugins = settings.value(IGNORED_PLUGINS, [])
        self.forceEnabledPlugins = settings.value(FORCEENABLED_PLUGINS, [])

    def writeSettings(self):
        settings = QSettings(QSettings.IniFormat, QSettings.UserScope,
                             "SparseBoolean", "Android Develop and Test Assistant")
        disabledPlugins = []
        forceEnabledPlugins = []
        for spec in self.pluginSpecs:
            if not spec.isExperimental() and not spec.isEnabled():
                disabledPlugins.append(spec.name())
            if spec.isExperimental() and spec.isEnabled():
                forceEnabledPlugins.append(spec.name())

        settings.setValue(IGNORED_PLUGINS, disabledPlugins)
        settings.setValue(FORCEENABLED_PLUGINS, forceEnabledPlugins)

    @staticmethod
    def disablePluginIndirectly(spec):
        spec.private.disabledIndirectly = True

    def pluginForOption(self, option):
        requiresArgument = False
        for spec in self.pluginSpecs:
            pargs = spec.argumentDescriptions()
            if pargs:
                for description in pargs:
                    if description.name == option:
                        requiresArgument = True if description.parameter else False
                        return spec, requiresArgument
        return None, requiresArgument

    def pluginByName(self, name):
        for spec in self.pluginSpecs:
            if spec.name() == name:
                return spec
        return None

    def __readPluginPaths(self):
        self.pluginCategories.clear()
        self.pluginSpecs[:] = []

        specFiles = []
        searchPaths = self.pluginPaths
        print("Append plugin spec files:")
        while searchPaths:
            searchDir = QDir(searchPaths.pop(0))
            pattern = "*." + self.extension
            fileInfoList = searchDir.entryInfoList([pattern], QDir.Files)
            for fileInfo in fileInfoList:
                print(BColors.DARKCYAN + fileInfo.absoluteFilePath() + BColors.ENDC)
                specFiles.append(fileInfo.absoluteFilePath())
            dirInfoList = searchDir.entryInfoList(QDir.Dirs | QDir.NoDotAndDotDot)
            for dirInfo in dirInfoList:
                searchPaths.append(dirInfo.absoluteFilePath())
        self.defaultCollection = PluginCollection("")
        self.pluginCategories[""] = self.defaultCollection

        for specFile in specFiles:
            spec = PluginSpec(self)
            spec.private.read(specFile)
            if spec.category() in self.pluginCategories:
                collection = self.pluginCategories[spec.category()]
            else:
                collection = PluginCollection(spec.category())
                self.pluginCategories[spec.category()] = collection
            if spec.isExperimental() and (spec.name() in self.forceEnabledPlugins):
                spec.setEnabled(True)
            if not spec.isExperimental() and (spec.name() in self.disabledPlugins):
                spec.setEnabled(False)
            collection.addPlugin(spec)
            self.pluginSpecs.append(spec)
        self.resolveDependencies()
        self.pluginManager.pluginsChanged.emit()

    def __loadQueue(self, spec, queue, circularityCheckQueue):
        if spec in queue:
            return True
        # todo: check for circular dependencies
        # check if we have the dependencies
        if (spec.state() == PluginState.Invalid) or (spec.state == PluginState.Read):
            queue.append(spec)
            return False
        # add dependencies
        for depSpec in spec.dependencySpecs():
            if not self.__loadQueue(depSpec, queue, circularityCheckQueue):
                spec.private.hasError = True
                spec.private.errorString = "Cannot load plugin because dependency failed to load: " \
                                           "{name}({ver})\nReason: {err}".format(
                                               name=depSpec.name(), ver=depSpec.version(),
                                               err=depSpec.errorString())
                return False
        # add self
        queue.append(spec)
        return True

    def __stopAll(self):
        queue = self.loadQueue()
        for spec in queue:
            self.loadPlugin(spec, PluginState.Stopped)
        for item in reversed(queue):
            self.loadPlugin(item, PluginState.Deleted)
