__author__ = 'kevin'

import platform


PLATFORM_SYSTEM = platform.system()
OS_MAC = (PLATFORM_SYSTEM == "Darwin")
OS_WIN = (PLATFORM_SYSTEM == "Windows")
OS_LINUX = (PLATFORM_SYSTEM == "Linux")