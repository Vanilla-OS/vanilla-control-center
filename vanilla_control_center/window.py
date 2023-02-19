# window.py
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
import subprocess
from gi.repository import Adw
from gi.repository import Gtk, GLib, GObject
from gettext import gettext as _

from vanilla_control_center.program import VanillaApxProgram
from vanilla_control_center.container import VanillaApxContainer
from vanilla_control_center.backends.apx import Apx
from vanilla_control_center.backends.vso import Vso
from vanilla_control_center.dialog_installation import VanillaDialogInstallation
from vanilla_control_center.run_async import RunAsync


logger = logging.getLogger("Vanilla")


@Gtk.Template(resource_path='/org/vanillaos/ControlCenter/gtk/window.ui')
class VanillaWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'VanillaWindow'
    __gsignals__ = {
        "installation-finished": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    status_updates = Gtk.Template.Child()
    btn_apply = Gtk.Template.Child()
    toasts = Gtk.Template.Child()
    row_update_status = Gtk.Template.Child()
    combo_update_schedule = Gtk.Template.Child()
    str_update_schedule = Gtk.Template.Child()
    switch_update_smart = Gtk.Template.Child()
    switch_update_auto = Gtk.Template.Child()
    page_apx = Gtk.Template.Child()
    group_containers = Gtk.Template.Child()
    group_apps = Gtk.Template.Child()
    row_update_auto = Gtk.Template.Child()

    __selected_drivers = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__selected_default = None
        self.vso = Vso()
        self.apx = Apx()
        self.__build_ui()

    def __build_ui(self):
        self.__setup_vso()
        self.__setup_apx()
    
    # region Vso
    def __setup_vso(self):
        if latest_check := self.vso.get_latest_check_beautified():
            self.row_update_status.set_subtitle(latest_check)

        if scheduling := self.vso.scheduling:
            state = 1
            if scheduling == "weekly":
                state = 0
            elif scheduling == "monthly":
                state = 1
            self.combo_update_schedule.set_selected(state)

        if smart := self.vso.smart:
            self.switch_update_smart.set_active(smart)
        
        if auto := self.vso.auto:
            self.switch_update_auto.set_active(auto)

        self.combo_update_schedule.connect("notify::selected", self.__on_update_schedule_changed)
        self.switch_update_smart.connect("state-set", self.__on_update_smart_changed)
        self.switch_update_auto.connect("state-set", self.__on_update_auto_changed)
        
    def __on_update_smart_changed(self, widget, state, *args):
        res = self.vso.set_smartupdate(state)
        if res:
            self.toast(_("Smart Update Changed."))
        else:
            self.toast(_("Failed to change the Smart Update setting."))

    def __on_update_auto_changed(self, widget, state, *args):
        res = self.vso.set_autoupdate(state)
        if res:
            self.toast(_("Automatic Update setting changed."))
        else:
            self.toast(_("Failed to change Automatic Update setting"))

    def __on_update_schedule_changed(self, widget, *args):
        new_state = widget.get_selected()
        old_state = 0 if new_state == 1 else 1

        if self.vso.set_scheduling(new_state):
            self.toast(_("Update Schedule Changed."))
            return
            
    # endregion

    # region Apx
    def __setup_apx(self):
        if not self.apx.supported:
            self.page_apx.set_visible(False)
            return
            
        for container in self.apx.containers:
            _row = VanillaApxContainer(self, container)
            self.group_containers.add(_row)
            
        for app in self.apx.apps:
            _row = VanillaApxProgram(app)
            _row.connect("run-requested", self.__on_apx_run_requested)
            self.group_apps.add(_row)
    
    def __on_apx_run_requested(self, widget, name):
        def run_async():
            return self.apx.run(name)

        def callback(result, *args):
            widget.emit("program-exited", name)

            if result in [None, False]:
                self.toast(_("{} Exited With Error.").format(name))
                return

            self.toast(_("{} Exited.").format(name))

        RunAsync(run_async, callback)
        self.toast(_("{} Launched.").format(name))
    # endregion
    
    def toast(self, message, timeout=2):
        toast = Adw.Toast.new(message)
        toast.props.timeout = timeout
        self.toasts.add_toast(toast)
