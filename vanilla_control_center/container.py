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
from gi.repository import Gtk, GLib, GObject
from gettext import gettext as _

logger = logging.getLogger("Vanilla:Container")


@Gtk.Template(resource_path='/org/vanillaos/ControlCenter/gtk/container.ui')
class VanillaApxContainer(Adw.ActionRow):
    __gtype_name__ = "VanillaApxContainer"
    btn_shell = Gtk.Template.Child()
    btn_init = Gtk.Template.Child()
    
    def __init__(self, window: Gtk.Widget, container: dict):
        super().__init__()
        self.__window = window
        self.__container = container
        self.__build_ui()
    
    def __build_ui(self):
        self.set_title(self.__container["Name"])
        self.set_subtitle(self.__container["Alias"])

        self.btn_init.set_visible(not self.__container["Status"] == 0)
        self.btn_shell.set_visible(self.__container["Status"] == 0)
        
        self.btn_shell.connect(_("Clicked"), self.__on_btn_shell_clicked)
        self.btn_init.connect(_("Clicked"), self.__on_btn_init_clicked)
        
    def __on_btn_shell_clicked(self, widget):
        GLib.spawn_command_line_async(self.__container["ShellCmd"])
        self.__window.toast(_("Shell opened for container '{}'").format(self.__container["Name"]))

    def __on_btn_init_clicked(self, widget):
        res = GLib.spawn_command_line_async(self.__container["InitCmd"])
        if res:
            self.btn_init.set_visible(False)
            self.btn_shell.set_visible(True)
            self.__window.toast(_("Container '{}' initialized").format(self.__container["Name"]))
        