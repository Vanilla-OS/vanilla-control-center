# vso.py
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
import json
import logging
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from enum import Enum
from glob import glob


logger = logging.getLogger("Vanilla::VSO")


class Vso:

    def __init__(self):
        self.__binary = shutil.which("vso")
        self.__conf_path = "/etc/vso/config.json"
        
    def get_latest_check(self) -> str:
        if os.path.exists("/var/log/vso-check.log"):
            with open("/var/log/vso-check.log", "r") as f:
                return f.read()
        return

    def get_latest_check_beautified(self) -> str:
        latest_check = self.get_latest_check()

        if latest_check:
            latest_check = latest_check.split(".")[0]
            latest_check = datetime.strptime(latest_check, "%Y-%m-%d %H:%M:%S")
            return latest_check.strftime("%-d %B %Y, %H:%M")
            
        return

    def get_config(self) -> dict:
        if os.path.exists(self.__conf_path):
            with open(self.__conf_path, "r") as f:
                return json.load(f)
        
        raise FileNotFoundError("VSO Config file not found at {}".format(self.__conf_path))

    @property
    def scheduling(self) -> str:
        return self.get_config()["updates"]["schedule"]

    @property
    def smart(self) -> bool:
        return self.get_config()["updates"]["smart"]

    def set_scheduling(self, value: int) -> bool:
        rules = {
            0: "weekly",
            1: "monthly"
        }
        res = subprocess.run(["pkexec", self.__binary, "config", "set", "updates.schedule", rules[value]])
        return res.returncode == 0

    def set_smartupdate(self, value: bool) -> bool:
        res = subprocess.run(["pkexec", self.__binary, "config", "set", "updates.smart", str(value).lower()])
        return res.returncode == 0
