# apx.py
#
# Copyright 2023 Mirko Brombin
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
        "apx_managed": {
            "Flag": "",
            "Name": "Sub System",
        },
        "apx_managed_aur": {
            "Flag": "--aur",
            "Name": "Arch Linux Sub System",
        },
        "apx_managed_dnf": {
            "Flag": "--dnf",
            "Name": "Fedora Sub System",
        },
        "apx_managed_apk": {
            "Flag": "--apk",
            "Name": "Alpine Sub System",
        }
    }

    def __init__(self):
        self.__binary = shutil.which("apx")
        self.__dbox_binary = "/usr/lib/apx/distrobox"
        self.__desktop = os.path.join(Path.home(), ".local", "share", "applications")
        self.__apps = self.__get_apps()
    
    @property
    def supported(self) -> bool:
        if "apx" in os.environ.get("DISABLED_MODULES", []):
            logger.debug("apx module disabled")
            return False

        if self.__binary is None:
            logger.debug("apx binary not found")
            return False

        if not os.path.exists(self.__dbox_binary):
            logger.debug("distrobox binary not found")
            return False

        return True
    
    @property
    def apps(self) -> list:
        return self.__apps

    @property
    def containers(self) -> list:
        return self.__get_containers()

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
                            "Container": self.__managed_containers[container]["Name"],
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
    
    def __get_apps_for_container(self, container: str) -> list:
        if not self.supported:
            return []

        apps = []
        for app in self.__apps:
            if app["Container"] == container:
                apps.append(app)

        return apps

    def __get_containers(self) -> list:
        if not self.supported:
            return []

        res = subprocess.run([self.__dbox_binary, "list"], capture_output=True)
        if res.returncode != 0:
            logger.error("Unable to get containers")
            return []
            
        containers = []
        for alias, container in self.__managed_containers.items():
            _container = {
                "Name": container["Name"],
                "Status": 1,
                "Alias": alias,
                "ShellCmd": f"kgx -e { self.__binary } { container['Flag'] } enter",
                "InitCmd": f"kgx -e { self.__binary } { container['Flag'] } init",
                "Apps": []
            }
            if alias in res.stdout.decode("utf-8"):
                logger.info("Container '{0}' found".format(alias))
                _container["Status"] = 0
                _container["Apps"] = self.__get_apps_for_container(_container["Name"])
            else:
                logger.info("Container '{0}' not found".format(alias))

            containers.append(_container)

        return containers

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