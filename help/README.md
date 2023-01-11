# Help page - Instructions

## Writing Help Pages

- New help pages must be added to the `C` directory (with `.page` file extension), added to `index.page`.
- It must contain details of the author writing it.
- All images must be named in a proper convension and added to the `C/media` subdirectory. And the added image must be marked as a non-translatable string.
- All help pages and media must be added to the `meson.build` file.
- Generate a POT file using the command in the section below and update all po files using `msgmerge <locale>.po <name>.pot --update` or a graphical translation software such as Poedit.
- Before proposing the changes, remove the POT file.

## Localization

### POT File

The translation pot file can be generated using the [itstool](https://itstool.org/) command:

`itstool -o vanilla-control-center-help.pot  C/index.page C/drivers-install.page C/drivers-not-available.page C/update-check.page C/update-scheduling.page C/update-smart.page C/subsystem-containers.page C/subsystem-installed.page C/prime-profiles.page C/legal.xml`

(Add your new pages to the above command, update it in README too)

### Adding a New Language

- Verify if your language is listed in <https://www.gnu.org/software/gettext/manual/html_node/Usual-Language-Codes.html>.
- Create a POT file using `itstool`.
- Create a PO file in a separate directory with the correct locale. (i.e es/es.po)
- Remove the POT file before committing the changes.
