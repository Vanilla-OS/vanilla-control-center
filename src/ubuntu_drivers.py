# ubuntu-drivers.py
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

logger = logging.getLogger("Vanilla::UbuntuDrivers")


class UbuntuDrivers:
    def __init__(self):
        self.__binary = "/usr/bin/ubuntu-drivers"
        if shutil.which("_ubuntu-drivers"):
            self.__binary = "/usr/bin/_ubuntu-drivers"
    
    def get_devices(self) -> list:
        logger.info("Getting devices list")
        devices = []
        output = subprocess.run([self.__binary, "devices"], capture_output=True, text=True).stdout
        nvidia_installed = False

        for line in output.splitlines():
            if "==" in line:
                device = {}
                device["modalias"] = line.split("==")[1].strip()
                devices.append(device)
            elif "vendor" in line:
                devices[-1]["vendor"] = line.split(":")[1].strip()
            elif "model" in line:
                devices[-1]["model"] = line.split(":")[1].strip()
            elif "driver" in line:
                if "drivers" not in devices[-1]:
                    devices[-1]["drivers"] = []

                driver = {}
                _driver = line.split(":")[1].strip().split(" ")
                driver["name"] = _driver[0]
                driver["type"] = " ".join(_driver[2:])
                driver["installed"] = self.__check_installation(driver["name"])

                if "nvidia" in driver["name"] and driver["installed"]:
                    nvidia_installed = True
                if "nouveau" in driver["name"] and nvidia_installed:
                    driver["installed"] = False

                devices[-1]["drivers"].append(driver)
                devices[-1]["drivers"] = sorted(devices[-1]["drivers"], key=lambda k: k["name"])
                devices[-1]["drivers"] = sorted(devices[-1]["drivers"], key=lambda k: k["installed"], reverse=True)
        
        logger.debug("Devices list: %s", devices)
                    
        return devices

    def __check_installation(self, driver: str) -> bool:
        output = subprocess.run(["dpkg", "-l", driver], capture_output=True, text=True).stdout
        res = "ii" in output
        logger.debug("Driver %s installed: %s", driver, res)
        return res

    def install(self, driver: str) -> bool:
        if "FAKE" in os.environ:
            logging.info(f"executing cmd: pkexec {self.__binary} install {driver}")
            return True

        _cmd = [self.__binary, "install", driver]
        if shutil.which("almost"):
            _cmd = ["pkexec", "almost", "run"] + _cmd
        else:
            _cmd = ["pkexec"] + _cmd
            
        proc = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        return proc.returncode == 0

    def autoinstall(self) -> bool:
        if "FAKE" in os.environ:
            logging.info(f"executing cmd: pkexec {self.__binary} autoinstall")
            return True

        proc = subprocess.Popen(["pkexec", self.__binary, "autoinstall"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        return proc.returncode == 0
