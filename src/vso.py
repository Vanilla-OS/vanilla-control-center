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

    def get_scheduling(self) -> str:
        res = subprocess.check_output([self.__binary, "config", "get", "updates.schedule"])
        return res.decode("utf-8").strip()

    def set_scheduling(self, value: int):
        rules = {
            0: "weekly",
            1: "monthly"
        }
        subprocess.run(["pkexec", self.__binary, "config", "set", "updates.schedule", rules[value]])
