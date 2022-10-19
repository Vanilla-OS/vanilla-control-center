# apx.py
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
from pathlib import Path
from enum import Enum
from glob import glob


logger = logging.getLogger("Vanilla::Apx")


class Apx:

    __managed_containers = {
        "apx_managed": "Sub System",
        "apx_managed_aur": "Arch Linux Sub System",
    }

    def __init__(self):
        self.__binary = shutil.which("apx")
        self.__desktop = os.path.join(Path.home(), ".local", "share", "applications")
        self.__apps = self.__get_apps()
    
    @property
    def supported(self) -> bool:
        if "apx" in os.environ.get("DISABLED_MODULES", []):
            return False
        return self.__binary is not None
    
    @property
    def apps(self) -> list:
        return self.__apps

    def __get_apps(self) -> list:
        if not self.supported or not os.path.exists(self.__desktop):
            return []
        
        apps = []
        for file in glob(os.path.join(self.__desktop, "apx_managed*.desktop")):
            container = os.path.basename(file).split("-")[0]
            
            with open(file, "r") as f:
                _name, _exec, _terminal = None, None, None
                lines = f.readlines()

                for index, line in enumerate(lines):
                    if _name and _exec and _terminal:
                        apps.append({
                            "Container": self.__managed_containers[container],
                            "Name": _name,
                            "Exec": _exec,
                            "Terminal": _terminal,
                        })
                        break

                    if line.startswith("Name="):
                        _name = line.split("=")[1].strip().replace("◆", "")
                    elif line.startswith("Exec="):
                        _exec = line.split("=")[1].strip()
                    elif line.startswith("Terminal="):
                        _terminal = line.split("=")[1].strip()
                        logger.info("Terminal: {0}".format(_terminal))

                        if index == len(lines) - 1 and not _terminal:
                            _terminal = "false"

        return apps

    def run(self, name: str) -> bool:
        logger.info("Running application: '{0}'".format(name))

        for app in self.__apps:
            if app["Name"] == name:

                cmd = app["Exec"]
                if app["Terminal"] == "true":
                    cmd = "x-terminal-emulator -e " + cmd
                
                try:
                    proc = subprocess.Popen(cmd, shell=True)
                    proc.wait()
                except Exception as e:
                    logger.error("Unable to start managed application: '{0}'".format(name))
                    logger.debug(e)
                    return False
                    
        return True