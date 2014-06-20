__author__ = 'kevin'

from PySide.QtCore import QCoreApplication


END_OF_OPTIONS = "--"


class TokenType(object):
    OptionalToken, RequiredToken = range(2)


class OptionsParser(object):
    NO_LOAD_OPTION = "-noload"
    TEST_OPTION = "-test"
    PROFILE_OPTION = "-profile"

    def __init__(self, args, appOptions, foundAppOptions, pmPrivate):
        super(OptionsParser, self).__init__()
        self.args = args
        self.currentArg = ""
        self.appOptions = appOptions
        self.foundAppOptions = foundAppOptions
        self.pmPrivate = pmPrivate
        # Jump over program name
        self.nextTokenIndex = 1
        self.argsLength = len(self.args)
        self.isDependencyRefreshNeeded = False
        self.hasError = False
        self.lastError = None
        if self.foundAppOptions:
            self.foundAppOptions.clear()
        self.pmPrivate.arguments[:] = []

    def lastError(self):
        return self.lastError

    def nextToken(self, tokenType=TokenType.OptionalToken):
        if self.nextTokenIndex == self.argsLength:
            if tokenType is TokenType.RequiredToken:
                self.hasError = True
                self.lastError = QCoreApplication.translate(None,
                                                            "The option {arg} requires an argument"
                                                                .format(arg=self.currentArg))
            return False
        self.currentArg = self.args[self.nextTokenIndex]
        self.nextTokenIndex += 1
        return True

    def parse(self):
        while not self.hasError:
            if not self.nextToken():
                break
            if self.checkForEndOfOptions():
                break
            if self.checkForNoLoadOption():
                continue
            if self.checkForProfilingOption():
                continue
            if self.checkForTestOption():
                continue
            if self.checkForAppOption():
                continue
            if self.checkForPluginOption():
                continue
            if self.checkForUnknownOption():
                break
            self.pmPrivate.arguments.append(self.currentArg)
        if self.isDependencyRefreshNeeded:
            self.pmPrivate.resolveDependencies()
        return not self.hasError, self.lastError

    def checkForEndOfOptions(self):
        if self.currentArg != END_OF_OPTIONS:
            return False
        while self.nextToken():
            self.pmPrivate.arguments.append(self.currentArg)
        return True

    def checkForNoLoadOption(self):
        if self.currentArg != OptionsParser.NO_LOAD_OPTION:
            return False
        if self.nextToken(TokenType.RequiredToken):
            spec = self.pmPrivate.pluginByName(self.currentArg)
            if not spec:
                self.lastError = QCoreApplication.translate(None,
                                                            "The plugin '{name}' does not exist."
                                                            .format(name=self.currentArg))
                self.hasError = True
            else:
                self.pmPrivate.disablePluginIndirectly(spec)
                self.isDependencyRefreshNeeded = True

        return True

    def checkForTestOption(self):
        if self.currentArg != OptionsParser.TEST_OPTION:
            return False
        if self.nextToken(TokenType.RequiredToken):
            spec = self.pmPrivate.pluginByName(self.currentArg)
            if not spec:
                self.lastError = QCoreApplication.translate(None,
                                                            "The plugin '{name}' doest not exist."
                                                            .format(self.currentArg))
                self.hasError = True
            else:
                self.pmPrivate.testSpecs.append(spec)

        return True

    def checkForAppOption(self):
        if self.currentArg not in self.appOptions:
            return False
        option = self.currentArg
        argument = ""
        if self.appOptions.get(self.currentArg) \
           and self.nextToken(TokenType.RequiredToken):
            argument = self.currentArg
        if self.foundAppOptions:
            self.foundAppOptions[option] = argument
        return True

    def checkForPluginOption(self):
        spec, requiresParameter = self.pmPrivate.pluginForOption(self.currentArg)
        if not spec:
            return False
        spec.addArgument(self.currentArg)
        if requiresParameter and self.nextToken(TokenType.RequiredToken):
            spec.addArgument(self.currentArg)

        return True

    def checkForProfilingOption(self):
        if self.currentArg != OptionsParser.PROFILE_OPTION:
            return False
        self.pmPrivate.initProfiling()
        return True

    def checkForUnknownOption(self):
        if '-' not in self.currentArg:
            return False
        self.lastError = QCoreApplication.translate(None,
                                                    "Unknown option '{name}'"
                                                    .format(self.currentArg))
        self.hasError = True
        return True
