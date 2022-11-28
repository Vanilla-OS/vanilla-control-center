# window.py
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

import logging
import subprocess
from gi.repository import Adw
from gi.repository import Gtk, GLib, GObject

from .driver import VanillaDriverRow, VanillaDriversGroup
from .program import VanillaApxProgram
from .ubuntu_drivers import UbuntuDrivers
from .apx import Apx
from .vso import Vso
from .dialog_installation import VanillaDialogInstallation
from .run_async import RunAsync


logger = logging.getLogger("Vanilla")


@Gtk.Template(resource_path='/org/vanillaos/ControlCenter/gtk/window.ui')
class VanillaWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'VanillaWindow'
    __gsignals__ = {
        "installation-finished": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    page_drivers = Gtk.Template.Child()
    status_drivers = Gtk.Template.Child()
    status_no_drivers = Gtk.Template.Child()
    status_no_apx = Gtk.Template.Child()
    btn_apply = Gtk.Template.Child()
    toasts = Gtk.Template.Child()
    status_updates = Gtk.Template.Child()
    row_update_status = Gtk.Template.Child()
    combo_update_schedule = Gtk.Template.Child()
    str_update_schedule = Gtk.Template.Child()
    page_apx = Gtk.Template.Child()
    group_apps = Gtk.Template.Child()
    __selected_drivers = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__selected_default = None
        self.ubuntu_drivers = UbuntuDrivers()
        self.vso = Vso()
        self.apx = Apx()
        self.__build_ui()

    def __build_ui(self):
        self.__setup_devices()
        self.__setup_vso()
        self.__setup_apx()
    
    # region Devices
    def __setup_devices(self):
        def run_async():
            result = []
            for vendor in self.ubuntu_drivers.get_devices():
                result.append(VanillaDriversGroup(
                        vendor["vendor"], 
                        vendor["model"], 
                        vendor["drivers"]))

            return result

        def callback(result, *args):
            if result is None:
                self.status_no_drivers.set_visible(True)
                self.status_drivers.set_visible(False)
                return

            self.btn_apply.connect("clicked", self.__on_apply_clicked)

            for item in result:
                item.connect("installation-needed", self.__on_installation_needed)
                self.page_drivers.add(item)

            self.status_drivers.set_visible(False)
            self.page_drivers.set_visible(True)

        RunAsync(run_async, callback)
    
    def __on_installation_needed(self, widget, model, driver):
        logging.info("Installation requested: {}".format(driver))
        self.__selected_drivers[model] = driver
        self.btn_apply.set_visible(len(self.__selected_drivers) > 0)

    def __on_apply_clicked(self, widget):
        if not self.ubuntu_drivers.can_install():
            self.toast(_("Another transaction is running or the system needs to be restarted."))
            return

        def async_task():
            res = []
            for model in self.__selected_drivers:
                res.append(self.ubuntu_drivers.install(self.__selected_drivers[model]))

            if False in res:
                return res, False

        def callback(result, error=False):
            if error:
                self.toast(_("Installation Failed."))
                return

            self.emit("installation-finished", self.__selected_drivers)
            self.__selected_drivers = {}
            self.toast(_("New Drivers Installed."))
            logger.info("Installation finished.")
            subprocess.run(['gnome-session-quit', '--reboot'])

        self.btn_apply.set_visible(False)
        VanillaDialogInstallation(self).show()
        RunAsync(async_task, callback)
    # endregion

    # region Vso
    def __setup_vso(self):
        if latest_check := self.vso.get_latest_check_beautified():
            self.row_update_status.set_subtitle(latest_check)

        self.combo_update_schedule.connect("notify::selected", self.__on_update_schedule_changed)

        if scheduling := self.vso.get_scheduling():
            state = 1
            if scheduling == "weekly":
                state = 0
            elif scheduling == "monthly":
                state = 1
            self.set_selected_with_no_trigger(self.combo_update_schedule, self.__on_update_schedule_changed, state)

    def __on_update_schedule_changed(self, widget, *args):
        self.vso.set_scheduling(widget.get_selected())
        self.toast(_("Update Schedule Changed."))

    # endregion

    # region Apx
    def __setup_apx(self):
        if not self.apx.supported:
            self.page_apx.set_visible(False)
            return

        if len(self.apx.apps) == 0:
            self.group_apps.set_visible(False)
            self.status_no_apx.set_visible(True)
            return
            
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
    
    def set_state_with_no_trigger(self, widget, signal_func, state):
        widget.handler_block_by_func(signal_func)
        widget.set_active(state)
        widget.handler_unblock_by_func(signal_func)

    def set_selected_with_no_trigger(self, widget, signal_func, state):
        widget.handler_block_by_func(signal_func)
        widget.set_selected(state)
        widget.handler_unblock_by_func(signal_func)
