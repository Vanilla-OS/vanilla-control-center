# main.py
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

import sys
import logging
import subprocess
import gi
import gettext
from os import path
import locale

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import VanillaWindow


logging.basicConfig(level=logging.INFO)

# region Translations
'''
This code snippet searches for and uploads translations to different 
directories, depending on your production or development environment. 
The function _() can be used to create and retrieve translations.
'''
share_dir = path.join(sys.prefix, 'share')
base_dir = '.'

if getattr(sys, 'frozen', False):
    base_dir = path.dirname(sys.executable)
    share_dir = path.join(base_dir, 'share')
elif sys.argv[0]:
    exec_dir = path.dirname(path.realpath(sys.argv[0]))
    base_dir = path.dirname(exec_dir)
    share_dir = path.join(base_dir, 'share')

    if not path.exists(share_dir):
        share_dir = base_dir

locale_dir = path.join(share_dir, 'locale')

if not path.exists(locale_dir):  # development
    locale_dir = path.join(base_dir, 'build', 'mo')

locale.bindtextdomain("vanilla-control-center", locale_dir)
locale.textdomain("vanilla-control-center")
gettext.bindtextdomain("vanilla-control-center", locale_dir)
gettext.textdomain("vanilla-control-center")
_ = gettext.gettext


# endregion


class VanillaControlCenterApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='org.vanillaos.ControlCenter',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.create_action('quit', self.quit, ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('help', self.help, ['F1'])

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = VanillaWindow(application=self)
        win.present()

    def on_about_action(self, widget, *args):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name=_('Vanilla OS Control Center'),
                                application_icon='org.vanillaos.ControlCenter',
                                developer_name='Mirko Brombin',
                                version='1.7.1',
                                copyright='Copyright © 2023 Mirko Brombin and Contributors',
                                website='https://vanillaos.org/',
                                issue_url=('https://github.com/Vanilla-OS/vanilla-control-center/issues'),
                                license_type=('gpl-3-0-only'))
        about.add_credit_section(
            _("Code by"),
            [
                "Mirko Brombin https://mirko.pm"
            ]
        )
        about.add_credit_section(
            _("Documentation by"),
            [
                "K.B.Dharun Krishna <kbdharunkrishna@gmail.com>",
                "Bart Gravendeel <monstertux@proton.me>",
            ]
        )
        about.add_credit_section(
            _("Contributors"),
            [
                "kramo https://github.com/kra-mo",
                "Muqtadir https://github.com/Muqtxdir",
                "Hari Rana (TheEvilSkeleton) https://theevilskeleton.gitlab.io",
            ]
        )
        about.add_credit_section(
            _("Translators"),
            [
                "0xMRTT https://github.com/0xMRTT",
                "Ali Paredes https://github.com/alinpr18",
                "Rafael Fontenelle https://github.com/rffontenelle",
                "MikeStavr https://github.com/MikeStavr",
                "rOxANDtOl https://github.com/r0xANDt0l",
                "kramo https://github.com/kra-mo",
                "Krzysztof https://github.com/kangurek-kao",
                "Ahmet Onder Mogol https://github.com/aomogol",
                "Alessandro Zangrandi https://github.com/AlexzanDev",
                "jorg76440 https://github.com/jorg76440",
                "leolost2605 https://github.com/leolost2605",
                "rizqiwoii https://github.com/rizqiwoii",
                "Serhii Chebanenko https://github.com/4e6anenk0",
                "Viktor https://github.com/p1xelll",
                "CJ/LinuxGamer https://github.com/LinuxGamer",
                "Hannor Smith https://github.com/Hannor-Smith",
                "K.B.Dharun Krishna https://github.com/kbdharun",
                "Al Capitan https://github.com/alcapitan",
                "v0id86 https://github.com/v0id86",
                "stpnwf https://github.com/stpnwf",
                "Sven https://github.com/SKBotNL",
                "bittin https://github.com/bittin",
                "sherichev https://github.com/sherichev",
                "Fábio/fabiogvdneto https://github.com/fabiogvdneto",
                "Raphaël Denni https://github.com/SlyEyes",
                "Deniz Akşimşek https://github.com/dz4k",
                "bobarakatx https://github.com/bobarakatx",
                "J. Lavoie https://hosted.weblate.org/user/Edanas",
                "Jehu Marcos Herrera Puentes https://github.com/JMarcosHP",
                "Reidho Satria https://github.com/elliottophellia",
                "JungHee Lee https://github.com/MarongHappy",
                "Pedro Costa https://github.com/pedrocosta",
                "Nguyễn Phú Trọng https://hosted.weblate.org/user/NguynPhTrng",
                "Olawenah/adriabrucortes https://github.com/adriabrucortes",
                "othmahammedi https://github.com/othmahammedi",
                "Luccas Ferreira https://hosted.weblate.org/user/Mertubeluiz",
                "una-mura https://github.com/una-mura",
                "deinen.finny https://github.com/finnmonstar",
                "Rodrigo Pedro https://github.com/rodrigo-pedro",
                "Veysel Erden https://github.com/veyselerden",
                "mmouzo https://github.com/mmouzo",
                "phlostically https://hosted.weblate.org/user/phlostically/",
                "Ryo Nakano https://github.com/ryonakano",
                "Cealica https://github.com/Cealica",
                "Chris <wolrekids@gmail.com>",
                "Martin Meizoso https://github.com/martinmei71",
                "Neeraj55#5 https://github.com/thakurfazer55",
                "stathious https://hosted.weblate.org/user/stathious/",
                "Michal Maděra https://github.com/czM1K3",
                "Mr.Narsus https://github.com/MrNarsus",
                "Kakujeetoz https://github.com/Kakujeetoz",
                "Henrique Picanço https://github.com/henriquepicanco",
                "Óscar Fernández Díaz https://github.com/oscfdezdz",
                "Nagy Ádám https://github.com/NagyAdamA",
                "Philip Goto https://github.com/flipflop97",
                "Roman Vassilchenko https://github.com/RomanVassilchenko",
                "Mohammad saliq https://github.com/darsaliq00",
                "Leo https://github.com/gnesterif",
                "Imam Faraz Aditya https://github.com/imfaditya",
                "yukidream https://github.com/sekalengrengginang",
                "Ghost/duch3201 https://github.com/duch3201",
                "Hugo Carvalho https://github.com/hugok79",
                "Emin KÖSE <kansaslicocuk@gmail.com>",
                "Kira Roubin https://github.com/jplie",
                "Samuel NAIT https://github.com/Tisamu",
                "Muhammed Bayraktar https://github.com/Xelorium",
                "imgradeone https://github.com/imgradeone",
                "sakydogalo https://github.com/sakydogalo",
                "EncryptedEasty https://github.com/EncryptedEasty",
                "PPNplus https://hosted.weblate.org/user/ppnplus",
                "gallegonovato https://github.com/gallegonovato",
                "czenon1 https://github.com/czenon1",
                "Raka Prasetya Pratama https://github.com/MizuNotCool",
                "Park Seonu https://github.com/Sannoob3144",
                "lakejason0 https://github.com/lakejason0",
                "Kefir2105 https://github.com/Kefir2105",
                "Eryk Michalak https://github.com/gnu-ewm",
                "allubie https://github.com/allubie",
                "David Lapshin https://github.com/daudix-UFO",
                "Akros <akrostv2@gmail.com>",
                "Jasenko https://github.com/jsnko",
                "Pistak22 https://github.com/Pistak22",
                "Andrey Sobolev <andrey.g.sobolev@gmail.com>",
                "BaerLKR https://github.com/BaerLKR",
                "Tiefseetauchner https://github.com/Tiefseetauchner",
                "azuki https://github.com/azu0609",
                "Diego Novaes https://github.com/dlnovaes"
            ]
        )
        about.present()
    
    def help(self, widget, callback=None):
        subprocess.Popen(["yelp", "help:vanilla-control-center"], start_new_session=True)

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = VanillaControlCenterApplication()
    return app.run(sys.argv)
