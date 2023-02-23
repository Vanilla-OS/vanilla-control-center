<div align="center">
    <img src="data/icons/hicolor/scalable/apps/org.vanillaos.ControlCenter.svg" height="64">
    <h1>Vanilla OS Control Center</h1>
    <p>This utility is meant to be used in <a href="https://github.com/vanilla-os">Vanilla OS</a> 
    to manage its components (ABroot, VSO, Apx) and drivers via ubuntu-drivers-common.</p>
    <hr />
    <a href="https://hosted.weblate.org/engage/vanilla-os/">
<img src="https://hosted.weblate.org/widgets/vanilla-os/-/installer/svg-badge.svg" alt="Stato traduzione" />
</a>
    <br />
    <img src="data/screenshot.png">
</div>


## Build
### Dependencies
- build-essential
- meson
- libadwaita-1-dev
- gettext
- desktop-file-utils

### Build
```bash
meson build
ninja -C build
```

### Install
```bash
sudo ninja -C build install
```

## Run
```bash
vanilla-control-center
```
