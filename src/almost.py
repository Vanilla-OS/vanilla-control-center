# almost.py
#
# Copyright 2022 Mirko Brombin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-only

import os
import logging
import subprocess
import shutil
from enum import Enum

logger = logging.getLogger("Vanilla::Almost")


class Almost:

    def __init__(self):
        self.__binary = shutil.which("almost")
        self.__config = "/etc/almost.ini"
        self.__params = self.__get_params()
    
    @property
    def supported(self):
        return self.__binary is not None

    @property
    def params(self):
        return self.__params

    def set_param(self, key: str, val: str):
        logger.info(f"Setting {key} to {val}")
        proc = subprocess.run(["pkexec", self.__binary, "config", "set", key, val], capture_output=True)
        return proc.returncode == 0

    def __get_params(self):
        logger.info("Getting Almost parameters")
        if not self.supported:
            return {}

        if not os.path.exists(self.__config):
            return {}

        params = {}
        with open(self.__config, "r") as f:
            lines = f.readlines()
            for line in lines:
                if "almost::persistmodestatus" in line:
                    params["persistent"] = True if "true" in line else False
                elif "almost::defaultmode" in line:
                    params["default"] = True if "0" in line else False
                elif "almost::currentmode" in line:
                    params["current"] = True if "0" in line else False
                    
        return params

    def set_persistent(self, value: bool):
        return self.set_param("almost::persistmodestatus", "0" if value else "1")

    def set_default(self, value: bool):
        return self.set_param("almost::defaultmode", "0" if value else "1")

    def set_current(self, value: bool):
        mode = "ro" if value else "rw"
        proc = subprocess.run(["pkexec", self.__binary, "enter", mode], capture_output=True)
        return proc.returncode == 0
