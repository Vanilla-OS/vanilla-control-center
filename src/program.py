# program.py
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


logger = logging.getLogger("Vanilla:Program")


@Gtk.Template(resource_path='/org/vanillaos/ControlCenter/gtk/program.ui')
class VanillaApxProgram(Adw.ActionRow):
    __gtype_name__ = "VanillaApxProgram"
    __gsignals__ = {
        "run-requested": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "program-exited": (GObject.SignalFlags.RUN_FIRST, None, (str,))
    }
    btn_run = Gtk.Template.Child()
    
    def __init__(self, app: dict):
        super().__init__()
        self.__app = app
        self.__build_ui()
    
    def __build_ui(self):
        self.set_title(self.__app["Name"])
        self.set_subtitle(self.__app["Container"])
        
        self.btn_run.connect("clicked", self.__on_btn_run_clicked)
        self.connect("program-exited", self.__on_program_exited)

    def __on_btn_run_clicked(self, widget: Gtk.Widget):
        self.btn_run.set_sensitive(False)
        self.emit("run-requested", self.__app["Name"])

    def __on_program_exited(self, widget, apxname: str):
        self.btn_run.set_sensitive(True)
