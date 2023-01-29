# vso.py
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
    def update_command(self) -> str:
        return "pkexec {} trigger-update --now".format(self.__binary)

    @property
    def scheduling(self) -> str:
        return self.get_config()["updates"]["schedule"]

    @property
    def smart(self) -> bool:
        return self.get_config()["updates"]["smart"]

    @property
    def auto(self) -> bool:
        return self.get_autoupdate_status()

    @property
    def can_update(self) -> bool:
        return not os.path.exists("/tmp/abroot-transactions.lock")

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

    def get_autoupdate_status(self) -> bool:
        res = subprocess.run(["systemctl", "is-enabled", "vso-autoupdate.timer"], capture_output=True)
        return res.returncode == 0

    def set_autoupdate(self, value: bool) -> bool:
        action = "enable" if value else "disable"
        subprocess.run(["pkexec", "systemctl", action, "vso-autoupdate.timer", "--now"])
        return self.get_autoupdate_status() == value

    def get_updates(self) -> [bool, list]:
        res = subprocess.run(["pkexec", self.__binary, "update-check"], capture_output=True)
        updates = []

        if res.returncode == 0:
            for update in [line for line in res.stdout.decode().splitlines() if line.startswith("  -")]:
                update = update.split()
                updates.append({
                    "name": update[1],
                    "version": update[2] + " -> " + update[4]
                })
            return True, updates
        else:
            logger.error(res.stderr.decode())
            return False, []
