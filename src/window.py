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
from .ubuntu_drivers import UbuntuDrivers
from .almost import Almost
from .apx import Apx
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
    btn_apply = Gtk.Template.Child()
    toasts = Gtk.Template.Child()
    status_almost = Gtk.Template.Child()
    switch_almost_status = Gtk.Template.Child()
    switch_almost_reboot = Gtk.Template.Child()
    combo_almost_default = Gtk.Template.Child()
    str_almost_defaults = Gtk.Template.Child()
    page_almost = Gtk.Template.Child()
    page_apx = Gtk.Template.Child()
    group_apps = Gtk.Template.Child()
    __selected_drivers = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__selected_default = None
        self.ubuntu_drivers = UbuntuDrivers()
        self.almost = Almost()
        self.apx = Apx()
        self.__build_ui()

    def __build_ui(self):
        self.__setup_devices()
        self.__setup_almost()
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
                self.status_drivers.set_icon_name("dialog-error-symbolic")
                self.status_drivers.set_title("No Drivers Found.")
                self.status_drivers.set_description("No drivers found for your devices or an error occurred.")
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
        def async_task():
            res = []
            for model in self.__selected_drivers:
                res.append(self.ubuntu_drivers.install(self.__selected_drivers[model]))

            if False in res:
                return res, False

        def callback(result, error=False):
            if error:
                self.toast("Installation Failed.")
                return

            self.emit("installation-finished", self.__selected_drivers)
            self.__selected_drivers = {}
            self.toast("New Drivers Installed.")
            logger.info("Installation finished.")
            subprocess.run(['gnome-session-quit', '--reboot'])

        self.btn_apply.set_visible(False)
        VanillaDialogInstallation(self).show()
        RunAsync(async_task, callback)
    # endregion

    # region Almost
    def __setup_almost(self):
        if not self.almost.supported:
            self.page_almost.set_visible(False)
            return
        
        self.__selected_default = self.almost.params.get("default", 0)

        self.switch_almost_status.set_active(self.almost.params.get("current", True))
        self.switch_almost_reboot.set_active(self.almost.params.get("persistent", True))
        self.combo_almost_default.set_selected(self.__selected_default)

        self.switch_almost_status.connect("state-set", self.__on_almost_status_changed)
        self.switch_almost_reboot.connect("state-set", self.__on_almost_reboot_changed)
        self.combo_almost_default.connect("notify::selected", self.__on_almost_default_changed)

    def __on_almost_status_changed(self, widget, state):
        def run_async():
            return self.almost.set_current(state)

        def callback(result, *args):
            widget.set_sensitive(True)
            if result in [None, False]:
                self.toast("Failed to Set Immutability Status.")
                self.set_state_with_no_trigger(
                    widget, self.__on_almost_status_changed, not state)
                return

            self.toast("Immutability Enabled." if state else "Immutability Disabled.",)

        widget.set_sensitive(False)
        RunAsync(run_async, callback)

    def __on_almost_reboot_changed(self, widget, state):
        def run_async():
            return self.almost.set_persistent(state)

        def callback(result, *args):
            widget.set_sensitive(True)
            if result in [None, False]:
                self.toast("Failed to Set Persistent Mode.")
                self.set_state_with_no_trigger(
                    widget, self.__on_almost_reboot_changed, not state)
                return

            self.toast("Persistent Mode Enabled." if state else "Persistent Mode Disabled.",)

        widget.set_sensitive(False)
        RunAsync(run_async, callback)

    def __on_almost_default_changed(self, widget, state):
        def run_async():
            return self.almost.set_default(widget.get_selected())
            
        def callback(result, *args):
            widget.set_sensitive(True)
            if result in [None, False]:
                self.toast("Failed to Set Default Mode.")
                self.set_selected_with_no_trigger(
                    widget, self.__on_almost_default_changed, self.__selected_default)
                return
                
            self.__selected_default = widget.get_selected()
            self.toast("Default Mode Changed to {}.".format("Read-Only" if widget.get_selected() == 0 else "Read-Write"))

        widget.set_sensitive(False)
        RunAsync(run_async, callback)
    # endregion

    # region Apx
    def __setup_apx(self):
        if not self.apx.supported:
            self.page_apx.set_visible(False)
            return

        for app in self.apx.get_apps():
            _name, _exec = app
            _row = Adw.ActionRow()
            _row.set_title(_name)
            self.group_apps.add(_row)
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
