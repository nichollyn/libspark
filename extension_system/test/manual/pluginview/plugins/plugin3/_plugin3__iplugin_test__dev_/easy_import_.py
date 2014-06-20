__author__ = 'kevin'

import sys
from os import path as ospath


PRINT_FRIENDLY = True


class BColors:
    def __init__(self):
        pass

    if PRINT_FRIENDLY:
        BOLD = '\033[1m'
        UNDERLINE = '\033]4m'
        ENDC = '\033[0m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        DARKCYAN = '\033[36m'
        CYAN = '\033[96m'
        PURPLE = '\033[95m'
    else:
        BOLD = ''
        UNDERLINE = ''
        ENDC = ''
        BLUE = ''
        GREEN = ''
        YELLOW = ''
        RED = ''
        DARKCYAN = ''
        CYAN = ''
        PURPLE = ''


class PackageInfo:
    def __init__(self):
        pass

    package_name = "plugin3"
    """
    The exact name of the package,
        as known as the containing directory name of modules

    For example,
        package_name = 'foo'
    """

    package_identifiable_name = "extension_system.test.manual.pluginview.plugins.plugin3"
    """
    An identifiable string in dotted full name style,
        with the last name exactly the same with package_name

    For example:
        package_identifiable_name = 'top.sub.final.foo'
    """

    package_version = "0.1"
    """
    An identifiable string to distinguish different versions of the package
    """

    dep_modules_roots = ["extension_system"]
    """
    A list for the exact names of top level packages for dependent modules,
        as known as the containing directory name of modules

    For example:
        If package depends on mod1, mod2, modA, modB, with mod1 and mod2 in package 'root1',
        modA and modB in package 'root2', then
            dep_modules_roots = ['foo_dep_mods_root1', 'foo_dep_mods_root2']
    """

    dep_modules_map = {'extension_system': ["extension_system.pluginmanager",
                                            "extension_system.iplugin"]}
    """
    A map with the key by a list of some dependent modules and
        the value by the root package containing the modules in the list

    Note: modules should use the full dotted name started by the root package

    For example:
        If package depends on mod1, mod2, modA, modB, with mod1 and mod2 in package 'root1',
        modA and modB in package 'root2', then it could be:
        dep_modules_map = {
            'root1': ["root1.<possible_intermediate_pkg>.mod1",
                "root1.<possible_intermediate_pkg>.mod2"],
            'root2': ["root2.<possible_intermediate_pkg>.modA",
                "root2.<possible_intermediate_pkg>.modB"],
    """


def append_deps_rootpath(dep_modules_roots, search_depth=10):
    """
    Append all paths described in PackageInfo.dep_modules_roots into the sys.path,
    so any module in the package can be called as a main entry,
    with successfully importing dependent modules of dependent package in an easy scheme:
        'import <identifiable_package_root>.<sub>.<target_module>',
    Which could a more intuitive usage of module import.

    Be sure this function is called for the main entry script with all outer dependent
    package names in the parameter 'dep_modules_roots'
    """
    check_path = ospath.dirname(ospath.abspath(__file__))
    dep_dirs = []
    dep_remains = list(dep_modules_roots)
    for i in range(search_depth):
        check_path = ospath.dirname(check_path)
        check_name = ospath.basename(check_path)
        for dep_name in dep_remains:
            if dep_name == check_name:
                dep_dirs.append(check_path)
                dep_remains.remove(dep_name)
        if not dep_remains:
            break

    if dep_dirs:
        for dep_dir in dep_dirs:
            sys.path.append(dep_dir)
            print(BColors.BLUE
                  + "Append path of package:'{pkg}'".format(pkg=ospath.basename(dep_dir))
                  + " for package:'{name}' to sys.path as dependent modules root."
                    .format(name=PackageInfo.package_name)
                  + BColors.ENDC)
        return [name for name in dep_modules_roots if name not in dep_remains]
    else:
        return None


def setup_easy_import():
    return append_deps_rootpath(PackageInfo.dep_modules_roots)


def pkg_init_intro():
    deps_info = ""
    for key, value in sorted(PackageInfo.dep_modules_map.items()):
        deps_info += "\t     {list} => {root}\n".format(list=value, root=key)
    print(BColors.GREEN + "Initialize package: \n"
          + "\t Name: '{name}'\n".format(name=PackageInfo.package_name)
          + "\t Author: '{auth}'\n".format(auth=__author__)
          + "\t Version: '{ver}'\n".format(ver=PackageInfo.package_version)
          + "\t Dependent modules: (modules list => root package)\n{deps_info}"
            .format(deps_info=deps_info)
          + BColors.ENDC)


pkg_init_intro()
initialized = setup_easy_import()