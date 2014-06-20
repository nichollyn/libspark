from PySide.QtCore import QRegExp, QXmlStreamReader, QFile, QFileInfo, QIODevice, QDir
from PySide.QtCore import QCoreApplication, QObject

import pluginloader
from _extension_system__libspark__dev_.dev_log_ import Log


TAG = "PluginSpec"

PLUGIN_SPEC = "PluginSpec"
PLUGIN = "plugin"
PLUGIN_NAME = "name"
PLUGIN_MAINCLASS = "mainClass"
PLUGIN_VERSION = "version"
PLUGIN_COMPATVERSION = "compatVersion"
PLUGIN_EXPERIMENTAL = "experimental"
VENDOR = "vendor"
COPYRIGHT = "copyright"
LICENSE = "license"
DESCRIPTION = "description"
URL = "url"
CATEGORY = "category"
DEPENDENCYLIST = "dependencyList"
DEPENDENCY = "dependency"
DEPENDENCY_NAME = "name"
DEPENDENCY_VERSION = "parameter"
ARGUMENTLIST = "argumentList"
ARGUMENT = "argument"
ARGUMENT_NAME = "name"
ARGUMENT_PARAMETER = "parameter"


class PluginDependency(object):
    def __init__(self):
        super(PluginDependency, self).__init__()
        self.name = ""
        self.version = ""

    def __eq__(self, other):
        return self.name.__eq__(other.name) \
            and self.version.__eq__(other.version)


class PluginArgumentDescription(object):
    def __init__(self):
        super(PluginArgumentDescription, self).__init__()
        self.name = ""
        self.parameter = ""
        self.description = ""


class PluginState(object):
    Invalid, Read, Resolved, Loaded, Initialized, Running, Stopped, Deleted = range(8)


class PluginSpec(object):
    def __init__(self, manager):
        super(PluginSpec, self).__init__()
        self.private = PluginSpecPrivate(self, manager)

    def name(self):
        return self.private.name

    def mainClass(self):
        return self.private.mainClass

    def version(self):
        return self.private.version

    def compatVersion(self):
        return self.private.compatVersion

    def vendor(self):
        return self.private.vendor

    def copyright(self):
        return self.private.copyright

    def license(self):
        return self.private.license

    def description(self):
        return self.private.description

    def url(self):
        return self.private.url

    def category(self):
        return self.private.category

    def isExperimental(self):
        return self.private.experimental

    def isEnabled(self):
        return self.private.enabled

    def isDisabledIndirectly(self):
        return self.private.disabledIndirectly

    def dependencies(self):
        return self.private.dependencies

    def argumentDescriptions(self):
        return self.private.argumentDescriptions

    def location(self):
        return self.private.location

    def filePath(self):
        return self.private.filePath

    def setEnabled(self, value):
        self.private.enabled = value

    def setDisabledIndirectly(self, value):
        self.private.disabledIndirectly = value

    def arguments(self):
        return self.private.arguments

    def setArguments(self, arguments):
        self.private.arguments = arguments

    def addArgument(self, argument):
        self.private.arguments.append(argument)

    def provides(self, pluginName, version):
        return self.private.provides(pluginName, version)

    def dependencySpecs(self):
        return self.private.dependencySpecs

    def providesForSpecs(self):
        return self.private.providesSpecs

    def plugin(self):
        return self.private.plugin

    def state(self):
        return self.private.state

    def hasError(self):
        return self.private.hasError

    def errorString(self):
        return self.private.errorString


