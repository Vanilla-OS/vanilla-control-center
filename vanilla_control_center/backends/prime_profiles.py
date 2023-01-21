# prime_profiles.py
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
import tempfile
import subprocess
import shutil

from vanilla_control_center.backends.exceptions import UnsupportedPrimeSetup

logger = logging.getLogger("Vanilla::PrimeProfiles")


class PrimeProfiles:
    
    def __init__(self):
        self.__binary = shutil.which("prime-select")
        self.__available_profiles = ["nvidia", "intel", "on-demand"]
    
    @property
    def supported(self) -> bool:
        if "prime" in os.environ.get("DISABLED_MODULES", []):
            logger.info("prime module disabled")
            return False
            
        if self.__binary is None:
            logger.info("prime-select not found")
            return False

        if not self.__is_laptop():
            logger.info("prime-select not supported for this device")
            return False
        
        try:
            self.get_gpus()
        except UnsupportedPrimeSetup:
            logger.info("prime-select not supported for this setup")
            return False

        return True

    @property
    def available_profiles(self) -> list:
        return self.__available_profiles

    def __is_laptop(self) -> bool:
        path = '/sys/devices/virtual/dmi/id/chassis_type'
        if not os.path.isfile(path):
            return False

        with open(path, 'r') as f:
            if chassis_type := f.read():
                chassis_type = int(chassis_type.strip())
            else:
                return False

            if chassis_type in (8, 9, 10, 31):
                return True
                
        return False

    def get_current(self) -> str:
        return subprocess.check_output([self.__binary, "query"], text=True).strip()

    def can_set(self) -> bool:
        return not os.path.exists("/tmp/abroot-transactions.lock")

    def get_set_profile_command(self, profile: str) -> str:
        if not self.can_set():
            return None

        if profile not in self.__available_profiles:
            raise ValueError("Invalid profile name")

        return " ".join(["pkexec", "abroot", "exec", "-f", self.__binary, profile])

    def get_gpus(self) -> dict:
        gpus = {
            "integrated": "",
            "discrete": ""
        }
        found = {}

        res = subprocess.check_output(["lspci", "-k"], text=True)
        for line in res.splitlines():
            if ("VGA" in line or "3D" in line) and not "Non-VGA" in line:
                _gpu = line.split("controller:")[1].strip()
                if "intel" in _gpu.lower():
                    found["intel"] = _gpu
                elif "nvidia" in _gpu.lower():
                    found["nvidia"] = _gpu
                elif "amd" in _gpu.lower() or "ati" in _gpu.lower():
                    found["amd"] = _gpu

        if "intel" in found and "nvidia" in found:
            gpus["integrated"] = found["intel"]
            gpus["discrete"] = found["nvidia"]
        elif "intel" in found and "amd" in found:
            gpus["integrated"] = found["intel"]
            gpus["discrete"] = found["amd"]
        elif "nvidia" in found and "amd" in found:
            gpus["integrated"] = found["amd"]
            gpus["discrete"] = found["nvidia"]
        else:
            raise UnsupportedPrimeSetup

        return gpus
