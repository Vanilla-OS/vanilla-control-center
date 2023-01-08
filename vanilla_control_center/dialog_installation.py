# dialog_installation.py
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

from gi.repository import Gtk, Gio, Gdk, GLib, Adw, Vte, Pango


@Gtk.Template(resource_path='/org/vanillaos/ControlCenter/gtk/dialog-installation.ui')
class VanillaDialogInstallation(Adw.Window):
    __gtype_name__ = 'VanillaDialogInstallation'

    status = Gtk.Template.Child()
    console_output = Gtk.Template.Child()

    def __init__(self, title, window, command, callback, **kwargs):
        super().__init__(**kwargs)
        self.set_transient_for(window)
        self.status.set_title(title)
        self.__window = window
        self.__command = command
        self.__callback = callback
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

        self.__terminal.spawn_async(
            Vte.PtyFlags.DEFAULT,
            None,
            ["/bin/sh", "-c", self.__command],
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
        self.progressbar.pulse()
        GObject.timeout_add(100, self.__pulse)

    def on_vte_child_exited(self, terminal, status, *args):
        status = not bool(status)
        self.__callback(status)
