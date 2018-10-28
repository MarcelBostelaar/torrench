#! /usr/bin/env python3

import platform
import os
import sys
import logging.config
import torrench.Torrench as Torrench
import torrench.utilities.logger as logger

logging.config.dictConfig(logger.LOG_SETTINGS)
mylogger = logging.getLogger('log1')

if platform.system() == 'Windows':
    os.system("mode 800")

system = platform.platform()
pyversion = sys.version
arch = platform.machine()


def main():
    """Execution begins here."""
    mylogger.debug(system)
    mylogger.debug(arch)
    mylogger.debug(pyversion)
    mylogger.debug("Torrench started.")
    Torrench.main()


if __name__ == "__main__":
    main()
