# dialog_update_check.py
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

import subprocess
from gi.repository import Gtk, Gio, Gdk, GLib, Adw, Vte, Pango

from vanilla_control_center.run_async import RunAsync


@Gtk.Template(resource_path='/org/vanillaos/ControlCenter/gtk/dialog-update-check.ui')
class VanillaDialogUpdateCheck(Adw.Window):
    __gtype_name__ = 'VanillaDialogUpdateCheck'

    status_check = Gtk.Template.Child()
    status_confirm = Gtk.Template.Child()
    status_no_updates = Gtk.Template.Child()
    status_installing = Gtk.Template.Child()
    status_complete = Gtk.Template.Child()
    status_failed = Gtk.Template.Child()
    group_updates = Gtk.Template.Child()
    console_box = Gtk.Template.Child()
    console_output = Gtk.Template.Child()
    btn_apply_updates = Gtk.Template.Child()
    btn_no_updates_close = Gtk.Template.Child()
    btn_updates_restart = Gtk.Template.Child()
    btn_complete_close = Gtk.Template.Child()
    btn_failed_close = Gtk.Template.Child()
    progress_check = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.set_transient_for(window)
        self.__window = window
        self.__terminal = Vte.Terminal()
        self.__font = Pango.FontDescription()
        self.__font.set_family("Ubuntu Mono")
        self.__font.set_size(13 * Pango.SCALE)
        self.__font.set_weight(Pango.Weight.NORMAL)
        self.__font.set_stretch(Pango.Stretch.NORMAL)

        self.__build_ui()

    def __build_ui(self):
        self.__terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.ON)
        self.__terminal.set_font(self.__font)
        self.__terminal.set_mouse_autohide(True)

        self.console_output.append(self.__terminal)

        self.__terminal.connect("child-exited", self.on_vte_child_exited)
        self.btn_apply_updates.connect("clicked", self.__on_apply_updates)
        self.btn_no_updates_close.connect("clicked", self.__close)
        self.btn_updates_restart.connect("clicked", self.__restart)
        self.btn_complete_close.connect("clicked", self.__close)
        self.btn_failed_close.connect("clicked", self.__close)

        palette = ["#353535", "#c01c28", "#26a269", "#a2734c", "#12488b", "#a347ba", "#2aa1b3", "#cfcfcf", "#5d5d5d", "#f66151", "#33d17a", "#e9ad0c", "#2a7bde", "#c061cb", "#33c7de", "#ffffff"]
        
        FOREGROUND = palette[0]
        BACKGROUND = palette[15]
        FOREGROUND_DARK = palette[15]
        BACKGROUND_DARK = palette[0]
        
        self.fg = Gdk.RGBA()
        self.bg = Gdk.RGBA()

        self.colors = [Gdk.RGBA() for c in palette]
        [color.parse(s) for (color, s) in zip(self.colors, palette)]
        desktop_schema = Gio.Settings.new('org.gnome.desktop.interface')
        if desktop_schema.get_enum('color-scheme') == 0:
            self.fg.parse(FOREGROUND)
            self.bg.parse(BACKGROUND)
        elif desktop_schema.get_enum('color-scheme') == 1:
            self.fg.parse(FOREGROUND_DARK)
            self.bg.parse(BACKGROUND_DARK)
        self.__terminal.set_colors(self.fg, self.bg, self.colors)

        self.__check_updates()

    def __run_command(self, command):
        self.status_confirm.set_visible(False)
        self.status_installing.set_visible(True)
        self.__terminal.spawn_async(
            Vte.PtyFlags.DEFAULT,
            None,
            ["/bin/sh", "-c", command],
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
            -1,
            None,
            None,
            None,
        )

    def __pulse(self):
        self.progress_check.pulse()
        GObject.timeout_add(100, self.__pulse)

    def __check_updates(self):
        def callback(result, *args):
            status, updates = result
            self.status_check.set_visible(False)

            if status:
                self.status_confirm.set_visible(True)

                for update in updates:
                    _entry = Adw.ActionRow()
                    _entry.set_title(update["name"])
                    _entry.set_subtitle(update["version"])
                    self.group_updates.add(_entry)
                return

            self.status_no_updates.set_visible(True)

        RunAsync(self.__window.vso.get_updates, callback)

    def __on_apply_updates(self, button):
        self.__run_command(self.__window.vso.update_command)

    def on_vte_child_exited(self, terminal, status, *args):
        status = not bool(status)

        if status:
            self.status_complete.set_visible(True)
            self.status_installing.set_visible(False)
            return

        self.status_failed.set_visible(True)
        self.status_installing.set_visible(False)

    def __close(self, button):
        self.destroy()

    def __restart(self, button):
        subprocess.run(['gnome-session-quit', '--reboot'])
