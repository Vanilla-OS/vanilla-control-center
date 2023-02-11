# driver.py
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

import logging
from gi.repository import Adw
from gi.repository import Gtk, GObject
from gettext import gettext as _

logger = logging.getLogger("Vanilla:Driver")


@Gtk.Template(resource_path='/org/vanillaos/ControlCenter/gtk/driver.ui')
class VanillaDriverRow(Adw.ActionRow):
    __gtype_name__ = "VanillaDriverRow"
    __gsignals__ = {
        "driver-selected": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }
    img_installed = Gtk.Template.Child()
    
    def __init__(self, driver: str):
        super().__init__()
        self.driver = driver
        self.__build_ui()
    
    def __build_ui(self):
        self.set_title(self.driver["name"])
        self.set_subtitle(self.driver["type"])
        self.set_activatable(True)

        if self.driver["installed"]:
            self.img_installed.set_visible(True)

        self.connect(_("Activated"), self.__on_activated)
    
    def __on_activated(self, widget):
        self.emit(_("Driver selected"), self.driver["name"])
    
    def set_installed(self, installed: bool):
        if self.driver[_("Installed")] == installed:
            return

        self.driver[_("Installed")] = installed
        self.img_installed.set_visible(installed)

class VanillaDriversGroup(Adw.PreferencesGroup):
    __gtype_name__ = "VanillaDriversGroup"
    __gsignals__ = {
        "installation-needed": (GObject.SignalFlags.RUN_FIRST, None, (str,str)),
    }

    def __init__(self, vendor: str, model: str, drivers: list):
        super().__init__()
        self.__registry = {}
        self.vendor = vendor
        self.model = model
        self.drivers = drivers
        self.__build_ui()

    def __build_ui(self):
        self.set_title(self.model)
        self.set_description(self.vendor)
        
        for driver in self.drivers:
            row = VanillaDriverRow(driver)
            self.__registry[driver["name"]] = row
            self.add(row)
            row.connect(_("Driver selected"), self.__on_driver_selected)

    def __on_driver_selected(self, widget, driver):
        logging.info(_("Selected driver: {}").format(driver))
        for _driver, widget in self.__registry.items():
            if _driver == driver:
                widget.set_installed(True)
                continue
            widget.set_installed(False)
        self.emit(_("Installation needed"), self.model, driver)