class PluginSpecPrivate(QObject):
    def __init__(self, spec, manager):
        super(PluginSpecPrivate, self).__init__()
        self.pluginSpec = spec
        self.manager = manager
        self.name = ""
        self.mainClass = ""
        self.version = ""
        self.compatVersion = ""
        self.experimental = False
        self.vendor = ""
        self.copyright = ""
        self.license = ""
        self.description = ""
        self.url = ""
        self.category = ""
        self.dependencies = []
        self.enabled = True
        self.disabledIndirectly = False

        self.location = ""
        self.filePath = ""
        self.arguments = []

        self.providesSpecs = []
        self.dependencySpecs = []
        self.argumentDescriptions = []
        self.plugin = None

        self.state = PluginState.Invalid
        self.hasError = False
        self.errorString = ""

    def read(self, fileName):
        self.state = PluginState.Invalid
        self.hasError = False
        self.dependencies = []
        specFile = QFile(fileName)
        if not specFile.exists():
            msg = QCoreApplication.translate(None, "File does not exist: {name}")
            return self.__reportError(msg.format(name=specFile.fileName()))
        if not specFile.open(QIODevice.ReadOnly):
            msg = QCoreApplication.translate(None, "Could not open file for read: {name}")
            return self.__reportError(msg.format(name=specFile.fileName()))
        fileInfo = QFileInfo(specFile)
        self.location = fileInfo.absolutePath()
        self.filePath = fileInfo.absoluteFilePath()
        reader = QXmlStreamReader(specFile)
        while not reader.atEnd():
            reader.readNext()
            tokenType = reader.tokenType()
            if tokenType is QXmlStreamReader.StartElement:
                self.__readPluginSpec(reader)
            else:
                pass
        if reader.hasError():
            msg = QCoreApplication.translate(None, "Error parsing file {0}: {1}, at line {2}, column {3}")
            return self.__reportError(msg.format(specFile.fileName(), reader.errorString(),
                                                 reader.lineNumber(), reader.columnNumber()))
        self.state = PluginState.Read
        return True

    def provides(self, pluginName, pluginVersion):
        if pluginName.lower() == self.name.lower():
            return (PluginSpecPrivate.versionCompare(self.compatVersion, pluginVersion)
                    <= 0 <= PluginSpecPrivate.versionCompare(self.version, pluginVersion))
        else:
            return False

    def resolveDependencies(self, specs):
        if self.hasError:
            return False
        if self.state is PluginState.Resolved:
            # Go back, so we just re-resolve the dependencies.
            self.state = PluginState.Read
        if self.state is not PluginState.Read:
            self.errorString = QCoreApplication.translate(None, "Resolving dependencies failed because state != Read")
            self.hasError = True
            return False
        resolvedDependencies = []
        for dependency in self.dependencies:
            found = None
            for spec in specs:
                if spec.provides(dependency.name, dependency.version):
                    found = spec
                    spec.private.addProvidesForPlugin(self.pluginSpec)
                    break
            if not found:
                self.hasError = True
                if self.errorString:
                    self.errorString += "\n"
                msg = QCoreApplication.translate(None, "Could not resolve dependency {0}({1})")
                self.errorString += msg.format(dependency.name, dependency.version)
                continue
            resolvedDependencies.append(found)
        if self.hasError:
            return False

        self.dependencySpecs = resolvedDependencies
        self.state = PluginState.Resolved
        return True

    def loadLibrary(self):
        if self.hasError:
            return False
        if self.state is not PluginState.Resolved:
            if self.state is PluginState.Loaded:
                return True
            self.errorString = QCoreApplication.translate(None, "Loading the library failed because state != Resolved")
            self.hasError = True
            return False
        pluginPath = QDir.toNativeSeparators(self.location)
        pluginClass = pluginloader.loadIPlugin(pluginPath, self.name + "." + self.mainClass)
        if not pluginClass:
            self.hasError = True
            self.errorString = QCoreApplication.translate(None,
                                                          "Plugin is not valid (does not derive from IPlugin")
            return False
        self.state = PluginState.Loaded
        self.plugin = pluginClass(self.manager)
        self.plugin.private.pluginSpec = self.pluginSpec
        return True

    def initializePlugin(self):
        if self.hasError:
            return False
        if self.state is not PluginState.Loaded:
            if self.state is PluginState.Initialized:
                return True
            self.errorString = QCoreApplication.translate(None,
                                                          "Initializing the plugin failed because state != Loaded")
            self.hasError = True
            return False
        if not self.plugin:
            self.errorString = QCoreApplication.translate(None,
                                                          "Internal error: have no plugin instance to initialize")
            self.hasError = True
            return False
        initialized, error = self.plugin.initialize(self.arguments)
        if not initialized:
            self.errorString = QCoreApplication.translate(None,
                                                          "Plugin initialization failed: {err}".format(err=error))
            self.hasError = True
            return False
        self.state = PluginState.Initialized
        return True

    def initializeExtensions(self):
        if self.hasError:
            return False
        if self.state is not PluginState.Initialized:
            if self.state is PluginState.Running:
                return True
            self.errorString = QCoreApplication.translate(None,
                                                          "Cannot perform extensionsInitialized "
                                                          "because state != Initialized")
            self.hasError = True
            return False
        if not self.plugin:
            self.errorString = QCoreApplication.translate(None,
                                                          "Internal error: have no plugin instance "
                                                          " perform extensionInitialized")
            self.hasError = True
            return False
        self.plugin.extensionsInitialized()
        self.state = PluginState.Running
        return True

    def stop(self):
        if not self.plugin:
            return None
        self.plugin.aboutToShutdown()

    def kill(self):
        if not self.plugin:
            return None
        self.plugin = None
        self.state = PluginState.Deleted

    def addProvidesForPlugin(self, dependent):
        self.providesSpecs.append(dependent)

    def removeProvidesForPlugin(self, dependent):
        self.providesSpecs.remove(dependent)

    def disableIndirectlyIfDependencyDisabled(self):
        self.disabledIndirectly = False
        if not self.enabled:
            return
        for dependencySpec in self.dependencySpecs:
            if dependencySpec.isDisabledIndirectly() or not dependencySpec.isEnabled():
                self.disabledIndirectly = True
                break

    @staticmethod
    def versionRegExp():
        if not hasattr(PluginSpecPrivate.versionRegExp, "reg"):
            PluginSpecPrivate.versionRegExp.reg = QRegExp("([0-9]+)(?:[.]([0-9]+))?(?:[.]([0-9]+))?(?:_([0-9]+))?")

        return PluginSpecPrivate.versionRegExp.reg

    @staticmethod
    def versionCompare(version1, version2):
        reg1 = PluginSpecPrivate.versionRegExp()
        reg2 = PluginSpecPrivate.versionRegExp()
        if not reg1.exactMatch(version1):
            return 0
        if not reg2.exactMatch(version2):
            return 0
        for i in range(4):
            number1 = int(reg1.cap(i+1))
            number2 = int(reg2.cap(i+1))
            if number1 < number2:
                return -1
            if number1 > number2:
                return 1
        return 0

    @staticmethod
    def isValidVersion(version):
        return PluginSpecPrivate.versionRegExp().exactMatch(version)

    @staticmethod
    def __msgAttributeMissing(elt, attribute):
        msg = QCoreApplication.translate(None, "'{param1}' misses attribute '{param2}'")
        return msg.format(param1=str(elt), param2=str(attribute))

    @staticmethod
    def __msgInvalidFormat(content):
        msg = QCoreApplication.translate(None, "'{param}' has invalid format")
        return msg.format(param=content)

    @staticmethod
    def __msgInvalidElement(name):
        msg = QCoreApplication.translate(None, "Invalid element '{param}'")
        return msg.format(param=name)

    @staticmethod
    def __msgUnexpectedClosing(name):
        msg = QCoreApplication.translate(None, "Unexpected closing element '{param}'")
        return msg.format(param=name)

    @staticmethod
    def __msgUnexpectedToken():
        return QCoreApplication.translate(None, "Unexpected token")

    def __reportError(self, err):
        self.errorString = err
        self.hasError = True
        Log.i(TAG, self.errorString)
        return False

    def __readPluginSpec(self, reader):
        element = reader.name()
        if element != "plugin":
            msg = QCoreApplication.translate(None, "Expected element '{name}' as top level element")
            reader.raiseError(msg.format(name=PLUGIN))
            return
        self.name = reader.attributes().value(PLUGIN_NAME)
        if not self.name:
            reader.raiseError(PluginSpecPrivate.__msgAttributeMissing(PLUGIN, PLUGIN_NAME))
            return
        self.version = reader.attributes().value(PLUGIN_VERSION)
        if not self.version:
            reader.raiseError(PluginSpecPrivate.__msgAttributeMissing(PLUGIN, PLUGIN_VERSION))
            return
        if not PluginSpecPrivate.isValidVersion(self.version):
            reader.raiseError(PluginSpecPrivate.__msgInvalidFormat(PLUGIN_VERSION))
            return
        self.compatVersion = reader.attributes().value(PLUGIN_COMPATVERSION)
        if self.compatVersion and not PluginSpecPrivate.isValidVersion(self.compatVersion):
            reader.raiseError(PluginSpecPrivate.__msgInvalidFormat(PLUGIN_COMPATVERSION))
            return
        elif not self.compatVersion:
            self.compatVersion = self.version

        experimentalString = reader.attributes().value(PLUGIN_EXPERIMENTAL)
        self.experimental = (experimentalString.lower() == "true".lower())
        if experimentalString and not self.experimental and not experimentalString.lower() == "false".lower():
            reader.raiseError(PluginSpecPrivate.__msgInvalidFormat(PLUGIN_EXPERIMENTAL))
            return
        self.enabled = not self.experimental
        while not reader.atEnd():
            reader.readNext()
            tokenType = reader.tokenType()
            if tokenType is QXmlStreamReader.StartElement:
                element = reader.name()
                if element == PLUGIN_MAINCLASS:
                    self.mainClass = reader.readElementText().strip()
                elif element == VENDOR:
                    self.vendor = reader.readElementText().strip()
                elif element == COPYRIGHT:
                    self.copyright = reader.readElementText().strip()
                elif element == LICENSE:
                    self.license = reader.readElementText().strip()
                elif element == DESCRIPTION:
                    self.description = reader.readElementText().strip()
                elif element == URL:
                    self.url = reader.readElementText().strip()
                elif element == CATEGORY:
                    self.category = reader.readElementText().strip()
                elif element == DEPENDENCYLIST:
                    self.__readDependencies(reader)
                elif element == ARGUMENTLIST:
                    self.__readArgumentDescriptions(reader)
                else:
                    reader.raiseError(PluginSpecPrivate.__msgInvalidElement(self.name))
            elif (tokenType is QXmlStreamReader.EndDocument
                  or tokenType is QXmlStreamReader.Comment
                  or tokenType is QXmlStreamReader.EndElement
                  or tokenType is QXmlStreamReader.Characters):
                pass
            else:
                reader.raiseError(PluginSpecPrivate.__msgUnexpectedToken())

    def __readArgumentDescriptions(self, reader):
        while not reader.atEnd():
            reader.readNext()
            tokenType = reader.tokenType()
            if tokenType is QXmlStreamReader.StartElement:
                element = reader.name()
                if element == ARGUMENT:
                    self.readArgumentDescription(reader)
                else:
                    reader.raiseError(PluginSpecPrivate.__msgInvalidElement(self.name))
            if (tokenType is QXmlStreamReader.Comment
                    or tokenType is QXmlStreamReader.Characters):
                pass
            elif tokenType is QXmlStreamReader.EndElement:
                element = reader.name()
                if element == ARGUMENTLIST:
                    return
                reader.raiseError(PluginSpecPrivate.__msgUnexpectedClosing(element))
            else:
                reader.raiseError(PluginSpecPrivate.__msgUnexpectedToken())

    def __readArgumentDescription(self, reader):
        arg = PluginArgumentDescription()
        arg.name = reader.attributes().value(ARGUMENT_NAME)
        if not arg.name:
            reader.raiseError(PluginSpecPrivate.__msgAttributeMissing(ARGUMENT, ARGUMENT_NAME))
            return
        arg.parameter = reader.attributes().value(ARGUMENT_PARAMETER)
        arg.description = reader.readElementText()
        if reader.tokenType() is not QXmlStreamReader.EndElement:
            reader.raiseError(PluginSpecPrivate.__msgUnexpectedToken())
        self.argumentDescriptions.append(arg)

    def __readDependencies(self, reader):
        while not reader.atEnd():
            reader.readNext()
            tokenType = reader.tokenType()
            if tokenType is QXmlStreamReader.StartElement:
                element = reader.name()
                if element == DEPENDENCY:
                    self.__readDependencyEntry(reader)
                else:
                    reader.raiseError(PluginSpecPrivate.__msgInvalidElement(self.name))
            elif (tokenType is QXmlStreamReader.Comment
                  or tokenType is QXmlStreamReader.Characters):
                pass
            elif tokenType is QXmlStreamReader.EndElement:
                element = reader.name()
                if element == DEPENDENCYLIST:
                    return
                reader.raiseError(PluginSpecPrivate.__msgUnexpectedClosing(element))
            else:
                reader.raiseError(PluginSpecPrivate.__msgUnexpectedToken())

    def __readDependencyEntry(self, reader):
        dep = PluginDependency()
        dep.name = reader.attributes().value(DEPENDENCY_NAME)
        if not dep.name:
            reader.raiseError(PluginSpecPrivate.__msgAttributeMissing(DEPENDENCY, DEPENDENCY_NAME))
            return
        dep.version = reader.attributes().value(DEPENDENCY_VERSION)
        if dep.version and not PluginSpecPrivate.isValidVersion(dep.version):
            reader.raiseError(PluginSpecPrivate.__msgInvalidFormat(DEPENDENCY_VERSION))
            return
        self.dependencies.append(dep)
        reader.readNext()
        if reader.tokenType() is not QXmlStreamReader.EndElement:
            reader.raiseError(PluginSpecPrivate.__msgUnexpectedToken())

