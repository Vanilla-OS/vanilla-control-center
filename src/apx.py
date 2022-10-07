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

    def __init__(self):
        self.__binary = shutil.which("apx")
        self.__desktop = os.path.join(Path.home(), ".local", "share", "applications")
    
    @property
    def supported(self):
        if "apx" in os.environ.get("DISABLED_MODULES", []):
            return False
        return self.__binary is not None

    def get_apps(self):
        if not self.supported or not os.path.exists(self.__desktop):
            return []
        
        apps = []
        for file in glob(os.path.join(self.__desktop, "apx_managed*.desktop")):
            with open(file, "r") as f:
                _name, _exec = None, None

                for line in f.readlines():
                    if line.startswith("Name="):
                        _name = line.split("=")[1].strip().replace("◆", "")
                    elif line.startswith("Exec="):
                        _exec = line.split("=")[1].strip()
                        
                    if _name and _exec:
                        apps.append((_name, _exec))
                        break

        return apps
